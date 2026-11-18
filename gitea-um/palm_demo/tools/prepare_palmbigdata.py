#!/usr/bin/env python3
"""Extract a small, auditable PalmBigDataBase development subset from its zip."""

from __future__ import annotations

import argparse
import csv
import re
import zipfile
from pathlib import Path


NAME_RE = re.compile(r"^PalmBigDataBase/P_F_(\d+)_(\d+)\.bmp$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).parents[2] / "data" / "PalmBigDataBase.zip")
    parser.add_argument("--output", type=Path, default=Path(__file__).parents[1] / "data" / "processed" / "palmbigdata-dev")
    parser.add_argument("--identities", type=int, default=20)
    parser.add_argument("--samples-per-identity", type=int, default=10)
    parser.add_argument(
        "--confirm-authorized-dataset",
        action="store_true",
        help="Confirm that the archive provider and original dataset terms allow this local processing",
    )
    args = parser.parse_args()
    if args.identities < 2 or args.samples_per_identity < 2:
        parser.error("need at least two identities and two samples per identity")
    if not args.source.is_file():
        parser.error(f"source archive not found: {args.source}")
    if not args.confirm_authorized_dataset:
        parser.error("confirm data permission with --confirm-authorized-dataset before extraction")

    selected: dict[int, list[tuple[int, str]]] = {}
    with zipfile.ZipFile(args.source) as archive:
        for name in archive.namelist():
            match = NAME_RE.match(name)
            if match:
                person, sample = map(int, match.groups())
                selected.setdefault(person, []).append((sample, name))
        usable = [(person, sorted(items)) for person, items in sorted(selected.items()) if len(items) >= args.samples_per_identity]
        usable = usable[: args.identities]
        if len(usable) < args.identities:
            parser.error(f"archive only has {len(usable)} eligible identities")
        args.output.mkdir(parents=True, exist_ok=True)
        manifest_rows: list[dict[str, str]] = []
        for person, items in usable:
            target_dir = args.output / f"P_F_{person:03d}"
            target_dir.mkdir(exist_ok=True)
            for sample, name in items[: args.samples_per_identity]:
                destination = target_dir / Path(name).name
                with archive.open(name) as source, destination.open("wb") as target:
                    target.write(source.read())
                manifest_rows.append({"identity": str(person), "sample": str(sample), "file": str(destination.relative_to(args.output)), "archive_member": name})

    with (args.output / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["identity", "sample", "file", "archive_member"])
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"Prepared {len(manifest_rows)} images from {len(usable)} identities in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
