#!/usr/bin/env python3
"""Generate a frozen PRF-TR episode schedule before capture begins."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path


DEFAULT_ACTIONS = (
    "visible_noir_only",
    "scalar_gate",
    "random_action",
    "always_review",
)

FIELDNAMES = (
    "run_order",
    "episode_id",
    "bundle_id",
    "session_id",
    "physical_cell",
    "split",
    "action",
    "attempt_index",
    "attempt_id",
)


def split_csv(value: str) -> tuple[str, ...]:
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    if not items:
        raise argparse.ArgumentTypeError("must contain at least one non-empty value")
    if len(items) != len(set(items)):
        raise argparse.ArgumentTypeError("values must be unique")
    return items


def make_rows(
    sessions: tuple[str, ...],
    cells: tuple[str, ...],
    actions: tuple[str, ...],
    attempts: int,
    held_out_cell: str,
    seed: int,
) -> list[dict[str, str | int]]:
    if held_out_cell not in cells:
        raise ValueError("held-out cell must be one of the declared physical cells")
    if attempts < 1:
        raise ValueError("attempts must be positive")

    rows: list[dict[str, str | int]] = []
    for session_id in sessions:
        for physical_cell in cells:
            split = "held_out" if physical_cell == held_out_cell else "source"
            for action in actions:
                for attempt_index in range(1, attempts + 1):
                    bundle_id = "-".join(
                        (session_id, physical_cell, f"b{attempt_index:02d}")
                    )
                    episode_id = "-".join(
                        (session_id, physical_cell, action, f"a{attempt_index:02d}")
                    )
                    rows.append(
                        {
                            "episode_id": episode_id,
                            "bundle_id": bundle_id,
                            "session_id": session_id,
                            "physical_cell": physical_cell,
                            "split": split,
                            "action": action,
                            "attempt_index": attempt_index,
                            "attempt_id": f"a{attempt_index:03d}",
                        }
                    )

    random.Random(seed).shuffle(rows)
    for run_order, row in enumerate(rows, start=1):
        row["run_order"] = run_order
    return rows


def write_plan(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze a PRF-TR episode plan before any physical capture."
    )
    parser.add_argument("--out", type=Path, required=True, help="New TSV plan path.")
    parser.add_argument(
        "--sessions",
        type=split_csv,
        required=True,
        help="Unique session/remount IDs, comma-separated.",
    )
    parser.add_argument(
        "--cells",
        type=split_csv,
        required=True,
        help="Unique preassigned physical-cell IDs, comma-separated.",
    )
    parser.add_argument(
        "--held-out-cell",
        required=True,
        help="One declared physical-cell ID reserved before scoring.",
    )
    parser.add_argument(
        "--actions",
        type=split_csv,
        default=DEFAULT_ACTIONS,
        help="Actions to schedule, comma-separated.",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=20,
        help="Repeated attempts per session/cell/action (default: 20).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260905,
        help="Recorded shuffle seed (default: 20260905).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.out.exists():
        print(f"ERROR: refusing to overwrite existing plan: {args.out}", file=sys.stderr)
        return 2
    try:
        rows = make_rows(
            args.sessions,
            args.cells,
            args.actions,
            args.attempts,
            args.held_out_cell,
            args.seed,
        )
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    write_plan(args.out, rows)
    print(f"Wrote {len(rows)} planned episodes to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
