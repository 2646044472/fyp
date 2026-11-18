"""Synthetic-only registry tests: no palm data, models, application imports or GPU."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('registry', Path(__file__).parents[1] / 'registry.py')
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


def row(key, status='completed', dependencies=()):
    return dict(id=key, candidate_status=status, title='synthetic', decision='synthetic',
                dependencies=[dict(id=k, propagates_invalidation=p) for k, p in dependencies])


class RegistryTests(unittest.TestCase):
    def test_candidate_invalidation_propagates_but_corrected_rebuild_is_separate(self):
        data = dict(schema_version=1, experiments=[row('D1', 'invalidated'),
            row('D2', dependencies=[('D1', True)]), row('D3', dependencies=[('D1', False)]),
            row('D4', dependencies=[('D2', True)])])
        by_id = registry.validate(data)
        self.assertEqual(registry.invalidation_sources('D4', by_id), ['D1'])
        self.assertEqual(registry.invalidation_sources('D3', by_id), [])

    def test_reject_duplicate_missing_cycle_and_unknown_state(self):
        examples = [[row('D1'), row('D1')], [row('D1', dependencies=[('D9', True)])],
            [row('D1', dependencies=[('D2', True)]), row('D2', dependencies=[('D1', False)])],
            [row('D1', 'finished-maybe')]]
        for rows in examples:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                registry.validate(dict(schema_version=1, experiments=rows))

    def test_inventory_is_shallow_skips_symlinks_and_does_not_read_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = root / 'synthetic-D2-X-attempt002'
            run.mkdir()
            (run / 'secret-D9').mkdir()
            (root / 'synthetic-D2-X-attempt001').mkdir()
            (root / 'synthetic-D3-file.py').write_text('not a directory')
            (root / 'linked-D4-X').symlink_to(run, target_is_directory=True)
            runs = registry.inventory(root)
            self.assertEqual(list(runs), ['D2'])
            self.assertEqual(len(runs['D2']), 2)

    def test_render_does_not_infer_completion_and_preserves_attempts(self):
        text = registry.render(dict(schema_version=1, reviewed_at='synthetic',
            experiments=[row('D2')]), {'D1': ['run-D1-X'], 'D2': ['run-D2-a', 'run-D2-b']})
        self.assertIn('| D1 | unreviewed |', text)
        self.assertIn('run-D2-a', text)
        self.assertIn('run-D2-b', text)


if __name__ == '__main__':
    unittest.main()
