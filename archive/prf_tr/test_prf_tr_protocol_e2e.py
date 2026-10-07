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
VALIDATE = ROOT / "prf_tr_validate.py"
FRONTIER = ROOT / "prf_tr_frontier.py"


class PrfTrProtocolE2ETest(unittest.TestCase):
    def run_tool(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_frozen_plan_to_frontier_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            plan = root / "plan.tsv"
            registry = root / "registry.tsv"
            bundles = root / "bundles.tsv"
            details = root / "episode-details.tsv"
            provenance = root / "provenance.tsv"
            decisions = root / "decision-episodes.tsv"
            frontier = root / "frontier.tsv"

            registry.write_text(
                "payload_id\texpected_payload\toracle_payload\ttarget_verified\n"
                "target-001\tONE\tONE\ttrue\n"
                "target-002\tTWO\tTWO\ttrue\n",
                encoding="utf-8",
            )
            plan_result = self.run_tool(
                PLAN,
                "--out",
                str(plan),
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
                "--seed",
                "5",
            )
            self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
            bundles_result = self.run_tool(
                BUNDLES,
                "--plan",
                str(plan),
                "--registry",
                str(registry),
                "--out",
                str(bundles),
                "--seed",
                "7",
            )
            self.assertEqual(bundles_result.returncode, 0, bundles_result.stderr)

            with plan.open(newline="", encoding="utf-8") as handle:
                plan_rows = list(csv.DictReader(handle, delimiter="\t"))
            with bundles.open(newline="", encoding="utf-8") as handle:
                bundle_rows = {
                    row["bundle_id"]: row for row in csv.DictReader(handle, delimiter="\t")
                }

            details.write_text(
                "session_id\tattempt_id\tpayload_id\tphysical_cell\tbundle_id\taction\ttarget_verified\n"
                + "".join(
                    "\t".join(
                        (
                            row["session_id"],
                            row["attempt_id"],
                            bundle_rows[row["bundle_id"]]["payload_id"],
                            row["physical_cell"],
                            row["bundle_id"],
                            row["action"],
                            "true",
                        )
                    )
                    + "\n"
                    for row in plan_rows
                ),
                encoding="utf-8",
            )
            validation_result = self.run_tool(
                VALIDATE,
                "--plan",
                str(plan),
                "--registry",
                str(registry),
                "--episodes",
                str(details),
                "--out",
                str(provenance),
                "--require-complete",
            )
            self.assertEqual(validation_result.returncode, 0, validation_result.stderr)

            decision_header = (
                "session_id\tbundle_id\tphysical_cell\taction\tfinal_decision\taction_sequence\t"
                "first_capture_id\tsecond_capture_id\tfinal_capture_id\ttarget_verified\tdecoded_exact\t"
                "reacquisition_count\ttotal_latency_ms\tbytes_written\tenergy_mj\n"
            )
            decision_rows = []
            for row in plan_rows:
                bundle = bundle_rows[row["bundle_id"]]
                first_capture_id = bundle["capture_slot_1_id"]
                if row["action"] == "visible_noir_only":
                    decision_rows.append(
                        "\t".join(
                            (
                                row["session_id"],
                                row["bundle_id"],
                                row["physical_cell"],
                                row["action"],
                                "retain",
                                "visible_noir_only",
                                first_capture_id,
                                "",
                                first_capture_id,
                                "true",
                                "true",
                                "0",
                                "10",
                                "100",
                                "1",
                            )
                        )
                    )
                else:
                    decision_rows.append(
                        "\t".join(
                            (
                                row["session_id"],
                                row["bundle_id"],
                                row["physical_cell"],
                                row["action"],
                                "review",
                                "scalar_gate",
                                first_capture_id,
                                "",
                                first_capture_id,
                                "true",
                                "true",
                                "0",
                                "20",
                                "100",
                                "1",
                            )
                        )
                    )
            decisions.write_text(
                decision_header + "\n".join(decision_rows) + "\n", encoding="utf-8"
            )
            frontier_result = self.run_tool(
                FRONTIER, "--episodes", str(decisions), "--out", str(frontier)
            )
            self.assertEqual(frontier_result.returncode, 0, frontier_result.stderr)
            with frontier.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))

            self.assertEqual(len(rows), 4)
            self.assertTrue(
                all(
                    row["pareto_non_dominated"] == "true"
                    for row in rows
                    if row["action"] == "visible_noir_only"
                )
            )
            self.assertTrue(
                all(
                    row["pareto_non_dominated"] == "false"
                    for row in rows
                    if row["action"] == "scalar_gate"
                )
            )


if __name__ == "__main__":
    unittest.main()
