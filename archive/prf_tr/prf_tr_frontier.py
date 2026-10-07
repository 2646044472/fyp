#!/usr/bin/env python3
"""Summarize PRF-TR decision episodes and mark per-cell Pareto frontiers."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FIELDS = {
    "session_id",
    "bundle_id",
    "physical_cell",
    "action",
    "final_decision",
    "action_sequence",
    "first_capture_id",
    "second_capture_id",
    "final_capture_id",
    "target_verified",
    "decoded_exact",
    "reacquisition_count",
    "total_latency_ms",
    "bytes_written",
}


@dataclass(frozen=True)
class Episode:
    session_id: str
    bundle_id: str
    physical_cell: str
    action: str
    final_decision: str
    decoded_exact: bool
    reacquisition_count: float
    total_latency_ms: float
    bytes_written: float
    energy_mj: float | None


@dataclass(frozen=True)
class Summary:
    physical_cell: str
    action: str
    episode_count: int
    session_count: int
    false_retain_rate: float
    review_rate: float
    mean_reacquisition_count: float
    mean_latency_ms: float
    mean_bytes_written: float
    mean_energy_mj: float | None

    def metric_vector(self, include_energy: bool) -> tuple[float, ...]:
        values = (
            self.false_retain_rate,
            self.review_rate,
            self.mean_reacquisition_count,
            self.mean_latency_ms,
            self.mean_bytes_written,
        )
        if include_energy:
            assert self.mean_energy_mj is not None
            return values + (self.mean_energy_mj,)
        return values


def parse_bool(value: str, field: str, row_number: int) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"row {row_number}: {field} must be true/false")


def parse_nonnegative(value: str, field: str, row_number: int) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise ValueError(f"row {row_number}: {field} must be numeric") from error
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError(f"row {row_number}: {field} must be finite and non-negative")
    return parsed


def load_episodes(path: Path) -> list[Episode]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = REQUIRED_FIELDS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"missing required TSV columns: {', '.join(sorted(missing))}")

        episodes: list[Episode] = []
        for row_number, row in enumerate(reader, start=2):
            for field in (
                "session_id",
                "bundle_id",
                "physical_cell",
                "action",
                "final_decision",
                "action_sequence",
                "first_capture_id",
                "final_capture_id",
            ):
                if not row[field].strip():
                    raise ValueError(f"row {row_number}: {field} must not be empty")
            decision = row["final_decision"].strip().lower()
            if decision not in {"retain", "review", "unknown"}:
                raise ValueError(
                    f"row {row_number}: final_decision must be retain/review/unknown"
                )
            reacquisition_count = parse_nonnegative(
                row["reacquisition_count"], "reacquisition_count", row_number
            )
            first_capture_id = row["first_capture_id"].strip()
            second_capture_id = row["second_capture_id"].strip()
            final_capture_id = row["final_capture_id"].strip()
            if reacquisition_count > 1:
                raise ValueError(
                    f"row {row_number}: only zero or one reacquisition is supported"
                )
            if reacquisition_count > 0 and (
                not second_capture_id or second_capture_id == first_capture_id
            ):
                raise ValueError(
                    f"row {row_number}: a reacquisition requires a distinct second_capture_id"
                )
            if reacquisition_count == 0 and final_capture_id != first_capture_id:
                raise ValueError(
                    f"row {row_number}: without reacquisition final_capture_id must equal first_capture_id"
                )
            if reacquisition_count == 1 and final_capture_id != second_capture_id:
                raise ValueError(
                    f"row {row_number}: after reacquisition final_capture_id must equal second_capture_id"
                )

            raw_energy = (row.get("energy_mj") or "").strip()
            energy_mj = (
                parse_nonnegative(raw_energy, "energy_mj", row_number) if raw_energy else None
            )
            target_verified = parse_bool(
                row["target_verified"], "target_verified", row_number
            )
            if not target_verified:
                raise ValueError(
                    f"row {row_number}: target_verified must be true for analysis"
                )
            episodes.append(
                Episode(
                    session_id=row["session_id"].strip(),
                    bundle_id=row["bundle_id"].strip(),
                    physical_cell=row["physical_cell"].strip(),
                    action=row["action"].strip(),
                    final_decision=decision,
                    decoded_exact=parse_bool(row["decoded_exact"], "decoded_exact", row_number),
                    reacquisition_count=reacquisition_count,
                    total_latency_ms=parse_nonnegative(
                        row["total_latency_ms"], "total_latency_ms", row_number
                    ),
                    bytes_written=parse_nonnegative(
                        row["bytes_written"], "bytes_written", row_number
                    ),
                    energy_mj=energy_mj,
                )
            )
    if not episodes:
        raise ValueError("input TSV has no decision episodes")
    validate_bundle_alignment(episodes)
    return episodes


def validate_bundle_alignment(episodes: list[Episode]) -> None:
    """Require fair counterfactual policy replay from frozen capture bundles."""
    seen: set[tuple[str, str, str, str]] = set()
    bundles_by_session_cell: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )

    for episode in episodes:
        duplicate_key = (
            episode.session_id,
            episode.physical_cell,
            episode.action,
            episode.bundle_id,
        )
        if duplicate_key in seen:
            raise ValueError(
                "duplicate bundle for the same session/cell/action: "
                + "/".join(duplicate_key)
            )
        seen.add(duplicate_key)
        bundles_by_session_cell[(episode.session_id, episode.physical_cell)][
            episode.action
        ].add(episode.bundle_id)

    for (session_id, physical_cell), action_bundles in bundles_by_session_cell.items():
        if len(action_bundles) < 2:
            continue
        reference_action, reference_bundles = next(iter(action_bundles.items()))
        for action, bundles in action_bundles.items():
            if bundles != reference_bundles:
                raise ValueError(
                    "actions must use the same bundle IDs within a session/cell: "
                    f"{session_id}/{physical_cell}; {reference_action} versus {action}"
                )


def summarize(episodes: list[Episode]) -> list[Summary]:
    groups: dict[tuple[str, str, str], list[Episode]] = defaultdict(list)
    for episode in episodes:
        groups[(episode.physical_cell, episode.action, episode.session_id)].append(episode)

    by_action: dict[tuple[str, str], list[list[Episode]]] = defaultdict(list)
    for (physical_cell, action, _session_id), group in groups.items():
        by_action[(physical_cell, action)].append(group)

    summaries: list[Summary] = []
    for (physical_cell, action), session_groups in sorted(by_action.items()):
        count = sum(len(group) for group in session_groups)
        false_retain_rates = []
        review_rates = []
        reacquisition_means = []
        latency_means = []
        byte_means = []
        energy_means: list[float] = []
        energy_complete = True

        for group in session_groups:
            group_count = len(group)
            false_retain_rates.append(
                sum(
                    episode.final_decision == "retain" and not episode.decoded_exact
                    for episode in group
                )
                / group_count
            )
            review_rates.append(
                sum(episode.final_decision in {"review", "unknown"} for episode in group)
                / group_count
            )
            reacquisition_means.append(
                sum(episode.reacquisition_count for episode in group) / group_count
            )
            latency_means.append(sum(episode.total_latency_ms for episode in group) / group_count)
            byte_means.append(sum(episode.bytes_written for episode in group) / group_count)
            if any(episode.energy_mj is None for episode in group):
                energy_complete = False
            else:
                energy_means.append(
                    sum(episode.energy_mj for episode in group if episode.energy_mj is not None)
                    / group_count
                )

        summaries.append(
            Summary(
                physical_cell=physical_cell,
                action=action,
                episode_count=count,
                session_count=len(session_groups),
                false_retain_rate=sum(false_retain_rates) / len(false_retain_rates),
                review_rate=sum(review_rates) / len(review_rates),
                mean_reacquisition_count=sum(reacquisition_means) / len(reacquisition_means),
                mean_latency_ms=sum(latency_means) / len(latency_means),
                mean_bytes_written=sum(byte_means) / len(byte_means),
                mean_energy_mj=(sum(energy_means) / len(energy_means) if energy_complete else None),
            )
        )
    return summaries


def dominates(left: Summary, right: Summary, include_energy: bool) -> bool:
    left_vector = left.metric_vector(include_energy)
    right_vector = right.metric_vector(include_energy)
    return all(a <= b for a, b in zip(left_vector, right_vector)) and any(
        a < b for a, b in zip(left_vector, right_vector)
    )


def annotate_frontiers(summaries: list[Summary]) -> list[tuple[Summary, bool, tuple[str, ...]]]:
    by_cell: dict[str, list[Summary]] = defaultdict(list)
    for summary in summaries:
        by_cell[summary.physical_cell].append(summary)

    annotated: list[tuple[Summary, bool, tuple[str, ...]]] = []
    for physical_cell, cell_summaries in sorted(by_cell.items()):
        include_energy = all(summary.mean_energy_mj is not None for summary in cell_summaries)
        for summary in cell_summaries:
            dominators = tuple(
                candidate.action
                for candidate in cell_summaries
                if candidate.action != summary.action and dominates(candidate, summary, include_energy)
            )
            annotated.append((summary, not dominators, dominators))
    return annotated


def write_output(path: Path, annotated: list[tuple[Summary, bool, tuple[str, ...]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = (
        "physical_cell",
        "action",
        "episode_count",
        "session_count",
        "false_retain_rate",
        "review_rate",
        "mean_reacquisition_count",
        "mean_latency_ms",
        "mean_bytes_written",
        "mean_energy_mj",
        "pareto_non_dominated",
        "dominated_by",
    )
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for summary, non_dominated, dominators in annotated:
            writer.writerow(
                {
                    "physical_cell": summary.physical_cell,
                    "action": summary.action,
                    "episode_count": summary.episode_count,
                    "session_count": summary.session_count,
                    "false_retain_rate": f"{summary.false_retain_rate:.6f}",
                    "review_rate": f"{summary.review_rate:.6f}",
                    "mean_reacquisition_count": f"{summary.mean_reacquisition_count:.6f}",
                    "mean_latency_ms": f"{summary.mean_latency_ms:.6f}",
                    "mean_bytes_written": f"{summary.mean_bytes_written:.6f}",
                    "mean_energy_mj": (
                        "" if summary.mean_energy_mj is None else f"{summary.mean_energy_mj:.6f}"
                    ),
                    "pareto_non_dominated": str(non_dominated).lower(),
                    "dominated_by": ",".join(dominators),
                }
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize PRF-TR decision episodes into per-cell Pareto frontiers."
    )
    parser.add_argument("--episodes", type=Path, required=True, help="Decision-episode TSV.")
    parser.add_argument("--out", type=Path, required=True, help="New frontier TSV path.")
    args = parser.parse_args(argv)
    if args.out.exists():
        print(f"ERROR: refusing to overwrite existing output: {args.out}", file=sys.stderr)
        return 2
    try:
        annotated = annotate_frontiers(summarize(load_episodes(args.episodes)))
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    write_output(args.out, annotated)
    print(f"Wrote {len(annotated)} action summaries to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
