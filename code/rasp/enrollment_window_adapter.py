"""Bridge the old enrollment candidate callbacks to one bounded staged selection."""
import math
import time
from ranked_window import Candidate, Window, candidate_exclusion
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
    target = s.get("station_target_count", 5)
    d.update(status={"partial":"STATION_PARTIAL","ready":"READY","collecting":"COLLECTING"}[state],
             kept=len(s["features"]), required=target, attempts=s["attempts"],
             candidate_pool_count=len(s["station_payloads"]), candidate_pool_required=target,
             quality_failures=s["quality_failures"], duplicate_frames=s["duplicate_frames"],
             feature_failures=s["feature_failures"], timeout_ms_remaining=max(0,int((600-time.monotonic()+s["last_activity"])*1000)),
             selected_roi_images=list(s["selected_roi_images"]), retry_after_ms=250)
    failure = d.pop("capture_failure", None)
    if failure:
        s["station_last_rejection"] = failure
    d["station_last_rejection"] = s.get("station_last_rejection")
    remaining = max(0, int(1000 * capture_remaining(s)))
    d["station_capture_ms_remaining"] = remaining
    d["preview_ms_remaining"] = math.ceil(1000 * preview_remaining(s))
    if state == "ready":
        d["reason"] = f"所选照片已就绪。确认后会保存 {target} 组原图与 ROI，以及登记模板。"
    elif state == "partial" and not d["kept"]:
        d["reason"] = ("这轮没有可用掌区。请让一只手的掌心完整进入画面，稳一下再开始；"
                       "如预览不动，请检查相机连接。")
    elif state == "partial":
        d["reason"] = ("采集已停止，已选照片可查看；需要时只补齐缺额。" if remaining else
                       f"已达本次采集上限；已有照片可查看，若不足 {target} 张可重新开始。")
    else:
        d["reason"] = d.get("reason") or "正在从可用掌区里挑选；请保持同一只手。"
    return d


MAX_TOTAL_CAPTURE_SECONDS = 59


def preview_remaining(s):
    duration = s.get("station_preview_seconds", 0)
    if not duration:
        return 0
    until = s.get("station_preview_until")
    if until is None:
        return duration
    paused_at = s.get("station_paused_at")
    return max(0, until - (time.monotonic() if paused_at is None else paused_at))


def arm_preview(s, now):
    if s.get("station_preview_seconds") and s.get("station_preview_until") is None:
        until = now + s["station_preview_seconds"]
        s["station_preview_until"] = until
        begin_next_window(s, until, s["station_capture_seconds"], s["station_window"].latest_consumed_id)


def capture_remaining(s):
    if preview_remaining(s):
        return s["station_capture_seconds"]
    if s.get("station_continuous"):
        if s.get("station_minimum_complete"):
            return 0
        paused_at = s.get("station_paused_at")
        return s["station_window"].deadline - (time.monotonic() if paused_at is None else paused_at)
    return s["station_started"] + s.get("station_capture_seconds", MAX_TOTAL_CAPTURE_SECONDS) - time.monotonic()


def can_resume(s):
    return s.get("station_continuous", False) or capture_remaining(s) > 0


def begin_next_window(s, now, seconds, last_frame_id, *, pool=()):
    s["station_window"] = Window(
        now, absolute_timeout_s=seconds, useful_window_s=min(12., seconds),
        retained=s.get("station_retained", ()), latest_consumed_id=last_frame_id,
        target_count=s.get("station_target_count", 5),
        wait_for_deadline=s.get("station_continuous", False),
    )
    s["station_window"].pool.extend(pool)
    s["station_state"] = "collecting"


def initialize(s):
    """Start timing at the successful legacy enrollment Start, not first ROI."""
    if "station_started" not in s:
        s["station_started"] = s.get("started", s["last_activity"])
        s["station_payloads"] = {}
        begin_next_window(s, s["station_started"], s.get("station_capture_seconds", MAX_TOTAL_CAPTURE_SECONDS),
                          s.get("last_capture_frame_id") or -1)
    return s["station_started"]


def sync_selection(s, *, stop=False, select=False):
    """Only called under the flow lock, including during status and review."""
    initialize(s)
    w=s.get("station_window")
    if w is None:
        state = "ready" if len(s["features"]) == s.get("station_target_count", 5) else "partial"
        s["station_state"] = state
        return state
    now=time.monotonic()
    if preview_remaining(s):
        if select:
            raise ValueError("请先完成预览和正式采集。")
        if stop and s.get("station_paused_at") is None:
            s["station_paused_at"] = now
        state = "partial" if s.get("station_paused_at") is not None else "collecting"
        s["station_state"] = state
        return state
    if s.get("station_continuous"):
        return sync_continuous(s, w, now, stop=stop, select=select)
    state,chosen=w.stop(now) if stop else w.status(now)
    s["station_eligible_count"] = len(chosen)
    if state!="collecting":
        retain(s,chosen)
        s["selection_mode"]="bounded_best_frame_set"
    s["station_state"] = state
    return state


