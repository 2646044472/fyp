import importlib
from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
import json,numpy as np,pytest


@pytest.fixture
def helpers(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('operation_cost_oracle')


def test_replay_is_copied_and_input_drift_is_rejected(helpers):
    trace=helpers.OperationTrace();oracle=helpers.FeatureOracle(trace)
    module=SimpleNamespace(feature=lambda x:(x.astype(np.float32),np.ones((2,3),np.float32)))
    oracle.wrap(module,'feature','feature');x=np.zeros((2,2),np.uint8)
    try:
        oracle.begin('record');module.feature(x);oracle.finish()
        oracle.begin('verify');result=module.feature(x);oracle.finish();result[0][:]=99
        oracle.begin('timed');result=module.feature(x);oracle.finish();assert not result[0].any()
        oracle.begin('verify')
        with pytest.raises(AssertionError,match='Input drift'):module.feature(np.ones_like(x))
    finally:oracle.close()


def test_parallel_task_paths_are_stable(helpers):
    trace=helpers.OperationTrace();oracle=helpers.FeatureOracle(trace)
    module=SimpleNamespace(feature=lambda x:(x.astype(np.float32),np.ones((2,3),np.float32)))
    oracle.wrap(module,'feature','feature');oracle.install_submit(ThreadPoolExecutor)
    try:
        with ThreadPoolExecutor(max_workers=2)as pool:
            for mode in ('record','verify','timed'):
                oracle.begin(mode)
                values=list(pool.map(module.feature,[np.full((2,2),i,np.uint8)for i in range(5)]))
                assert [int(v[0][0,0])for v in values]==list(range(5));oracle.finish()
    finally:oracle.close()


def test_budget_stops_before_recording_unbounded_data(helpers):
    oracle=helpers.FeatureOracle(helpers.OperationTrace(),budget=1)
    module=SimpleNamespace(feature=lambda x:(x.copy(),x.copy()))
    oracle.wrap(module,'feature','feature')
    try:
        oracle.begin('record')
        with pytest.raises(AssertionError,match='budget'):module.feature(np.zeros((2,2),np.uint8))
    finally:oracle.close()


def test_trace_exports_specs_and_exclusive_cpu_without_array_values(helpers):
    trace=helpers.OperationTrace();module=SimpleNamespace(child=lambda x:x.copy())
    trace.wrap(module,'child','copy','copy')
    root=trace.function(lambda:module.child(np.zeros((3,4),np.uint8)),'root','framework')
    trace.begin();root();data=trace.finish();trace.close()
    json.dumps(data)
    assert len(data['nodes'])==2
    assert data['nodes'][1]['input_spec'][0]['shape']==[3,4]
    assert sum(data['global_wall_partition_ms'].values())==pytest.approx(data['nodes'][0]['inclusive_ms'])
    assert all(v['exclusive_thread_cpu_ms']>=0 for v in data['nodes'])
