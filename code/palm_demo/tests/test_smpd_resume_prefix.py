import importlib
import inspect
from pathlib import Path

import pytest


def module(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('resume_raw_smpd')


def test_resume_preserves_failed_queries_and_never_filters_by_outcome(monkeypatch):
    m=module(monkeypatch)
    rows=[dict(sample='a',subject='001',index=5,enrollment=False),dict(sample='b',subject='001',index=6,enrollment=False),
          dict(sample='enroll',subject='001',index=0,enrollment=True),dict(sample='c',subject='002',index=5,enrollment=False)]
    prefix=[dict(sample='a',correct=False,http_status=400),dict(sample='b',correct=False,http_status=200)]
    assert [r['sample'] for r in m.remaining(rows,prefix)]==['c']
    with pytest.raises(AssertionError,match='prefix'):m.remaining(rows,[prefix[1]])
    with pytest.raises(AssertionError,match='Duplicate'):m.remaining(rows,[prefix[0],prefix[0]])


def test_restart_metadata_keeps_original_results_and_initial_startup(monkeypatch):
    m=module(monkeypatch)
    common=dict(protocol_sha256='P',archive_sha256='A',enrollments=[dict(identity='one',registered=True)],actual_gallery_identities=1)
    previous=dict(common,complete=False,startup_and_gallery_ready_ms=11,queries=[dict(sample='a',correct=False)],warnings=[])
    fresh=dict(common,complete=False,startup_and_gallery_ready_ms=22,queries=[],warnings=[])
    result=m.resumed_report(fresh,previous,22)
    assert result['queries']==previous['queries'] and result['queries'] is not previous['queries']
    assert result['startup_and_gallery_ready_ms']==11
    assert result['resume_epochs'][0]['startup_and_gallery_ready_ms']==22
    assert previous['warnings']==[]


def test_operational_adapter_keeps_capture_scoring_and_http_body_exact(monkeypatch):
    m=module(monkeypatch);source=inspect.getsource(m.base.run);adapted=m.adapt(source)
    begin='        camera.select([row]);numeric.clear();status,response,elapsed=request'
    end="       assert len(report['queries'])==protocol['query_images']"
    assert source[source.index(begin):source.index(end)]==adapted[adapted.index(begin):adapted.index(end)]
    compile(adapted,'<verified-operational-resume>','exec')
