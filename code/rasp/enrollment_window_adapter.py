"""Bridge the old enrollment candidate callbacks to one bounded staged selection."""
import math
import time
from ranked_window import Candidate, Window
from enrollment_review import SLOTS, attach_frame


def descriptor(photo, captured_s):
    q = photo.roi_quad
    w,h = photo.frame_size
    cx,cy = (sum(float(p[0]) for p in q)/4/w, sum(float(p[1]) for p in q)/4/h)
    dx,dy = float(q[1][0]-q[0][0]), float(q[1][1]-q[0][1])
    scale = math.hypot(dx,dy)/min(w,h)
    return Candidate(photo.frame_id,captured_s,photo.sharpness,photo.contrast,
                     cx,cy,scale,math.atan2(dy,dx),tuple(float(x) for x in photo.texture))


def retain(s, chosen):
    items=[s["station_payloads"][c.frame_id] for c in chosen]
    s["photo_candidates"][:] = items
    for key,payload in zip(SLOTS[:-1],("feature","source","roi","quality","encoded_roi")):
        s[key][:] = [p.payload[payload] for p in items]
    s["selected_frame_ids"][:] = [x.frame_id for x in items]
    s["station_payloads"] = {x.frame_id:x for x in items}
    s["station_retained"] = tuple(chosen)


def response(s, state, base=None):
    d = dict(base or {})
    d.update(status={"partial":"STATION_PARTIAL","ready":"READY","collecting":"COLLECTING"}[state],
             kept=len(s["features"]), required=5, attempts=s["attempts"],
             candidate_pool_count=len(s["photo_candidates"]), candidate_pool_required=5,
             quality_failures=s["quality_failures"], duplicate_frames=s["duplicate_frames"],
             feature_failures=s["feature_failures"], timeout_ms_remaining=max(0,int((600-time.monotonic()+s["last_activity"])*1000)),
             selected_roi_images=list(s["selected_roi_images"]), retry_after_ms=250)
    d.pop("capture_failure",None)
    d["reason"] = ("所选照片已就绪，检查后确认保存。" if state=="ready" else
                   ("本轮取帧已停止，已保留所选候选；需要时只补齐缺额。" if state=="partial" else
                    "正在从新鲜、有效的掌区里挑选；请保持同一只手。"))
    return d


MAX_TOTAL_CAPTURE_SECONDS = 120


def initialize(s):
    """Start timing at the successful legacy enrollment Start, not first ROI."""
    if "station_started" not in s:
        s["station_started"] = s.get("started", s["last_activity"])
        s["station_payloads"] = {}
        s["station_window"] = Window(s["station_started"],
            latest_consumed_id=s.get("last_capture_frame_id") or -1)
    return s["station_started"]


def sync_selection(s, *, stop=False):
    """Only called under the flow lock, including during status and review."""
    initialize(s)
    w=s.get("station_window")
    if w is None:
        return "ready" if len(s["features"]) == 5 else "partial"
    now=time.monotonic()
    state,chosen=w.stop(now) if stop else w.status(now)
    if state!="collecting":
        retain(s,chosen)
        s["selection_mode"]="bounded_best_frame_set"
    return state


def session_status(s, d):
    state=sync_selection(s)
    result=dict(d)
    result.update(status="READY" if state=="ready" else "PAUSED",
                  station_partial=state=="partial", station_state=state,
                  kept=len(s["features"]), candidate_pool_count=len(s["photo_candidates"]),
                  selected_roi_images=list(s["selected_roi_images"]),
                  resume_allowed=time.monotonic()<s["station_started"]+MAX_TOTAL_CAPTURE_SECONDS)
    if state!="collecting":
        result.update(candidate_roi_image=None,fallback_after_ms=None,candidate_pool_required=5)
    return result


def start_refill(flow, token):
    with flow.lock:
        s = flow._active_enrollment(token)
        if s["capture_in_flight"] or s.get("station_step_in_flight") or len(s["features"])>=5:
            raise ValueError("本次照片仍在处理，或已选齐。")
        state=sync_selection(s)
        if state!="partial":
            return {"status":"CONTINUING" if state=="collecting" else "READY","kept":len(s["features"])}
        now=time.monotonic()
        cap=min(20.,s["station_started"]+MAX_TOTAL_CAPTURE_SECONDS-now)
        if cap<=0:
            raise ValueError("本次已达两分钟采集上限。已有照片仍可查看；请取消后重新开始。")
        s["station_window"] = Window(now,absolute_timeout_s=cap,useful_window_s=min(8.,cap),
                                     retained=s.get("station_retained",()),
                                     latest_consumed_id=s.get("last_capture_frame_id") or -1)
        s["last_activity"]=now
        return {"status":"CONTINUING","kept":len(s["features"])}


def run_step(flow, original, local, token, *args, **kwargs):
    # Small legacy or mock instances can continue without the station overlay.
    if not hasattr(flow, "_active_enrollment"):
        return original(flow, token, *args, **kwargs)
    with flow.lock:
        s=flow._active_enrollment(token)
        if s["capture_in_flight"] or s.get("station_step_in_flight"):
            return dict(status="WAIT",required=5,kept=len(s["features"]),retry_after_ms=250,
                        attempts=s["attempts"])
        state=sync_selection(s,stop=bool(kwargs.get("selection_only")))
        if state!="collecting":
            return response(s,state)
        w=s["station_window"]
        s["station_step_in_flight"]=True
        # Existing flow still handles capture/feature safety and de-duplication;
        # disable only its legacy finalizer (8+second wait, absolute quality).
        s["candidate_pool_required"]=25
        s["five_candidates_since"]=None
        local.capture_deadline=w.deadline
    try:
        base=original(flow,token,*args,**kwargs)
        fresh=local.review_frame
        if fresh is not None and time.monotonic()<w.deadline and w._sealed is None:
            attach_frame(flow,token,fresh[:2])
        with flow.lock:
            if flow.enrollment_session is not s or base.get("status")=="STOPPED":
                return base
            if fresh is not None and time.monotonic() < w.deadline and w._sealed is None:
                p=next((x for x in s["photo_candidates"] if x.frame_id==fresh[0]),None)
                if p is not None:
                    cand=descriptor(p,fresh[2])
                    s["station_payloads"][cand.frame_id]=p
                    state,chosen=w.observe(cand,time.monotonic())
                else:
                    state,chosen=w.status(time.monotonic())
            else:
                state,chosen=w.status(time.monotonic())
            # Review/status/stop may have sealed this same Window during I/O.
            # Publish only its chosen descriptors; never retain a late arrival.
            state=sync_selection(s)
            return response(s,state,base)
    finally:
        with flow.lock:
            s["station_step_in_flight"]=False
