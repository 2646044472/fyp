from types import SimpleNamespace as N
import sys
import enrollment_best_frame as b
import capture_station as s

class Failure(Exception):
    pass

class Image:
    size = 640, 480
    def __init__(self, frame):
        self.frame = frame
    def copy(self):
        return Image(self.frame)

def frame(n, ts, sharp, geom=True):
    return N(captured=N(frame_id=n, captured_monotonic=ts, image=Image(n)),
              roi=N(copy=lambda: n), roi_quad=N(copy=lambda: -n),
              roi_status=dict(quality={"sharpness": sharp, "contrast": 4},
                              quality_status="READY" if geom else "NO_HAND",
                              quality_required_frames=5, quality_consecutive_frames=5,
                              demo_quality_status="LOW_QUALITY", roi_mode="pklnet"))

def strict(st):
    return None if st["demo_quality_status"] == "READY" and st["roi_status_fresh"] else "blocked"

class FakeFeed:
    camera_backend = "uvc"
    running = True
    capture_profile = "mock"
    processing_thread = N(is_alive=lambda: True)
    def _camera_frame_state(self):
        return {"camera_ready": True}
    def __init__(self, frames):
        self.frames = iter(frames)
        self.now = 1
        self.latest = N(frame_id=1)
        self.latest_processed = frame(1, .95, 200)
        self.frame_condition = self
    def __enter__(self):
        pass
    def __exit__(self, *_):
        pass
    def wait(self, timeout):
        p = next(self.frames, None)
        self.now += timeout if p is None else .2
        if p is not None:
            self.latest_processed = p
            self.latest = p.captured

f = FakeFeed([frame(2,1.1,.6), frame(3,1.3,1.8),frame(4,1.5,27,False), frame(5,1.7,.9)])
preview, image, meta = b.select_frame(f,strict,Failure,clock=lambda:f.now,sample_window=.85)
assert (preview.frame, image.frame, meta["processed_roi"], meta["processed_roi_quad"]) == (3,3,3,-3)
assert f.station_enroll_last == 5, "all considered frame IDs are consumed"
f.frames = iter([frame(6,2.2,1.2),frame(7,2.4,1.5),frame(8,2.6,float("nan"))])
assert b.select_frame(f,strict,Failure,clock=lambda:f.now,sample_window=.85)[2]["capture_frame_id"] == 7
for frames in ([frame(2,1.1,0)], [frame(2,1.1,90,False)], [frame(2,.9,90)]):
    f = FakeFeed(frames)
    try:
        b.select_frame(f,strict,Failure,clock=lambda:f.now,sample_window=.85)
        raise AssertionError("empty, invalid, stale ROI should be refused")
    except Failure:
        pass

class Flow:
    def enrollment_step(self, *args, **kwargs):
        return flow.enrollment_quality_issue({"sharpness": .7, "contrast": 8})
class Camera:
    pass
class App:
    def capture_demo_feature(self, **kwargs):
        return mod._capture_readiness_gate_failure(dict(
            demo_quality_status="LOW_QUALITY",quality_status="READY",roi_status_fresh=True))
flow = N(DemoFlow=Flow, enrollment_quality_issue=lambda q: "old strict issue")
sys.modules["demo_flow"] = flow
mod=N(App=App, CameraFeed=Camera, _capture_readiness_gate_failure=strict)
b.install(mod)
assert mod.App().capture_demo_feature(enrollment=True) is None
assert mod.App().capture_demo_feature(require_live_ready=True) == "blocked"
assert flow.DemoFlow().enrollment_step("fake-token") is None
assert flow.enrollment_quality_issue({"sharpness": .7, "contrast": 8}) == "old strict issue"
assert "/api/station/enroll-status?t=" in s.render("<body>/api/status?t=</body>", "/enroll")
assert "/api/station/enroll-status?t=" not in s.render("<body>/api/status?t=</body>", "/gate")
print("PASS: ranked among valid fresh frames, consumed distinct exposures, blocked invalid geometry/zero/stale, scoped enrollment UI and runtime, verification gate remained strict")

# Geometry and pixels can survive a strict quality rejection: the older
# ProcessedFrame would expose the ROI pixels but lose its accepted quad.
frames = [frame(i, 1 + i/10, .65) for i in range(2, 23)]
for p in frames:
    p.enrollment_quad, p.roi_quad = p.roi_quad, None
    p.roi_status.update(quality_status="LOW_QUALITY", quality_reason="sharpness_below_minimum",
                        enrollment_geometry_valid=True)
    raw = dict(p.roi_status, camera_ready=True, roi_status_fresh=True)
    assert strict(raw) == "blocked" and strict(b.ranking_status(raw)) is None
    assert raw["quality_status"] == "LOW_QUALITY"  # no verification mutation
f = FakeFeed(frames)
assert b.select_frame(f,strict,Failure,clock=lambda:f.now,sample_window=.85)[2]["processed_roi_quad"] < 0
f = FakeFeed([frames[0]])
frames[0].enrollment_quad = None  # visible pixels, but invalid geometry
try:
    b.select_frame(f,strict,Failure,clock=lambda:f.now)
except Failure:
    pass
else:
    raise AssertionError("enrollment status alone cannot admit unsafe geometry")
print("PASS: low-sharpness sidecar fixes lost geometry; verification unchanged; missing geometry rejected")
