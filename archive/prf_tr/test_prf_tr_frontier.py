from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "prf_tr_frontier.py"


HEADER = (
    "session_id\tbundle_id\tphysical_cell\taction\tfinal_decision\taction_sequence\tfirst_capture_id\tsecond_capture_id\tfinal_capture_id\ttarget_verified\tdecoded_exact\t"
    "reacquisition_count\ttotal_latency_ms\tbytes_written\tenergy_mj\n"
)


class PrfTrFrontierTest(unittest.TestCase):
    def test_marks_dominated_action_and_keeps_tradeoff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text(
                HEADER
                + "s01\tb01\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf01\t\tf01\ttrue\tfalse\t0\t10\t100\t1\n"
                + "s02\tb01\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf01\t\tf01\ttrue\tfalse\t0\t10\t100\t1\n"
                + "s01\tb01\tcover\ttwo_shot\treview\tfixed_visible_then_ir\tf01\tf02\tf02\ttrue\ttrue\t1\t20\t200\t2\n"
                + "s02\tb01\tcover\ttwo_shot\treview\tfixed_visible_then_ir\tf01\tf02\tf02\ttrue\ttrue\t1\t20\t200\t2\n"
                + "s01\tb01\tcover\tbad\tretain\tbad_reacquire\tf01\tf02\tf02\ttrue\tfalse\t1\t30\t300\t3\n"
                + "s02\tb01\tcover\tbad\tretain\tbad_reacquire\tf01\tf02\tf02\ttrue\tfalse\t1\t30\t300\t3\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="", encoding="utf-8") as handle:
                rows = {row["action"]: row for row in csv.DictReader(handle, delimiter="\t")}

            self.assertEqual(rows["bad"]["pareto_non_dominated"], "false")
            self.assertEqual(rows["bad"]["dominated_by"], "visible_noir_only")
            self.assertEqual(rows["visible_noir_only"]["pareto_non_dominated"], "true")
            self.assertEqual(rows["two_shot"]["pareto_non_dominated"], "true")

    def test_rejects_missing_required_column(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text("session_id\tphysical_cell\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing required TSV columns", result.stderr)

    def test_weights_sessions_equally_when_attempt_counts_differ(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text(
                HEADER
                + "".join(
                    f"s01\tb{index:03d}\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf{index:03d}\t\tf{index:03d}\ttrue\tfalse\t0\t10\t100\t1\n"
                    for index in range(1, 101)
                )
                + "s02\tb01\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf01\t\tf01\ttrue\ttrue\t0\t10\t100\t1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="", encoding="utf-8") as handle:
                row = next(csv.DictReader(handle, delimiter="\t"))

            self.assertEqual(row["episode_count"], "101")
            self.assertEqual(row["session_count"], "2")
            self.assertEqual(row["false_retain_rate"], "0.500000")

    def test_rejects_misaligned_or_duplicate_policy_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text(
                HEADER
                + "s01\tb01\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf01\t\tf01\ttrue\ttrue\t0\t10\t100\t1\n"
                + "s01\tb02\tcover\tscalar_gate\treview\tscalar_gate\tf02\tf03\tf03\ttrue\ttrue\t1\t20\t200\t2\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("same bundle IDs", result.stderr)

            episodes.write_text(
                HEADER
                + "s01\tb01\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf01\t\tf01\ttrue\ttrue\t0\t10\t100\t1\n"
                + "s01\tb01\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf01\t\tf01\ttrue\ttrue\t0\t10\t100\t1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate bundle", result.stderr)

    def test_rejects_unverified_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text(
                HEADER
                + "s01\tb01\tcover\tvisible_noir_only\tretain\tvisible_noir_only\tf01\t\tf01\tfalse\ttrue\t0\t10\t100\t1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("target_verified must be true", result.stderr)

    def test_rejects_reacquisition_without_distinct_second_frame(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text(
                HEADER
                + "s01\tb01\tcover\tscalar_gate\tretain\tscalar_gate_reacquire\tf01\tf01\tf01\ttrue\ttrue\t1\t10\t100\t1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("distinct second_capture_id", result.stderr)

    def test_rejects_reacquire_as_a_terminal_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text(
                HEADER
                + "s01\tb01\tcover\tscalar_gate\treacquire\tscalar_gate_reacquire\tf01\tf02\tf02\ttrue\ttrue\t1\t10\t100\t1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("final_decision must be retain/review/unknown", result.stderr)

    def test_rejects_final_capture_that_does_not_follow_reacquisition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            episodes = root / "episodes.tsv"
            output = root / "frontier.tsv"
            episodes.write_text(
                HEADER
                + "s01\tb01\tcover\tscalar_gate\tretain\tscalar_gate_reacquire\tf01\tf02\tf01\ttrue\ttrue\t1\t10\t100\t1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("final_capture_id must equal second_capture_id", result.stderr)


if __name__ == "__main__":
    unittest.main()