def sync_continuous(s, window, now, *, stop, select):
    paused_at = s.get("station_paused_at")
    capture_now = now if paused_at is None else paused_at
    _, chosen = window.status(capture_now)
    s["station_eligible_count"] = len(chosen)
    if capture_now >= window.deadline:
        s["station_minimum_complete"] = True
    if select:
        if not s.get("station_minimum_complete") or len(chosen) != window.target_count:
            raise ValueError("请至少采集 60 秒并累积 10 张不同的候选照片。")
        retain(s, chosen)
        s["selection_mode"] = "bounded_best_frame_set"
        s["station_window"] = None
        s.pop("station_paused_at", None)
        state = "ready"
    elif paused_at is not None:
        state = "partial"
    elif stop:
        s["station_paused_at"] = now
        state = "partial"
    else:
        if now >= window.deadline:
            # Keep the ranked pool available for the user's final selection.
            begin_next_window(s, now, s["station_capture_seconds"], window.latest_consumed_id, pool=window.pool)
        state = "collecting"
    s["station_state"] = state
    return state


def session_status(s, d):
    state=sync_selection(s)
    result=dict(d)
    result.update(status="READY" if state=="ready" else "PAUSED",
                  required=s.get("station_target_count", 5),
                  station_partial=state=="partial", station_state=state,
                  kept=len(s["features"]), candidate_pool_count=len(s["station_payloads"]),
                  selected_roi_images=list(s["selected_roi_images"]),
                  resume_allowed=can_resume(s))
    if state!="collecting":
        result.update(candidate_roi_image=None, fallback_after_ms=None, candidate_pool_required=result["required"])
    return result


def start_refill(flow, token):
    with flow.lock:
        s = flow._active_enrollment(token)
        target = s.get("station_target_count", 5)
        if s["capture_in_flight"] or s.get("station_step_in_flight") or len(s["features"]) >= target:
            raise ValueError("本次照片仍在处理，或已选齐。")
        state=sync_selection(s)
        if state!="partial":
            return {"status":"CONTINUING" if state=="collecting" else "READY","kept":len(s["features"])}
        now=time.monotonic()
        if preview_remaining(s):
            s.pop("station_paused_at", None)
            s["station_preview_until"] = None
            s["last_activity"] = now
            s["station_state"] = "collecting"
            return {"status": "CONTINUING", "kept": len(s["features"])}
        previous = s.get("station_window")
        pool = ()
        last_frame = s.get("last_capture_frame_id") or -1
        if s.get("station_continuous"):
            paused_at = s.pop("station_paused_at", None)
            if previous is not None and paused_at is not None:
                pool, last_frame = previous.pool, previous.latest_consumed_id
            cap = (max(.001, previous.deadline - paused_at)
                   if paused_at is not None and not s.get("station_minimum_complete")
                   else s["station_capture_seconds"])
        else:
            cap = capture_remaining(s)
        if cap<=0:
            raise ValueError("本次已达60 秒采集上限。已有照片仍可查看；请取消后重新开始。")
        begin_next_window(s, now, cap, last_frame, pool=pool)
        s["last_activity"]=now
        return {"status":"CONTINUING","kept":len(s["features"])}


def run_step(flow, original, local, token, *args, **kwargs):
    # Small legacy or mock instances can continue without the station overlay.
    if not hasattr(flow, "_active_enrollment"):
        return original(flow, token, *args, **kwargs)
    with flow.lock:
        s=flow._active_enrollment(token)
        state=sync_selection(s,stop=bool(kwargs.get("selection_only")))
        if state!="collecting":
            return response(s,state)
        if preview_remaining(s):
            return response(s, state)
        if s["capture_in_flight"] or s.get("station_step_in_flight"):
            return dict(status="WAIT",required=s.get("station_target_count", 5),
                        kept=len(s["features"]),retry_after_ms=250,
                        attempts=s["attempts"])
        w=s["station_window"]
        s["station_step_in_flight"]=True
        # Existing flow still handles capture/feature safety and de-duplication;
        # disable only its legacy finalizer (8+second wait, absolute quality).
        local.capture_deadline=w.deadline
    try:
        base=original(flow,token,*args,**kwargs)
        fresh=local.review_frame
        if fresh is not None and time.monotonic()<w.deadline and w._sealed is None:
            attach_frame(flow, token, fresh[:2], original_jpeg=fresh[3] if len(fresh) > 3 else None)
        with flow.lock:
            if flow.enrollment_session is not s or base.get("status")=="STOPPED":
                return base
            last_attempt = base.get("capture_failure")
            if (fresh is not None and time.monotonic() < w.deadline and w._sealed is None
                    and s["station_window"] is w and s.get("station_paused_at") is None):
                p=next((x for x in s["photo_candidates"] if x.frame_id==fresh[0]),None)
                if p is not None:
                    cand=descriptor(p,fresh[2])
                    s["station_payloads"][cand.frame_id]=p
                    _, chosen = w.observe(cand, time.monotonic())
                    if last_attempt is None:
                        last_attempt = ("LOW_QUALITY" if cand not in w.pool else candidate_exclusion(cand, chosen))
                    active_ids = {item.frame_id for item in (*w.retained, *w.pool)}
                    s["station_payloads"] = {i: photo for i, photo in s["station_payloads"].items() if i in active_ids}
                    s["photo_candidates"][:] = [photo for photo in s["photo_candidates"] if photo.frame_id in active_ids]
            elif s.get("station_continuous"):
                s["photo_candidates"][:] = [photo for photo in s["photo_candidates"] if photo.frame_id in s["station_payloads"]]
            s["station_last_rejection"] = last_attempt
            # Review/status/stop may have sealed this same Window during I/O.
            # Publish only its chosen descriptors; never retain a late arrival.
            state=sync_selection(s)
            return response(s,state,base)
    finally:
        with flow.lock:
            s["station_step_in_flight"]=False
