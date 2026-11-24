from pathlib import Path
import numpy as np


def test_pilot_cache_checks_inputs_and_cannot_leak_mutable_results(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    from profile_fallback_reuse import Recorder
    recorder=Recorder(cache=True)
    def reset():
        import time
        recorder.current=dict(start=time.perf_counter(),seen={},events=[],cache={},cache_bytes=0)
    reset();calls=[]
    def function(a):calls.append(1);return a.copy(),a.copy()*2
    a=np.arange(8,dtype=np.uint8)
    # Simulate a key collision; equality checks must still reject different data.
    key=lambda *_:'same-key'
    first=recorder.call(function,'sift',(a,),{},key)
    first[0][:]=255
    second=recorder.call(function,'sift',(a.copy(),),{},key)
    np.testing.assert_array_equal(second[0],a)
    assert len(calls)==1
    b=a+1
    third=recorder.call(function,'sift',(b,),{},key)
    np.testing.assert_array_equal(third[0],b)
    assert len(calls)==2
    a[:]=42
    mutated=recorder.call(function,'sift',(a,),{},key)
    np.testing.assert_array_equal(mutated[0],a)
    assert len(calls)==3
    reset()
    recorder.call(function,'sift',(a,),{},key)
    assert len(calls)==4
