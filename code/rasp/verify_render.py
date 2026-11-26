"""Check the English overlays without starting the camera or a service."""
from pathlib import Path
import re
from runpy import run_path
import subprocess
import sys

from capture_station import render, stand_by

here = Path(__file__).resolve().parent
enroll = run_path(sys.argv[1] if len(sys.argv) > 1 else str(here / "demo_page.py"))["HTML"]
rendered = render(enroll, "/enroll")
for needle in (
    "STATION_PARTIAL", "stationPartial", "station-review",
    "function scheduleEnrollmentCommit(token,retries=0){return;",
    "/api/station/enroll-refill", "/api/station/enroll-status",
    'aria-current=page>① Palm enrollment', "Continue capture / Retake",
    "Stop and keep selected photos", "Remove and retake",
    "Review the originals and ROIs, then confirm to save.",
    "This page will not submit another save automatically.",
    "Nothing is saved until you confirm.", "60-second capture limit reached",
    "Confirm same hand and save", "Go to Palm verification",
):
    assert needle in rendered, needle
assert rendered.count('id="station-review-items"') == 1
assert rendered.count('id="station-zoom-img"') == 1
assert "thumb(i.rgb,'Original','image/jpeg'),thumb(i.roi,'ROI','image/png')" in rendered
assert "zoomImage.src=img.src;zoom.showModal()" in rendered
assert "Demo item · MOP 20.00" not in rendered
assert "new MediaRecorder" not in rendered and "getUserMedia" not in rendered
for obsolete in (
    "The system automatically selects and saves five frames.",
    "Five qualified palm regions are selected and saved automatically.",
    "Saving.${elapsed}",
):
    assert obsolete not in rendered, obsolete

gate = render(enroll, "/gate")
assert "station-review-items" not in gate
assert 'aria-current=page>② Palm verification' in gate and "Pause verification" in gate
collection = render(run_path(str(here / "collection_page.py"))["HTML"], "/collect")
assert 'aria-current=page>③ Data management' in collection
assert 'id="start">Start a set of retakes</button>' in collection
standby = stand_by("/enroll", "Synthetic check")
assert "Waiting for the camera and recognition service" in standby
assert "Synthetic check" in standby and "<html lang=en>" in standby

if len(sys.argv) == 1:
    # This known pre-English anchor still needs to work when the station overlay
    # is upgraded without reinstalling a compatible old demo engine.
    legacy = enroll.replace("Continue capture</button>",
                            "\u7ee7\u7eed\u91c7\u96c6</button>")
    assert legacy != enroll
    assert "Continue capture / Retake</button>" in render(legacy, "/enroll")

for page in (rendered, gate, collection, standby):
    scripts = re.findall(r"<script>(.*?)</script>", page, re.S)
    assert scripts
    for script in scripts:
        subprocess.run(["node", "--check"], input=script, text=True, check=True)

# The legacy base declares an automatic-save function. A ready selection in
# the station must never schedule a timer or call the save handler implicitly.
start = rendered.index("function scheduleEnrollmentCommit(")
end = rendered.index("\nfunction enrollmentSelectionText", start)
subprocess.run(
    ["node"],
    input=rendered[start:end] + '''
let calledAnySaveHook = false;
global.setTimeout = () => { calledAnySaveHook = true; };
scheduleEnrollmentCommit("synthetic");
if (calledAnySaveHook) throw Error("Enrollment overlay scheduled auto-save");
''',
    text=True,
    check=True,
)
print("PASS: English enrollment, verification and data management; valid browser JS; manual save only")
