"""Synthetic only: no camera, participant records, weights, or real embeddings."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

import numpy as np

from rank_features import InputError, evaluate, main, read_features


def row(sample, hand, feature_row):
    return {"sample": sample, "hand": hand, "feature_row": feature_row}


def plan(gallery, queries):
    return {"schema": 1, "gallery": gallery, "queries": queries}


class RankFeaturesTests(unittest.TestCase):
    def test_cosine_and_dot_are_distinct_routes(self):
        source = plan([row("synthetic-g1", "A", 0), row("synthetic-g2", "B", 1)],
                      [row("synthetic-q1", "A", 0)])
        g = np.array([[2., 0.], [10., 10.]])
        q = np.array([[1., 0.]])
        cosine = evaluate(source, g, q, route="cosine", gallery_policy="available")["queries"]
        dot = evaluate(source, g, q, route="dot", gallery_policy="available")["queries"]
        self.assertEqual(cosine["known"]["rank1_correct"], 1)
        self.assertEqual(dot["known"]["rank1_wrong"], 1)

    def test_fixed_five_withholds_incomplete_hands_without_removing_probes(self):
        gallery = [row(f"synthetic-ga{i}", "A", i) for i in range(5)]
        gallery += [row(f"synthetic-gb{i}", "B", i + 5 if i < 4 else None) for i in range(5)]
        queries = [row("synthetic-qa", "A", 0), row("synthetic-qb", "B", 1),
                   row("synthetic-qc", "C", 2), row("synthetic-qd", "A", None),
                   row("synthetic-qe", None, 3), row("synthetic-qf", None, None)]
        g = np.array([[1., 0.]] * 5 + [[0., 1.]] * 4)
        q = np.array([[1., 0.], [0., 1.], [1., 1.], [1., 1.]])
        out = evaluate(plan(gallery, queries), g, q, route="cosine", gallery_policy="fixed-five")
        self.assertEqual(out["gallery"], {"planned_samples": 10, "usable_samples": 9, "scored_samples": 5,
                                          "planned_hands": 2, "scored_hands": 1})
        self.assertEqual(out["queries"]["planned"], 6)
        self.assertEqual(out["queries"]["known_planned"], 4)
        self.assertEqual(out["queries"]["unknown_planned"], 2)
        self.assertEqual(out["queries"]["known"]["rank1_correct"], 1)
        self.assertEqual(out["queries"]["known"]["true_gallery_unavailable"], 2)
        self.assertEqual(out["queries"]["known"]["query_feature_unavailable"], 1)
        self.assertEqual(out["queries"]["unknown"]["scored"], 1)
        self.assertEqual(out["queries"]["unknown"]["query_feature_unavailable"], 1)
        self.assertEqual(out["queries"]["rank1_over_planned_known"], .25)
        available = evaluate(plan(gallery, queries), g, q, route="cosine", gallery_policy="available")
        self.assertEqual(available["queries"]["known"]["rank1_correct"], 2)
        self.assertEqual(available["queries"]["unknown"]["top_score_tie"], 1)

    def test_score_is_max_per_hand_and_ties_are_between_distinct_hands(self):
        source = plan([row("synthetic-g1", "A", 0), row("synthetic-g2", "B", 1),
                       row("synthetic-g3", "A", 2), row("synthetic-g4", "A", 3)],
                      [row("synthetic-q1", "A", 0), row("synthetic-q2", "A", 1)])
        g = np.array([[2., 0.], [0., 2.], [2., 0.], [-9., 0.]])
        q = np.array([[1., 0.], [1., 1.]])
        known = evaluate(source, g, q, route="dot", gallery_policy="available")["queries"]["known"]
        self.assertEqual(known["rank1_correct"], 1)
        self.assertEqual(known["top_score_tie"], 1)
        self.assertEqual(known["rank1_wrong"], 0)

    def test_bad_features_and_overflow_never_create_a_winner(self):
        source = plan([row("synthetic-g1", "A", 0), row("synthetic-g2", "B", 1)],
                      [row("synthetic-q1", "A", 0), row("synthetic-q2", "A", 1),
                       row("synthetic-q3", "B", 2), row("synthetic-q4", "A", 3)])
        g = np.array([[1.e200, 0.], [0., 0.]])
        q = np.array([[1.e200, 0.], [np.nan, 1.], [1., 0.], [0., 0.]])
        known = evaluate(source, g, q, route="dot", gallery_policy="available")["queries"]["known"]
        self.assertEqual(known["nonfinite_score"], 1)
        self.assertEqual(known["query_feature_unavailable"], 2)
        self.assertEqual(known["true_gallery_unavailable"], 1)
        cosine = evaluate(source, g, q, route="cosine", gallery_policy="available")["queries"]["known"]
        self.assertEqual(cosine["rank1_correct"], 1)

    def test_no_eligible_gallery_reports_known_and_unknown_separately(self):
        source = plan([], [row("synthetic-q1", "A", 0), row("synthetic-q2", None, 1)])
        out = evaluate(source, np.empty((0, 2)), np.array([[0., 1.], [1., 0.]]),
                       route="cosine", gallery_policy="available")["queries"]
        self.assertEqual(out["known"]["true_gallery_unavailable"], 1)
        self.assertEqual(out["unknown"]["gallery_unavailable"], 1)

    def test_plan_rejects_duplicates_unmapped_features_and_wrong_five(self):
        g, q = np.ones((2, 2)), np.ones((1, 2))
        good_gallery = [row("synthetic-g1", "A", 0), row("synthetic-g2", "A", 1)]
        good_query = [row("synthetic-q1", "A", 0)]
        for bad in (plan(good_gallery, [row("synthetic-g1", "A", 0)]),
                    plan(good_gallery[:1], good_query),
                    plan([good_gallery[0], row("synthetic-g2", "A", 0)], good_query),
                    plan(good_gallery, [row("synthetic-q1", "A", True)])):
            with self.subTest(bad=bad), self.assertRaises(InputError):
                evaluate(bad, g, q, route="cosine", gallery_policy="available")
        with self.assertRaisesRegex(InputError, "five planned"):
            evaluate(plan(good_gallery, good_query), g, q, route="cosine", gallery_policy="fixed-five")
        with self.assertRaisesRegex(InputError, "dimensions differ"):
            evaluate(plan(good_gallery, good_query), g, np.ones((1, 3)),
                     route="cosine", gallery_policy="available")

    def test_cli_uses_only_safe_archives_and_emits_aggregate_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gp, qp, mp = root / "gal.npz", root / "qry.npz", root / "plan.json"
            np.savez(gp, features=np.array([[1., 0.]], dtype=np.float32))
            np.savez_compressed(qp, features=np.array([[1., 0.]], dtype=np.float32))
            mp.write_text(json.dumps(plan([row("synthetic-ghidden", "synthetic-hidden-hand", 0)],
                                           [row("synthetic-qhidden", "synthetic-hidden-hand", 0)])))
            argv = ["--plan", str(mp), "--gallery-features", str(gp), "--query-features", str(qp),
                    "--route", "dot", "--gallery-policy", "available"]
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(main(argv), 0)
            self.assertEqual(json.loads(stdout.getvalue())["queries"]["known"]["rank1_correct"], 1)
            self.assertNotIn("synthetic-hidden-hand", stdout.getvalue())
            self.assertNotIn("synthetic-qhidden", stdout.getvalue())
            self.assertFalse(stderr.getvalue())

            np.savez(qp, features=np.array([[object()]], dtype=object))
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(main(argv), 2)
            self.assertFalse(stdout.getvalue())
            self.assertNotIn(str(root), stderr.getvalue())
            self.assertIn("supported floating matrix", stderr.getvalue())
            np.savez(qp, features=np.array([[1., 0.]]), extra=np.zeros(1))
            with self.assertRaises(InputError):
                read_features(qp)
            with ZipFile(qp, "w") as zipfile:
                zipfile.writestr("features.npy", b"invalid numpy")
            with self.assertRaises(InputError):
                read_features(qp)
            np.savez(qp, features=np.array([[1., 0.]]))
            mp.write_text('{"schema":1,"schema":1,"gallery":[],"queries":[]}')
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as stderr:
                self.assertEqual(main(argv), 2)
            self.assertIn("duplicate JSON key", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
