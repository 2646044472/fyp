from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "prf_tr_plan.py"
BUNDLES = ROOT / "prf_tr_bundles.py"


class PrfTrBundlesTest(unittest.TestCase):
    def create_plan(self, path: Path) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(PLAN),
                "--out",
                str(path),
                "--sessions",
                "s01",
                "--cells",
                "clean,held",
                "--held-out-cell",
                "held",
                "--actions",
                "visible_noir_only,scalar_gate",
                "--attempts",
                "2",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def write_registry(self, path: Path, verified: bool = True) -> None:
        value = "true" if verified else "false"
        path.write_text(
            "payload_id\texpected_payload\toracle_payload\ttarget_verified\n"
            f"target-001\tONE\tONE\t{value}\n"
            f"target-002\tTWO\tTWO\t{value}\n",
            encoding="utf-8",
        )

    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BUNDLES), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_deduplicates_bundles_and_freezes_verified_assignments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            plan = root / "plan.tsv"
            registry = root / "registry.tsv"
            output = root / "bundles.tsv"
            self.create_plan(plan)
            self.write_registry(registry)

            result = self.run_tool(
                "--plan", str(plan), "--registry", str(registry), "--out", str(output), "--seed", "7"
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))

            self.assertEqual(len(rows), 4)
            self.assertEqual(len({row["bundle_id"] for row in rows}), 4)
            self.assertEqual({row["payload_id"] for row in rows}, {"target-001", "target-002"})
            self.assertTrue(all(row["capture_slot_1_id"].endswith("-slot1") for row in rows))
            self.assertTrue(all(row["capture_slot_2_id"].endswith("-slot2") for row in rows))
            self.assertTrue(all(row["assignment_seed"] == "7" for row in rows))

    def test_rejects_unverified_target_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            plan = root / "plan.tsv"
            registry = root / "registry.tsv"
            output = root / "bundles.tsv"
            self.create_plan(plan)
            self.write_registry(registry, verified=False)

            result = self.run_tool(
                "--plan", str(plan), "--registry", str(registry), "--out", str(output)
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("no independently verified targets", result.stderr)


if __name__ == "__main__":
    unittest.main()
