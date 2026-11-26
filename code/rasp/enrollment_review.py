"""Review and mutation of this token's provisional enrollment only."""
from base64 import b64encode
from io import BytesIO
import math
import time

SLOTS = ("features", "sources", "rois", "qualities", "selected_roi_images", "selected_frame_ids")
DEFAULT_TIMEOUT = 600


def attach_frame(flow, token, incoming, *, original_jpeg=None):
    if incoming is None:
        return
    frame_id, image = incoming
    with flow.lock:
        s = flow.enrollment_session
        if s is None or s["token"] != token:
            return
        candidate = next((x for x in s["photo_candidates"] if x.frame_id == frame_id), None)
        if candidate is not None:
            # Keep review traffic small. The archive uses the camera's JPEG when available.
            output = BytesIO()
            image.save(output, format="JPEG", quality=87)
            preview_jpeg = output.getvalue()
            candidate.payload["station_review_rgb"] = b64encode(preview_jpeg).decode("ascii")
            candidate.payload["station_original_jpeg"] = original_jpeg if original_jpeg is not None else preview_jpeg
            candidate.payload["station_native_original"] = original_jpeg is not None


def selected_photo(flow, token, frame_id):
    with flow.lock:
        s = flow.enrollment_session
        if (s is not None and s["token"] == token and time.monotonic() - s["last_activity"] < DEFAULT_TIMEOUT
                and type(frame_id) is int and frame_id in s["selected_frame_ids"]):
            for photo in s["photo_candidates"]:
                if photo.frame_id == frame_id and photo.payload.get("station_original_jpeg"):
                    return photo
    raise ValueError("This photo is no longer in the current selection.")


def mutate(flow, token, frame_id=None, *, stop=False, select=False, geometry=False):
    from enrollment_window_adapter import can_resume, capture_remaining, preview_remaining, sync_selection
    with flow.lock:
        s = flow.enrollment_session
        if s is None or s["token"] != token or time.monotonic() - s["last_activity"] >= DEFAULT_TIMEOUT:
            return {"status": "INACTIVE", "items": [], "kept": 0}
        if select and (s["capture_in_flight"] or s.get("station_step_in_flight")):
            raise ValueError("The last frame is still processing. Please wait.")
        state = sync_selection(s, stop=stop, select=select)
        selected = tuple(s["selected_frame_ids"])
        if frame_id is not None:
            if state=="collecting" or s["capture_in_flight"] or s.get("station_step_in_flight") or frame_id not in selected:
                raise ValueError("The photo status changed. Refresh the preview and try again.")
            if not all(len(s[k]) == len(selected) for k in SLOTS):
                raise ValueError("The photo list is out of sync. Nothing was removed.")
            remaining = tuple(x for x in selected if x != frame_id)
            by_id = {c.frame_id: c for c in s["photo_candidates"]}
            if not all(x in by_id for x in remaining):
                raise ValueError("This candidate is unavailable. Nothing was removed.")
            idx = selected.index(frame_id)
            for key in SLOTS:
                s[key].pop(idx)
            s["photo_candidates"][:] = [by_id[x] for x in remaining]
            s["candidate_pool_required"] = s.get("station_target_count", 5)
            s["five_candidates_since"] = None
            s["last_activity"] = time.monotonic()
            s["station_retained"] = tuple(c for c in s.get("station_retained",()) if c.frame_id != frame_id)
            s["station_payloads"].pop(frame_id, None)
            s["station_window"] = None
            state = "partial"
            s["station_state"] = state
            s["station_eligible_count"] = len(remaining)
            selected = remaining
        # Do not enumerate a gallery. Before selection the base capture UI
        # displays progress; the review only shows chosen pairs and replacements.
        by_id = {c.frame_id: c for c in s["photo_candidates"]}
        items = [{"frame": k, "rgb": by_id[k].payload.get("station_review_rgb"),
                  "roi": by_id[k].payload.get("encoded_roi")} for k in selected if k in by_id]
        if geometry:
            for item in items:
                photo = by_id[item["frame"]]
                item.update(quad=photo.roi_quad.tolist(), size=list(photo.frame_size))
        return {"status": "REVIEW", "items": items, "kept": len(selected), "required": s.get("station_target_count", 5),
                "preview_ms_remaining": math.ceil(1000 * preview_remaining(s)),
                "preview_waiting_camera": bool(s.get("station_preview_seconds") and s.get("station_preview_until") is None),
                "station_capture_ms_remaining": max(0, int(1000 * capture_remaining(s))),
                "candidate_count": len(s["station_payloads"]),
                "attempts": s.get("attempts", 0),
                "duplicates": s.get("duplicate_frames", 0),
                "last_rejection": s.get("station_last_rejection"),
                "eligible_count": max(len(selected), s.get("station_eligible_count", 0)) if state != "ready" else len(selected),
                "minimumComplete": s.get("station_minimum_complete", False),
                "archive_only": s.get("archive_only", False),
                "state": state, "inFlight": bool(s["capture_in_flight"] or s.get("station_step_in_flight")),
                "resumeAllowed": state == "partial" and can_resume(s)}


