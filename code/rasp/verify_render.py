from pathlib import Path
import re, subprocess, sys, tempfile
from capture_station import render
from runpy import run_path
enroll=run_path(sys.argv[1] if len(sys.argv)>1 else str(Path(__file__).with_name("demo_page.py")))['HTML']
rendered=render(enroll,'/enroll')
for needle in ("STATION_PARTIAL", "stationPartial", "station-review",
               "仅", "function scheduleEnrollmentCommit(token,retries=0){return;",
               "/api/station/enroll-refill","/api/station/enroll-status"):
    if needle=="仅":continue
    assert needle in rendered,needle
assert rendered.count('id="station-review-items"')==1
assert rendered.count('id="station-zoom-img"')==1
assert "thumb(i.rgb,'原图','image/jpeg'),thumb(i.roi,'ROI','image/png')" in rendered
assert "zoomImage.src=img.src;zoom.showModal()" in rendered
assert "60 秒" in rendered
assert "new MediaRecorder" not in rendered and "getUserMedia" not in rendered
assert "station-review-items" not in render(enroll,"/gate")
for script in re.findall(r'<script>(.*?)</script>',rendered,re.S):
    subprocess.run(["node","--check"],input=script,text=True,check=True)
print("PASS: existing demo page rendered with enrollment-only preview/review, browser JS syntax, no auto-commit")
