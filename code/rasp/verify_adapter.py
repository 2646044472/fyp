from types import SimpleNamespace as N
from threading import Lock
from ranked_window import Window
import enrollment_window_adapter as a
import enrollment_review as r

class Picture:
    def save(self,f,**kw):f.write(b"synthetic")

class Flow:
    def __init__(self):
        self.lock=Lock()
        self.enrollment_session=dict(token="session",capture_in_flight=False,features=[],
            sources=[],rois=[],qualities=[],selected_roi_images=[],selected_frame_ids=[],
            photo_candidates=[],last_activity=100.0,attempts=0,quality_failures=0,
            duplicate_frames=0,feature_failures=0)
    def _active_enrollment(self,token):
        assert token=="session"
        return self.enrollment_session

original_clock = a.time.monotonic
try:
    now = 100.0
    a.time.monotonic=lambda:now
    f=Flow()
    loc=N(review_frame=None,capture_deadline=None)
    def base(f,token):
        s=f.enrollment_session
        s["attempts"]+=1
        s["last_activity"]=now
        if loc.review_frame:
            fid,_,ts=loc.review_frame
            x=40+4*fid
            p=N(frame_id=fid,roi_quad=[(x,50),(x+29,50+2.5*fid),(x+30,78),(x,80)],
               frame_size=(180,130),sharpness=.7,contrast=5,texture=(0,.4,.3,.6,1),
               payload=dict(feature=f"feature-{fid}",source="synthetic",roi=f"roi-{fid}",
                            quality={},encoded_roi=f"roi-png-{fid}"))
            s["photo_candidates"].append(p)
            s["last_capture_frame_id"]=fid
        return {"status":"WAIT","capture_failure":"ROI_NOT_READY"}
    for fid in range(1,5):
        now += .45
        loc.review_frame=(fid,Picture(),now)
        assert a.run_step(f,base,loc,"session")["status"]=="COLLECTING"
    now+=9
    d=a.run_step(f,base,loc,"session")
    assert (d["status"],d["kept"])==("STATION_PARTIAL",4)
    assert f.enrollment_session["attempts"]==4
    assert dict(r.mutate(f,"session")["items"][0])["rgb"]=="c3ludGhldGlj"
    a.start_refill(f,"session")
    now += .5
    loc.review_frame=(5,Picture(),now)
    d=a.run_step(f,base,loc,"session")
    assert (d["status"],d["kept"])==("READY",5)
    assert r.mutate(f,"session",5)["kept"]==4
    retained_ids=list(f.enrollment_session["selected_frame_ids"])
    a.start_refill(f,"session")
    now += .5
    loc.review_frame=(6,Picture(),now)
    d=a.run_step(f,base,loc,"session")
    assert (d["status"],d["kept"])==("READY",5)
    assert f.enrollment_session["selected_frame_ids"]==retained_ids+[6]
    g=Flow()
    g.enrollment_session["last_activity"]=now
    loc.review_frame=None
    assert a.run_step(g,base,loc,"session")["status"]=="COLLECTING"
    now+=20
    assert a.run_step(g,base,loc,"session")["status"]=="STATION_PARTIAL"
    assert g.enrollment_session["attempts"]==1
    # A paused browser must not move the clock when the first request is late.
    now=200.0
    g=Flow()
    g.enrollment_session.update(started=now,last_activity=now)
    a.initialize(g.enrollment_session)
    a.initialize(g.enrollment_session)
    now+=21
    loc.review_frame=(1,Picture(),now)
    assert a.session_status(g.enrollment_session,{})["station_partial"]
    d=a.run_step(g,base,loc,"session")
    assert (d["status"],d["kept"],d["attempts"])==("STATION_PARTIAL",0,0)

    # Three captured originals survive status-only refresh and immediate refill.
    now=300.
    h=Flow()
    h.enrollment_session.update(started=now,last_activity=now)
    for fid in range(1,4):
        now+=.45
        loc.review_frame=(fid,Picture(),now)
        assert a.run_step(h,base,loc,"session")["status"]=="COLLECTING"
    now+=9
    d=a.session_status(h.enrollment_session,{})
    assert d["station_state"]=="partial" and d["kept"]==3
    assert sorted(x["frame"] for x in r.mutate(h,"session")["items"])==[1,2,3]
    assert a.start_refill(h,"session")["kept"]==3
    assert sorted(x["frame"] for x in r.mutate(h,"session")["items"])==[1,2,3]
    now+=.5
    loc.review_frame=(4,Picture(),now)
    a.run_step(h,base,loc,"session")
    d=a.run_step(h,base,loc,"session",selection_only=True)
    assert (d["status"],d["kept"],d["attempts"])==("STATION_PARTIAL",4,4)
    a.start_refill(h,"session")
    now+=.5
    loc.review_frame=(5,Picture(),now)
    assert a.run_step(h,base,loc,"session")["kept"]==5
    assert r.mutate(h,"session",5)["kept"]==4
    assert sorted(h.enrollment_session["station_payloads"])==[1,2,3,4]
    now=419.75
    assert a.start_refill(h,"session")["kept"]==4
    assert h.enrollment_session["station_window"].deadline==420
    now=420
    loc.review_frame=(6,Picture(),now)
    d=a.run_step(h,base,loc,"session")
    assert (d["status"],d["kept"],d["attempts"])==("STATION_PARTIAL",4,5)
    try:
        a.start_refill(h,"session")
        raise AssertionError("refill after two minutes accepted")
    except ValueError:
        pass

    # A capture completing after Stop is purged, even if legacy candidate callback finishes.
    now=500.
    j=Flow()
    j.enrollment_session.update(started=now,last_activity=now)
    for fid in range(1,3):
        now+=.45
        loc.review_frame=(fid,Picture(),now)
        a.run_step(j,base,loc,"session")
    def stopped_during_step(flow,token,**_):
        assert sorted(x["frame"] for x in r.mutate(flow,token,stop=True)["items"])==[1,2]
        return base(flow,token)
    now+=.45
    loc.review_frame=(3,Picture(),now)
    d=a.run_step(j,stopped_during_step,loc,"session")
    assert (d["status"],d["kept"])==("STATION_PARTIAL",2)
    assert sorted(x.frame_id for x in j.enrollment_session["photo_candidates"])==[1,2]
    assert sorted(j.enrollment_session["station_payloads"])==[1,2]

finally:
    a.time.monotonic=original_clock
print("PASS: Start-anchored timeout, status-only partial survival, explicit stop and late completion, payload eviction, fresh refill and 120s total cap")
