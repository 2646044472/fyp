"""Present corrected DoN results and preserve the earlier CNN assay separately."""
import json
from pathlib import Path
import sys


def write(root):
    don=json.loads((root/'audit/don_summary.json').read_text())['5']
    blur=json.loads((root/'audit/blur_probe_pytorch/summary.json').read_text())
    audit=json.loads((root/'audit/roi_audit.json').read_text())
    low=sum(r['std']<12 for r in audit)
    rows=''
    cases=[('Historical original (no artificial blur)',don),('Artificial Gaussian blur, sigma=1.5',blur['gaussian_1.5']),
           ('Artificial Gaussian blur, sigma=2.5',blur['gaussian_2.5']),('Artificial motion blur, 9 px / 45°',blur['motion_9_45deg'])]
    for name,result in cases:
        raw,restored=result['raw'],result['restored']
        rows+=f"<tr><td>{name}</td><td>{raw['true_accepts']}/20 → {restored['true_accepts']}/20</td><td>{raw['false_accepts']}/60 → {restored['false_accepts']}/60</td></tr>"
    images=''.join(f'<details><summary>View group {i} : all 10 originals and ROIs</summary><img src="/palmir-audit-{i}.jpg" alt="Original-image crop overlays and restoration comparison"></details>' for i in range(1,5))
    html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PalmIR × DoN audit</title><style>body{{font:16px system-ui;max-width:1100px;margin:auto;padding:24px;background:#f4f7f5;color:#172d31;line-height:1.7}}section{{background:white;padding:22px;margin:20px 0;border-radius:14px}}h1{{font-size:25px}}h2{{font-size:21px}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;padding:12px 7px;border-bottom:1px solid #dce5e3}}img{{width:100%;height:auto}}a{{color:#17654b}}.warn{{border-left:4px solid #c58a31}}summary{{cursor:pointer;padding:12px 0}}.note{{color:#566d68}}</style>
<a href="/palmir">Return to live restoration and DoN comparison</a><h1>Local PalmIR-style model × original DoN: audit results</h1>
<section><h2>No evidence for enabling restoration by default to improve genuine acceptance</h2>
<p>DoN already accepted 20/20 original probes and still accepted 20/20 after restoration. Some artificial blur conditions reduced false acceptance; others reduced genuine acceptance from 20/20 to 7/20. Gains were inconsistent.</p>
<table><tr><th>Input condition</th><th>Genuine accepted: unrestored → restored</th><th>Other hands falsely accepted: unrestored → restored</th></tr>{rows}</table>
<p>2 people, 4 hands and 40 historical originals. Images 1–5 per hand form the unrestored gallery; images 6–10 are probes. DoN uses the median distance to 5 enrollment images. The fixed threshold {don['threshold']:.6f}  comes from original images 2–5 compared with other hands and is shared across arms.</p>
<p class="note">Calibration overlaps enrollment in the same short capture sequence. This pilot establishes neither population accuracy nor calibration for a new USB camera. Artificial blur is not real camera defocus and did not replace original files. With 100% genuine acceptance, these samples cannot show a further gain.</p></section>
<section class="warn"><h2>Correction to the previous report</h2><p>The earlier 55% used a local CNN trained on PolyU and is not the original DoN acceptance rate. Its scores are preserved; no poor sample was removed. This table now uses the original DoN matcher.</p>
<p>Low-contrast blurred inputs are numerically sensitive. ONNX and PyTorch exceeded the original strict error tolerance on some images; for sigma=2.5 the number of false accepts may differ by 1. Artificial-blur results here use the original PyTorch checkpoint; identical decisions are not guaranteed on Pi ONNX. The live page compares distances only and deploys no threshold.</p></section>
<section><h2>Investigation of problematic palm images</h2><p>All 40 originals and green crop boxes were reviewed. None clearly fell outside the hand, which does not prove landmark accuracy. Shadows, low contrast and pose-dependent framing were present; they differ from synthetic Gaussian or motion blur.</p>
<p>With the engineering warning criterion of grayscale standard deviation below 12, {low} /40 were flagged but retained. Two right-hand examples (9 and 10) had contrast around 5.5 and 5.8. Some dark regions came from original shadows, not invented padding. Improve lighting, distance and alignment before reassessing restoration.</p>
{images}</section><section><h2>Artificial-blur diagnostic examples</h2><p>Each group shows historical ROI, artificially blurred input and restoration by the original PyTorch model. Restoration can alter palm detail.</p><img src="/palmir-blur-examples.jpg" alt="Three-way original, artificial blur and restored comparison"></section>
<section><h2>Integration status</h2><p>Pi USB connectivity, continuous autofocus and 640×480 preview worked; still capture was 1920×1080. The page compares original DoN distances before/after restoration and flags low contrast. It uses local CompactRestorer RIA, not the official PalmIR network. The paused training queue was not restarted.</p></section></html>'''
    (root/'report.html').write_text(html,encoding='utf-8')


if __name__=='__main__':write(Path(sys.argv[1]))
