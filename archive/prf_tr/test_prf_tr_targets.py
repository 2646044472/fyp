from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "prf_tr_targets.py"


class PrfTrTargetsTest(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_create_and_verify_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            payloads = root / "payloads.txt"
            registry = root / "registry.tsv"
            oracle_results = root / "oracle.tsv"
            verified = root / "verified.tsv"
            payloads.write_text("PRF-001\nPRF-002\n", encoding="utf-8")

            created = self.run_tool(
                "create", "--out", str(registry), "--payloads", str(payloads)
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            oracle_results.write_text(
                "payload_id\toracle_payload\n"
                "target-001\tPRF-001\n"
                "target-002\tWRONG\n",
                encoding="utf-8",
            )
            verified_result = self.run_tool(
                "verify",
                "--registry",
                str(registry),
                "--oracle-results",
                str(oracle_results),
                "--out",
                str(verified),
            )
            self.assertEqual(verified_result.returncode, 0, verified_result.stderr)
            with verified.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))

            self.assertEqual(rows[0]["target_verified"], "true")
            self.assertEqual(rows[1]["target_verified"], "false")

    def test_rejects_duplicate_payload_and_incomplete_oracle_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            payloads = root / "payloads.txt"
            registry = root / "registry.tsv"
            payloads.write_text("DUP\nDUP\n", encoding="utf-8")
            duplicate = self.run_tool(
                "create", "--out", str(registry), "--payloads", str(payloads)
            )
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn("duplicate payloads", duplicate.stderr)

            payloads.write_text("ONE\nTWO\n", encoding="utf-8")
            created = self.run_tool(
                "create", "--out", str(registry), "--payloads", str(payloads)
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            oracle_results = root / "oracle.tsv"
            verified = root / "verified.tsv"
            oracle_results.write_text(
                "payload_id\toracle_payload\n"
                "target-001\tONE\n",
                encoding="utf-8",
            )
            incomplete = self.run_tool(
                "verify",
                "--registry",
                str(registry),
                "--oracle-results",
                str(oracle_results),
                "--out",
                str(verified),
            )
            self.assertEqual(incomplete.returncode, 2)
            self.assertIn("missing oracle IDs", incomplete.stderr)


if __name__ == "__main__":
    unittest.main()
