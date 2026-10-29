import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import prepare_linked_replay as replay


def test_copy_preserves_source_and_feature_payload(tmp_path, monkeypatch):
    source = tmp_path / 'http-staged-native-test'
    source.mkdir()
    (source / 'summary.json').write_text(json.dumps({
        'live_camera_tested': False, 'matcher': replay.StagedIndexMatcher.name,
        'passes': ['old-results-must-not-be-inherited']}))
    manifest = '[{"original": "not-opened-by-copy-tool"}]'
    (source / 'input-manifest.json').write_text(manifest)
    store = replay.TemplateStore(source / 'demo_runtime/demo_templates')
    features = np.arange(60, dtype=np.uint8).reshape(5, 12)
    for feature in features:
        feature[:4] = np.asarray([replay.StagedIndexMatcher.magic], '<i4').view(np.uint8)
    store.save('person', features, {'algorithm': replay.StagedIndexMatcher.name})
    original_bytes = {p: p.read_bytes() for p in source.rglob('*') if p.is_file()}
    output = tmp_path / 'candidate'
    monkeypatch.setattr(replay, 'FEATURE_SIZE', 12)
    monkeypatch.setattr(sys, 'argv', ['copy', str(source), str(output)])
    replay.main()
    copied, meta = replay.TemplateStore(output / 'demo_runtime/demo_templates').load('person')
    np.testing.assert_array_equal(copied[:, 4:], features[:, 4:])
    assert all(f[:4].view('<i4')[0] == replay.LinkedEnrollmentMatcher.magic for f in copied)
    assert meta['algorithm'] == replay.LinkedEnrollmentMatcher.name
    assert all(p.read_bytes() == before for p, before in original_bytes.items())
    result = json.loads((output / 'summary.json').read_text())
    assert 'passes' not in result and result['fresh_enrollment_measured'] is False
    assert (output / 'input-manifest.json').read_text() == manifest
