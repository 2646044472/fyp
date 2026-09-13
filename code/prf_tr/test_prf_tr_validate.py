from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "prf_tr_plan.py"
VALIDATE = ROOT / "prf_tr_validate.py"


class PrfTrValidateTest(unittest.TestCase):
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
                "1",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def write_registry(self, path: Path) -> None:
        path.write_text(
            "payload_id\texpected_payload\toracle_payload\ttarget_verified\n"
            "target-001\tPAYLOAD\tPAYLOAD\ttrue\n",
            encoding="utf-8",
        )

    def write_episodes(self, plan: Path, path: Path, bad_bundle: bool = False) -> None:
        with plan.open(newline="", encoding="utf-8") as handle:
            plan_rows = list(csv.DictReader(handle, delimiter="\t"))
        lines = [
            "session_id\tattempt_id\tpayload_id\tphysical_cell\tbundle_id\taction\ttarget_verified",
        ]
        for index, row in enumerate(plan_rows):
            bundle_id = "wrong" if bad_bundle and index == 0 else row["bundle_id"]
            lines.append(
                "\t".join(
                    (
                        row["session_id"],
                        row["attempt_id"],
                        "target-001",
                        row["physical_cell"],
                        bundle_id,
                        row["action"],
                        "true",
                    )
                )
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATE), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_validates_complete_plan_and_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            plan = root / "plan.tsv"
            registry = root / "registry.tsv"
            episodes = root / "episodes.tsv"
            output = root / "validation.tsv"
            self.create_plan(plan)
            self.write_registry(registry)
            self.write_episodes(plan, episodes)

            result = self.run_validator(
                "--plan", str(plan), "--registry", str(registry),
                "--episodes", str(episodes), "--out", str(output), "--require-complete",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="", encoding="utf-8") as handle:
                rows = {row["split"]: row for row in csv.DictReader(handle, delimiter="\t")}
            self.assertEqual(rows["source"]["missing_plan_count"], "0")
            self.assertEqual(rows["held_out"]["observed_episode_count"], "2")

    def test_rejects_bundle_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            plan = root / "plan.tsv"
            registry = root / "registry.tsv"
            episodes = root / "episodes.tsv"
            output = root / "validation.tsv"
            self.create_plan(plan)
            self.write_registry(registry)
            self.write_episodes(plan, episodes, bad_bundle=True)

            result = self.run_validator(
                "--plan", str(plan), "--registry", str(registry),
                "--episodes", str(episodes), "--out", str(output),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("bundle_id differs", result.stderr)


if __name__ == "__main__":
    unittest.main()
