#!/usr/bin/env python3
"""Score a planned local gallery and query set; emit aggregate Rank-1 counts only.

The JSON plan has exactly schema (1), gallery, and queries. Every row has
sample, hand, and feature_row. Sample keys must be distinct across both roles.
Gallery hand keys are nonempty strings; query hand=null denotes a planned
unknown hand. A null feature_row means extraction did not produce an embedding.
Each feature archive contains only features.npy: a real N×D floating matrix.
The plan links to zero-based rows, each used once within its role. Byte-distinct
samples and disjoint identities must be established by the caller's protocol;
these files only establish the declared roles and distinct sample keys.

Cosine normalizes features; dot preserves magnitude. A hand's score is the
maximum over eligible gallery samples, with exact top ties counted separately.
Fixed-five requires exactly five planned rows for each enrolled hand and withholds
that hand if any of its five features is unavailable. Available uses every valid
feature of a hand with at least one. Missing, zero, and nonfinite vectors do not
score. These are rank/coverage counts, not camera/model inference or acceptance.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from zipfile import BadZipFile, ZipFile
from zlib import error as ZlibError

import numpy as np


MAX_PLAN_BYTES = 32 << 20
MAX_FEATURE_BYTES = 256 << 20
SCORE_BLOCK_CELLS = 1_000_000


class InputError(ValueError):
    """Fixed diagnostic text without private paths or sample keys."""


@dataclass(frozen=True)
class Entry:
    sample: str
    hand: str | None
    feature_row: int | None


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("duplicate JSON key")
        result[key] = value
    return result


def read_plan(path):
    try:
        with Path(path).open("rb") as source:
            raw = source.read(MAX_PLAN_BYTES + 1)
        if len(raw) > MAX_PLAN_BYTES:
            raise InputError("plan exceeds the size limit")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_json_object)
    except InputError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        raise InputError("could not read the local JSON plan") from error


def read_features(path):
    # Validate the ZIP member list and uncompressed size before NumPy allocates.
    try:
        with Path(path).open("rb") as source:
            with ZipFile(source) as archive:
                members = archive.infolist()
                if (len(members) != 1 or members[0].filename != "features.npy"
                        or not 0 < members[0].file_size <= MAX_FEATURE_BYTES):
                    raise InputError("feature archive must contain one supported features.npy member")
                # Read the header from the ZIP stream before allocating the array.
                # NumPy does not pickle for floating arrays and allow_pickle=False
                # prevents object records from loading even if a header is forged.
                with archive.open(members[0]) as data:
                    version = np.lib.format.read_magic(data)
                    readers = {(1, 0): np.lib.format.read_array_header_1_0,
                               (2, 0): np.lib.format.read_array_header_2_0}
                    if version not in readers:
                        raise InputError("unsupported feature array header")
                    shape, _fortran, dtype = readers[version](data)
                    if (len(shape) != 2 or shape[0] < 0 or shape[1] <= 0
                            or dtype.kind != "f" or dtype.itemsize > 8
                            or shape[0] * shape[1] * dtype.itemsize != members[0].file_size - data.tell()):
                        raise InputError("feature array must be a supported floating matrix")
            source.seek(0)
            with np.load(source, allow_pickle=False) as data:
                return data["features"]
    except InputError:
        raise
    except (OSError, BadZipFile, EOFError, KeyError, RuntimeError, ValueError, ZlibError) as error:
        raise InputError("could not read the local feature archive") from error


def validate_plan(plan, gallery_count, query_count):
    if (not isinstance(plan, dict) or set(plan) != {"schema", "gallery", "queries"}
            or type(plan["schema"]) is not int or plan["schema"] != 1):
        raise InputError("invalid plan schema")
    seen = set()
    groups = []
    for name, feature_count in (("gallery", gallery_count), ("queries", query_count)):
        rows = plan[name]
        if not isinstance(rows, list) or (name == "queries" and not rows):
            raise InputError("invalid gallery or query list")
        seen_rows, entries = set(), []
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"sample", "hand", "feature_row"}:
                raise InputError("invalid plan row schema")
            sample, hand, feature_row = row["sample"], row["hand"], row["feature_row"]
            if not isinstance(sample, str) or not sample or sample in seen:
                raise InputError("empty or duplicate sample key")
            if (hand is not None or name == "gallery") and (not isinstance(hand, str) or not hand):
                raise InputError("invalid hand key")
            if feature_row is not None:
                if (type(feature_row) is not int or not 0 <= feature_row < feature_count
                        or feature_row in seen_rows):
                    raise InputError("invalid or duplicate feature row")
                seen_rows.add(feature_row)
            seen.add(sample)
            entries.append(Entry(sample, hand, feature_row))
        if len(seen_rows) != feature_count:
            raise InputError("feature rows must match the declared plan exactly")
        groups.append(entries)
    return groups


def prepare_vectors(values, route):
    vectors = np.asarray(values)
    if vectors.ndim != 2 or vectors.shape[1] <= 0 or vectors.dtype.kind != "f" or vectors.dtype.itemsize > 8:
        raise InputError("feature array must be a supported floating matrix")
    vectors = vectors.astype(np.float64, copy=False)
    scale = np.max(np.abs(vectors), axis=1)
    valid = (scale > 0) & np.isfinite(vectors).all(axis=1)
    if route == "cosine":
        vectors = np.zeros_like(vectors)
        scaled = values[valid].astype(np.float64) / scale[valid, None]
        vectors[valid] = scaled / np.linalg.norm(scaled, axis=1)[:, None]
    return vectors, valid


def usable(entry, valid):
    return entry.feature_row is not None and bool(valid[entry.feature_row])


def evaluate(plan, gallery_features, query_features, *, route, gallery_policy):
    if route not in {"cosine", "dot"} or gallery_policy not in {"fixed-five", "available"}:
        raise InputError("unknown scoring route or gallery policy")
    gallery_vectors, gallery_valid = prepare_vectors(gallery_features, route)
    query_vectors, query_valid = prepare_vectors(query_features, route)
    if gallery_vectors.shape[1] != query_vectors.shape[1]:
        raise InputError("feature dimensions differ between roles")
    gallery, queries = validate_plan(plan, len(gallery_vectors), len(query_vectors))

    planned_per_hand = Counter(row.hand for row in gallery)
    if gallery_policy == "fixed-five" and any(n != 5 for n in planned_per_hand.values()):
        raise InputError("fixed-five requires five planned gallery rows per hand")
    by_hand = {hand: [] for hand in planned_per_hand}
    for row in gallery:
        if usable(row, gallery_valid):
            by_hand[row.hand].append(row.feature_row)
    eligible = {hand: rows for hand, rows in by_hand.items()
                if rows and (gallery_policy == "available" or len(rows) == 5)}
    positions = {hand: i for i, hand in enumerate(eligible)}
    flat = [idx for rows in eligible.values() for idx in rows]
    starts = np.cumsum([0, *(len(rows) for rows in eligible.values())], dtype=np.intp)[:-1]

    counts = {
        "known": Counter(dict.fromkeys(("rank1_correct", "rank1_wrong", "top_score_tie",
                                        "query_feature_unavailable", "true_gallery_unavailable",
                                        "nonfinite_score"), 0)),
        "unknown": Counter(dict.fromkeys(("scored", "top_score_tie", "query_feature_unavailable",
                                          "gallery_unavailable", "nonfinite_score"), 0)),
    }
    pending = []
    for row in queries:
        group = "unknown" if row.hand is None else "known"
        if not usable(row, query_valid):
            counts[group]["query_feature_unavailable"] += 1
        elif group == "known" and row.hand not in eligible:
            counts[group]["true_gallery_unavailable"] += 1
        elif not flat:
            counts[group]["gallery_unavailable"] += 1
        else:
            pending.append((group, row))

    if pending:
        gallery_matrix = gallery_vectors[flat]
        batch_size = max(1, SCORE_BLOCK_CELLS // len(flat))
        for i in range(0, len(pending), batch_size):
            block = pending[i:i + batch_size]
            input_rows = [row.feature_row for _, row in block]
            with np.errstate(over="ignore", invalid="ignore"):
                scores = query_vectors[input_rows] @ gallery_matrix.T
            for (group, row), sample_scores in zip(block, scores):
                if not np.isfinite(sample_scores).all():
                    counts[group]["nonfinite_score"] += 1
                    continue
                hand_scores = np.maximum.reduceat(sample_scores, starts)
                top = hand_scores.max()
                if np.count_nonzero(hand_scores == top) != 1:
                    counts[group]["top_score_tie"] += 1
                elif group == "unknown":
                    counts[group]["scored"] += 1
                else:
                    outcome = "rank1_correct" if hand_scores[positions[row.hand]] == top else "rank1_wrong"
                    counts[group][outcome] += 1

    known, unknown = counts["known"], counts["unknown"]
    known_planned, unknown_planned = sum(known.values()), sum(unknown.values())
    return {
        "schema": 1,
        "route": route,
        "gallery_policy": gallery_policy,
        "gallery": {"planned_samples": len(gallery), "usable_samples": sum(map(len, by_hand.values())),
                    "scored_samples": len(flat), "planned_hands": len(by_hand), "scored_hands": len(eligible)},
        "queries": {"planned": len(queries), "known_planned": known_planned, "unknown_planned": unknown_planned,
                    "known": dict(known), "unknown": dict(unknown),
                    "rank1_over_planned_known": known["rank1_correct"] / known_planned if known_planned else None},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", required=True, type=Path, help="private local JSON manifest")
    parser.add_argument("--gallery-features", required=True, type=Path, help="private local gallery .npz")
    parser.add_argument("--query-features", required=True, type=Path, help="private local query .npz")
    parser.add_argument("--route", choices=("cosine", "dot"), required=True)
    parser.add_argument("--gallery-policy", choices=("fixed-five", "available"), required=True)
    args = parser.parse_args(argv)
    try:
        result = evaluate(read_plan(args.plan), read_features(args.gallery_features),
                          read_features(args.query_features), route=args.route, gallery_policy=args.gallery_policy)
    except InputError as error:
        print(f"Invalid local ranking input: {error}.", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
