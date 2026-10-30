import importlib
from pathlib import Path

import pytest


def test_report_rejects_outer_v26_label_without_execution_provenance(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    reporter=importlib.import_module('report_halfturn_candidate')
    historical={'complete':True,'matcher':'FastCCCompNetAlternateROI-v26-experimental'}
    with pytest.raises(AssertionError,match='Missing verified executed matcher'):
        reporter.build({'complete':True},historical,{'complete':True})
