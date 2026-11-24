from types import SimpleNamespace as N
from threading import Lock
import time
from enrollment_review import mutate, SLOTS, attach_frame

class Image:
    def save(self, f, **kw):
        f.write(b"synthetic-image")
flow = N(lock=Lock())
def candidate(i):
    return N(frame_id=i,payload={"encoded_roi":f"roi-{i}"})
s = dict(token="current", last_activity=time.monotonic(), capture_in_flight=False,
         selected_frame_ids=[1,2,3,4,5], photo_candidates=[candidate(i) for i in range(1,8)],
         candidate_pool_required=8, five_candidates_since=1, last_capture_frame_id=7)
for k in SLOTS[:-1]:
    s[k]=[f"{k}-{i}" for i in s["selected_frame_ids"]]
s.update(station_started=s["last_activity"], station_window=None,
         station_payloads={c.frame_id:c for c in s["photo_candidates"]})
flow.enrollment_session = s
assert mutate(flow,"unrelated",2)["items"] == []
attach_frame(flow,"current",(2,Image()))
assert mutate(flow,"current")["items"][1] == {"frame":2,"rgb":"c3ludGhldGljLWltYWdl","roi":"roi-2"}
s["capture_in_flight"]=True
try:
    mutate(flow,"current",2)
    raise AssertionError("concurrent delete allowed")
except ValueError:
    pass
s["capture_in_flight"]=False
d=mutate(flow,"current",2)
assert [x["frame"] for x in d["items"]] == [1,3,4,5] and d["kept"]==4
assert s["selected_frame_ids"] == [1,3,4,5]
assert 2 not in s["station_payloads"]
for k in SLOTS[:-1]:
    assert s[k] == [f"{k}-{i}" for i in [1,3,4,5]]
assert [x.frame_id for x in s["photo_candidates"]] == [1,3,4,5]
assert s["last_capture_frame_id"]==7 and s["candidate_pool_required"]==5
try:
    mutate(flow,"current",2)
    raise AssertionError("stale frame was deleted twice")
except ValueError:
    pass
flow.enrollment_session = None
assert mutate(flow,"current")["items"] == []
print("PASS: same-frame thumbnail, current-session guard, in-flight/dead token guard, delete exact paired slot, 4/5 awaiting a new frame")
