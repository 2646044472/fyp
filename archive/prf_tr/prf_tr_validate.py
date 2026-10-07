#!/usr/bin/env python3
"""Validate PRF-TR episode records against the frozen plan and target registry."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

from prf_tr_targets import read_registry


PLAN_FIELDS = {
    "episode_id",
    "bundle_id",
    "session_id",
    "physical_cell",
    "split",
    "action",
    "attempt_id",
}
EPISODE_FIELDS = {
    "session_id",
    "attempt_id",
    "payload_id",
    "physical_cell",
    "bundle_id",
    "action",
    "target_verified",
}


def load_tsv(path: Path, fields: set[str], label: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = fields - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{label} missing columns: {', '.join(sorted(missing))}")
        rows = [
            {field: (row.get(field) or "").strip() for field in fields}
            for row in reader
        ]
    if not rows:
        raise ValueError(f"{label} has no rows")
    return rows


def plan_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row["session_id"],
        row["physical_cell"],
        row["action"],
        row["attempt_id"],
    )


def validate(
    plan_path: Path, registry_path: Path, episodes_path: Path, require_complete: bool
) -> list[dict[str, str]]:
    plan_rows = load_tsv(plan_path, PLAN_FIELDS, "plan")
    plan_by_key: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in plan_rows:
        if any(not row[field] for field in PLAN_FIELDS):
            raise ValueError("plan rows must not contain empty required values")
        key = plan_key(row)
        if key in plan_by_key:
            raise ValueError(f"plan contains duplicate episode key: {key}")
        plan_by_key[key] = row

    registry_rows = read_registry(registry_path)
    verified_payloads = {
        row["payload_id"]
        for row in registry_rows
        if row["target_verified"].lower() == "true"
    }
    if not verified_payloads:
        raise ValueError("registry has no independently verified targets")

    episode_rows = load_tsv(episodes_path, EPISODE_FIELDS, "episodes")
    seen: set[tuple[str, str, str, str]] = set()
    counts: Counter[str] = Counter()
    for row_number, row in enumerate(episode_rows, start=2):
        if any(not row[field] for field in EPISODE_FIELDS):
            raise ValueError(f"episodes row {row_number} has an empty required value")
        if row["target_verified"].lower() != "true":
            raise ValueError(f"episodes row {row_number}: target_verified must be true")
        if row["payload_id"] not in verified_payloads:
            raise ValueError(
                f"episodes row {row_number}: payload_id is not independently verified"
            )
        key = plan_key(row)
        planned = plan_by_key.get(key)
        if planned is None:
            raise ValueError(f"episodes row {row_number}: not present in frozen plan")
        if row["bundle_id"] != planned["bundle_id"]:
            raise ValueError(f"episodes row {row_number}: bundle_id differs from frozen plan")
        if key in seen:
            raise ValueError(f"episodes row {row_number}: duplicate planned episode")
        seen.add(key)
        counts[planned["split"]] += 1

    if require_complete and seen != set(plan_by_key):
        missing = len(set(plan_by_key) - seen)
        raise ValueError(f"episodes are incomplete: {missing} frozen plan rows are missing")

    rows = []
    for split in sorted({row["split"] for row in plan_rows}):
        planned_count = sum(row["split"] == split for row in plan_rows)
        rows.append(
            {
                "split": split,
                "planned_episode_count": str(planned_count),
                "observed_episode_count": str(counts[split]),
                "missing_plan_count": str(planned_count - counts[split]),
            }
        )
    return rows


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "split",
                "planned_episode_count",
                "observed_episode_count",
                "missing_plan_count",
            ),
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate PRF-TR episode provenance before frontier analysis."
    )
    parser.add_argument("--plan", type=Path, required=True, help="Frozen episode-plan TSV.")
    parser.add_argument("--registry", type=Path, required=True, help="Verified target registry TSV.")
    parser.add_argument("--episodes", type=Path, required=True, help="Collected episode TSV.")
    parser.add_argument("--out", type=Path, required=True, help="New validation-summary TSV.")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Reject any missing frozen plan row.",
    )
    args = parser.parse_args(argv)
    if args.out.exists():
        print(f"ERROR: refusing to overwrite existing output: {args.out}", file=sys.stderr)
        return 2
    try:
        rows = validate(args.plan, args.registry, args.episodes, args.require_complete)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    write_summary(args.out, rows)
    print(f"Wrote validation summary to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
