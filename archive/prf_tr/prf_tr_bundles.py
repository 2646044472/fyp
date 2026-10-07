#!/usr/bin/env python3
"""Freeze one verified target assignment for each PRF-TR capture bundle."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

from prf_tr_targets import read_registry


PLAN_FIELDS = {"bundle_id", "session_id", "physical_cell", "split", "attempt_id"}
OUTPUT_FIELDS = (
    "session_id",
    "physical_cell",
    "split",
    "attempt_id",
    "bundle_id",
    "payload_id",
    "capture_slot_1_id",
    "capture_slot_2_id",
    "assignment_seed",
)


def load_plan_bundles(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = PLAN_FIELDS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"plan missing columns: {', '.join(sorted(missing))}")
        rows = [
            {field: (row.get(field) or "").strip() for field in PLAN_FIELDS}
            for row in reader
        ]
    if not rows:
        raise ValueError("plan has no rows")

    bundles: dict[str, dict[str, str]] = {}
    for row in rows:
        if any(not row[field] for field in PLAN_FIELDS):
            raise ValueError("plan rows must not have empty bundle fields")
        bundle_id = row["bundle_id"]
        existing = bundles.get(bundle_id)
        if existing is None:
            bundles[bundle_id] = row
        elif existing != row:
            raise ValueError(f"bundle_id has inconsistent plan metadata: {bundle_id}")
    return sorted(
        bundles.values(),
        key=lambda row: (
            row["session_id"],
            row["physical_cell"],
            row["attempt_id"],
            row["bundle_id"],
        ),
    )


def make_assignments(
    plan_path: Path, registry_path: Path, seed: int
) -> list[dict[str, str]]:
    bundles = load_plan_bundles(plan_path)
    verified_payloads = sorted(
        row["payload_id"]
        for row in read_registry(registry_path)
        if row["target_verified"].lower() == "true"
    )
    if not verified_payloads:
        raise ValueError("registry has no independently verified targets")

    shuffled_payloads = list(verified_payloads)
    random.Random(seed).shuffle(shuffled_payloads)
    assignments: list[dict[str, str]] = []
    for index, bundle in enumerate(bundles):
        bundle_id = bundle["bundle_id"]
        assignments.append(
            {
                "session_id": bundle["session_id"],
                "physical_cell": bundle["physical_cell"],
                "split": bundle["split"],
                "attempt_id": bundle["attempt_id"],
                "bundle_id": bundle_id,
                "payload_id": shuffled_payloads[index % len(shuffled_payloads)],
                "capture_slot_1_id": f"{bundle_id}-slot1",
                "capture_slot_2_id": f"{bundle_id}-slot2",
                "assignment_seed": str(seed),
            }
        )
    return assignments


def write_assignments(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze verified target assignments for deduplicated capture bundles."
    )
    parser.add_argument("--plan", type=Path, required=True, help="Frozen episode plan TSV.")
    parser.add_argument(
        "--registry", type=Path, required=True, help="Independently verified target registry TSV."
    )
    parser.add_argument("--out", type=Path, required=True, help="New capture-bundle TSV.")
    parser.add_argument(
        "--seed", type=int, default=20260905, help="Frozen assignment seed."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.out.exists():
        print(f"ERROR: refusing to overwrite existing output: {args.out}", file=sys.stderr)
        return 2
    try:
        write_assignments(args.out, make_assignments(args.plan, args.registry, args.seed))
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
