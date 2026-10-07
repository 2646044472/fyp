from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "prf_tr_plan.py"


class PrfTrPlanTest(unittest.TestCase):
    def run_plan(self, output: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--out",
                str(output),
                "--sessions",
                "s01,s02",
                "--cells",
                "clean,low,cover,held",
                "--held-out-cell",
                "held",
                "--actions",
                "visible_noir_only,fixed_visible_then_ir",
                "--attempts",
                "2",
                "--seed",
                "17",
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_plan_is_complete_and_marks_holdout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "plan.tsv"
            result = self.run_plan(output)
            self.assertEqual(result.returncode, 0, result.stderr)

            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))

            self.assertEqual(len(rows), 2 * 4 * 2 * 2)
            self.assertEqual({row["run_order"] for row in rows}, {str(i) for i in range(1, 33)})
            self.assertTrue(all(row["split"] == "held_out" for row in rows if row["physical_cell"] == "held"))
            self.assertTrue(all(row["split"] == "source" for row in rows if row["physical_cell"] != "held"))
            self.assertEqual(len({row["episode_id"] for row in rows}), len(rows))
            bundle_ids_by_attempt = {}
            for row in rows:
                key = (row["session_id"], row["physical_cell"], row["attempt_index"])
                bundle_ids_by_attempt.setdefault(key, set()).add(row["bundle_id"])
            self.assertTrue(all(len(ids) == 1 for ids in bundle_ids_by_attempt.values()))

    def test_rejects_invalid_holdout_and_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "plan.tsv"
            invalid = self.run_plan(output, "--held-out-cell", "missing")
            self.assertEqual(invalid.returncode, 2)
            self.assertFalse(output.exists())

            valid = self.run_plan(output)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            existing = self.run_plan(output)
            self.assertEqual(existing.returncode, 2)

    def test_default_plan_does_not_schedule_optional_ir_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "plan.tsv"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--out",
                    str(output),
                    "--sessions",
                    "s01",
                    "--cells",
                    "clean,held",
                    "--held-out-cell",
                    "held",
                    "--attempts",
                    "1",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="", encoding="utf-8") as handle:
                actions = {row["action"] for row in csv.DictReader(handle, delimiter="\t")}

            self.assertEqual(
                actions,
                {"visible_noir_only", "scalar_gate", "random_action", "always_review"},
            )


if __name__ == "__main__":
    unittest.main()