PANEL = '''<style>
#station-review{background:#edf7fb;border-radius:12px;padding:12px;margin:12px 0}
#station-review[hidden]{display:none}#enroll-thumbs{display:none!important}.station-pair{display:grid;grid-template-columns:1.4fr 1fr auto;gap:8px;align-items:center;margin:8px 0}
.station-pair button{margin:0;padding:6px;font-size:.86rem}.station-pair img{width:100%;height:68px;object-fit:contain;display:block}
#station-zoom{border:0;border-radius:12px;max-width:92vw;padding:10px}#station-zoom img{display:block;max-width:86vw;max-height:75vh;object-fit:contain}
</style><section id="station-review" hidden aria-label="Photos for this enrollment"><strong id="station-review-count"></strong> <button type="button" id="station-stop" class="secondary" hidden>Stop and keep selected photos</button><div id="station-review-items"></div></section>
<dialog id="station-zoom"><form method="dialog"><button>Close enlarged view</button></form><img id="station-zoom-img" alt=""></dialog>
<script>
(()=>{const panel=document.getElementById('station-review'),list=document.getElementById('station-review-items'),heading=document.getElementById('station-review-count');
const zoom=document.getElementById('station-zoom'),zoomImage=document.getElementById('station-zoom-img'),stop=document.getElementById('station-stop');
let epoch=0,pending=false,signature='',lastToken='';
zoom.addEventListener('close',()=>zoomImage.removeAttribute('src'));
const reload=()=>{zoom.close();zoomImage.removeAttribute('src');list.replaceChildren();signature='';panel.hidden=true};
function thumb(data,kind,mime){const b=document.createElement('button');b.type='button';b.textContent=kind;b.disabled=!data;
if(data){const img=document.createElement('img');img.alt=kind;img.src='data:'+mime+';base64,'+data;b.prepend(img);
b.onclick=()=>{zoomImage.alt=kind;zoomImage.src=img.src;zoom.showModal()}}return b}
function draw(d,t){const items=Array.isArray(d.items)?d.items:[];const key=items.map(i=>i.frame+':'+Boolean(i.rgb)+':'+Boolean(i.roi)).join(',');
if(d.status!=='REVIEW'){reload();return}panel.hidden=false;
const partial=d.state==='partial';stationResumeAllowed=d.resumeAllowed!==false;stop.hidden=d.state!=='collecting';
if(partial&&!stationPartial){stationPartial=true;enrollmentPaused=true;enrollmentSawNotReady=false;
notice.textContent=d.kept?'Capture stopped. Your selection is retained; you can retake only the missing photos.':'No usable palm region. Hold one palm fully in frame. If the preview is frozen, check the camera connection.';controls()}
heading.textContent='Selected '+d.kept+'/5 photos'+(d.kept<5?(d.state==='collecting'?' · Selecting photos':' · Still needed: '+(5-d.kept)):' · Click an original or ROI to enlarge');
if(partial&&!stationResumeAllowed)heading.textContent+=' · 60-second capture limit reached';
const locked=d.inFlight||d.state==='collecting';
enrollmentThumbnails=items.map(i=>i.roi).filter(Boolean);document.getElementById('enroll-thumbs').replaceChildren();
if(d.state==='ready'&&!d.inFlight&&!busy&&!enrollmentStopping){document.getElementById('enroll-commit').hidden=false;enrollmentPaused=false;controls()}
if(key===signature){for(const b of list.querySelectorAll('.station-remove'))b.disabled=!!locked;return}signature=key;list.replaceChildren();
for(const i of items){const row=document.createElement('div');row.className='station-pair';const remove=document.createElement('button');remove.type='button';remove.className='secondary station-remove';remove.textContent='Remove and retake';remove.disabled=locked;
remove.onclick=async()=>{if(pending||busy||enrollmentToken!==t||!confirm('Remove this unsaved original and ROI pair and retake it?'))return;
epoch++;pending=true;remove.disabled=true;try{const next=await post('/api/station/enroll-remove',{token:t,frame:i.frame});
if(enrollmentToken!==t)return;if(next.status!=='REVIEW')throw Error('This session has ended.');zoom.close();document.getElementById('enroll-commit').hidden=true;
enrollmentPaused=true;enrollmentSawNotReady=false;stationPartial=true;draw(next,t);notice.textContent='Pair removed. Keep the same hand ready to retake one photo.';controls()
}catch(e){if(enrollmentToken===t)notice.textContent=e.message}finally{pending=false;remove.disabled=false}};
row.append(thumb(i.rgb,'Original','image/jpeg'),thumb(i.roi,'ROI','image/png'),remove);list.append(row)}}
stop.onclick=async()=>{const t=enrollmentToken;if(!t||pending)return;epoch++;pending=true;stop.disabled=true;
try{const d=await post('/api/station/enroll-stop',{token:t});if(t===enrollmentToken)draw(d,t)}
catch(e){if(t===enrollmentToken)notice.textContent=e.message}
finally{pending=false;stop.disabled=false}};
async function poll(){const t=enrollmentToken;if(t!==lastToken){lastToken=t;epoch++;reload()}if(!t||pending||document.hidden){setTimeout(poll,650);return}
const e=epoch;try{const d=await post('/api/station/enroll-review',{token:t});if(t===enrollmentToken&&e===epoch&&!pending)draw(d,t)}catch(_){}finally{setTimeout(poll,850)}}poll();
})()
</script>'''
