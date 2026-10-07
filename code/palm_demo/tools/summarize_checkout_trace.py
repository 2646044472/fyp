#!/usr/bin/env python3
"""Summarize payment checkout JSONL without inferring biometric accuracy."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


TIMING_FIELDS = ("capture_ms", "roi_ms", "feature_ms", "search_ms", "payment_ms", "total_ms")


def _distribution(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "p50": None, "p95": None}
    ordered = sorted(values)
    def percentile(q: float) -> float:
        index = (len(ordered) - 1) * q
        lower = int(index)
        upper = min(lower + 1, len(ordered) - 1)
        weight = index - lower
        return ordered[lower] * (1 - weight) + ordered[upper] * weight
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "p50": percentile(0.50),
        "p95": percentile(0.95),
    }


def summarize_events(events: Iterable[dict[str, Any]], malformed_lines: int = 0) -> dict[str, Any]:
    rows = list(events)
    timings = {
        field: _distribution([float(row[field]) for row in rows if isinstance(row.get(field), (int, float))])
        for field in TIMING_FIELDS
    }
    return {
        "event": "checkout_trace_summary",
        "total_checkouts": len(rows),
        "malformed_lines": malformed_lines,
        "results": dict(Counter(str(row.get("result", "MISSING")) for row in rows)),
        "roi_status": dict(Counter(str(row.get("roi_status", "MISSING")) for row in rows)),
        "roi_reasons": dict(Counter(str(row.get("roi_reason", "MISSING")) for row in rows)),
        "identification_status": dict(Counter(str(row.get("identification_status", "MISSING")) for row in rows)),
        "capture_sources": dict(Counter(str(row.get("capture_source", "MISSING")) for row in rows)),
        "frame_id_present": sum(row.get("frame_id") is not None for row in rows),
        "timings_ms": timings,
        "warning": "Descriptive trace summary only; no FAR/FRR, causal effect, or payment-security claim.",
    }


def read_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    malformed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if value.get("event") == "checkout":
            events.append(value)
    return events, malformed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="Checkout JSONL log")
    parser.add_argument("--output", type=Path, help="Optional JSON summary path")
    args = parser.parse_args()
    events, malformed = read_events(args.trace)
    summary = summarize_events(events, malformed)
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
