"""Compare two recognition runs on one fixed plan; emit aggregate counts only.

Run `python paired_outcomes.py --self-test` without any image, model, or deps.
For an authorized local JSON file: `python paired_outcomes.py --input /LOCAL/plan.json`.
Input is a nonempty array of rows:
  {"probe":"local-key", "enrolled":true, "a":{"rank":"correct","decision":"accept"},
   "b":{"rank":"wrong","decision":"reject"}}
Use null for a missing result, "unscored" for a failed/missing rank or decision,
and require "unscored" rank for an unenrolled probe. Inputs and their identifiers
stay local. This compares outcome tables, not raw features, calibration, or rates.
"""
import argparse
from collections import Counter
import json
from pathlib import Path


def outcome(enrolled, arm):
    if arm is None:
        return "unscored", "unscored"
    if not isinstance(arm, dict) or set(arm) != {"rank", "decision"}:
        raise ValueError("invalid arm schema")
    rank, decision = arm["rank"], arm["decision"]
    if rank not in ("correct", "wrong", "unscored") or decision not in (
        "accept", "reject", "unscored"
    ):
        raise ValueError("invalid outcome")
    if not enrolled and rank != "unscored":
        raise ValueError("unenrolled probes cannot have a known-hand rank")
    if enrolled and rank == "unscored" and decision != "unscored":
        raise ValueError("an unavailable known-hand score has no decision")
    return rank, decision


def aggregate(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("expected nonempty plan array")
    seen, arms, paired = set(), {"a": Counter(), "b": Counter()}, Counter()
    enrolled_total = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"probe", "enrolled", "a", "b"}:
            raise ValueError("invalid planned-probe schema")
        key, enrolled = row["probe"], row["enrolled"]
        if not isinstance(key, str) or not key or key in seen or type(enrolled) is not bool:
            raise ValueError("invalid or duplicate planned probe")
        seen.add(key)
        enrolled_total += enrolled
        ranks = {}
        for label in ("a", "b"):
            rank, decision = outcome(enrolled, row[label])
            c = arms[label]
            ranks[label] = rank == "correct"
            c["planned"] += 1
            if enrolled:
                c["known_rank_" + rank] += 1
                if decision == "accept":
                    c["known_accept_" + rank] += 1
                else:
                    c["known_" + decision] += 1
            else:
                c["unknown_" + decision] += 1
        if enrolled:
            paired["both_correct" if all(ranks.values()) else
                   "a_only_correct" if ranks["a"] else
                   "b_only_correct" if ranks["b"] else "neither_correct"] += 1
    return {"planned": len(rows), "known": enrolled_total,
            "unknown": len(rows) - enrolled_total, "arms": arms,
            "paired_known_rank": paired}


def self_test():
    def arm(rank, decision):
        return {"rank": rank, "decision": decision}

    rows = [
        dict(probe="invented-1", enrolled=True, a=arm("correct", "reject"), b=None),
        dict(probe="invented-2", enrolled=True, a=arm("wrong", "accept"), b=arm("correct", "accept")),
        dict(probe="invented-3", enrolled=False, a=None, b=arm("unscored", "reject")),
        dict(probe="invented-4", enrolled=False, a=arm("unscored", "accept"), b=None),
    ]
    result = aggregate(rows)
    assert result["planned"] == 4 and result["known"] == result["unknown"] == 2
    assert result["paired_known_rank"] == {"a_only_correct": 1, "b_only_correct": 1}
    assert result["arms"]["a"]["known_rank_correct"] == 1
    assert result["arms"]["a"]["known_accept_correct"] == 0
    assert result["arms"]["a"]["known_accept_wrong"] == 1
    assert result["arms"]["a"]["unknown_unscored"] == result["arms"]["a"]["unknown_accept"] == 1
    assert result["arms"]["b"]["unknown_reject"] == 1
    assert "invented-" not in json.dumps(result)
    for invalid in (rows + rows[:1], [dict(rows[2], a=arm("correct", "accept"))]):
        try:
            aggregate(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid plan was accepted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--input", type=Path, help="authorized local outcome plan only")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("Synthetic paired-outcome checks passed.")
        return
    try:
        result = aggregate(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError, RecursionError):
        parser.exit(2, "Could not read or validate the local outcome plan.\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
