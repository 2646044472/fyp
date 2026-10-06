"""Run the Effectual crop with repaired finger-valley location selection."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import run_effectual_roi_tongji as effectual  # noqa: E402

effectual.OUT_DIR = ROOT / "results" / "effectual_palm_roi_fixed"
effectual.main(repair_location=True)
