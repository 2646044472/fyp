#!/usr/bin/env python3
"""Freeze PRF-TR target payloads and merge independent target verification."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REGISTRY_FIELDS = ("payload_id", "expected_payload", "oracle_payload", "target_verified")
ORACLE_FIELDS = {"payload_id", "oracle_payload"}


def read_payloads(path: Path) -> list[str]:
    payloads = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    payloads = [payload for payload in payloads if payload]
    if not payloads:
        raise ValueError("payload file has no non-empty payloads")
    if len(payloads) != len(set(payloads)):
        raise ValueError("payload file contains duplicate payloads")
    return payloads


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def create_registry(out: Path, payloads_path: Path, id_prefix: str) -> None:
    if out.exists():
        raise ValueError(f"refusing to overwrite existing registry: {out}")
    if not id_prefix.strip():
        raise ValueError("id prefix must not be empty")
    payloads = read_payloads(payloads_path)
    rows = [
        {
            "payload_id": f"{id_prefix}{index:03d}",
            "expected_payload": payload,
            "oracle_payload": "",
            "target_verified": "",
        }
        for index, payload in enumerate(payloads, start=1)
    ]
    write_rows(out, rows)


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = set(REGISTRY_FIELDS) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"registry missing columns: {', '.join(sorted(missing))}")
        rows = [
            {field: (row.get(field) or "").strip() for field in REGISTRY_FIELDS}
            for row in reader
        ]
    if not rows:
        raise ValueError("registry has no targets")
    ids = [row["payload_id"] for row in rows]
    if not all(ids) or len(ids) != len(set(ids)):
        raise ValueError("registry payload_id values must be non-empty and unique")
    if any(not row["expected_payload"] for row in rows):
        raise ValueError("registry expected_payload values must be non-empty")
    return rows


def read_oracles(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = ORACLE_FIELDS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"oracle results missing columns: {', '.join(sorted(missing))}")
        pairs = [
            ((row.get("payload_id") or "").strip(), (row.get("oracle_payload") or "").strip())
            for row in reader
        ]
    if not pairs or any(not payload_id for payload_id, _ in pairs):
        raise ValueError("oracle results require non-empty payload_id values")
    ids = [payload_id for payload_id, _ in pairs]
    if len(ids) != len(set(ids)):
        raise ValueError("oracle results contain duplicate payload_id values")
    return dict(pairs)


def verify_registry(registry_path: Path, oracle_path: Path, out: Path) -> None:
    if out.exists():
        raise ValueError(f"refusing to overwrite existing verified registry: {out}")
    rows = read_registry(registry_path)
    oracle_by_id = read_oracles(oracle_path)
    registry_ids = {row["payload_id"] for row in rows}
    missing = registry_ids - set(oracle_by_id)
    extras = set(oracle_by_id) - registry_ids
    if missing or extras:
        details = []
        if missing:
            details.append(f"missing oracle IDs: {', '.join(sorted(missing))}")
        if extras:
            details.append(f"unknown oracle IDs: {', '.join(sorted(extras))}")
        raise ValueError("; ".join(details))
    for row in rows:
        row["oracle_payload"] = oracle_by_id[row["payload_id"]]
        row["target_verified"] = str(
            row["oracle_payload"] == row["expected_payload"]
        ).lower()
    write_rows(out, rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze PRF-TR payloads and record independent target verification."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create", help="Create a new unverified target registry.")
    create.add_argument("--out", type=Path, required=True, help="New TSV registry path.")
    create.add_argument(
        "--payloads", type=Path, required=True, help="UTF-8 text file with one payload per line."
    )
    create.add_argument(
        "--id-prefix", default="target-", help="Payload ID prefix (default: target-)."
    )

    verify = commands.add_parser("verify", help="Merge independent oracle scans into a registry.")
    verify.add_argument("--registry", type=Path, required=True, help="Frozen registry TSV.")
    verify.add_argument(
        "--oracle-results", type=Path, required=True, help="TSV with payload_id and oracle_payload."
    )
    verify.add_argument("--out", type=Path, required=True, help="New verified registry TSV.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "create":
            create_registry(args.out, args.payloads, args.id_prefix)
        else:
            verify_registry(args.registry, args.oracle_results, args.out)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
