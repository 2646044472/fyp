"""Small same-burst camera assay, with a disjoint calibration/probe split.

Never modifies originals or the research training queue. Not a population or
cross-session accuracy estimate. Enrollment is raw in both branches.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from pklnet_roi import PKLNetROI


def session(path):
    manifest = json.loads(path.with_suffix(".json").read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["onnx_sha256"]
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    return ort.InferenceSession(str(path), sess_options=options, providers=["CPUExecutionProvider"])


def embed(model, tensor):
    out = model.run(None, {"image": tensor})[0][0]
    return out / np.linalg.norm(out)


def threshold(scores, target=.01):
    if not scores:
        raise ValueError("No impostor calibration comparisons")
    ordered = np.sort(np.asarray(scores))[::-1]
    allowed = int(np.floor(len(scores) * target))
    return float(np.nextafter(ordered[allowed], np.inf))


def metrics(rows, name, operating):
    genuine = [r[name] >= operating for r in rows if r["genuine"]]
    impostor = [r[name] >= operating for r in rows if not r["genuine"]]
    return dict(threshold=operating, true_accepts=sum(genuine), n_genuine=len(genuine),
                false_accepts=sum(impostor), n_impostor=len(impostor),
                TAR=float(np.mean(genuine)), FMR=float(np.mean(impostor)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archives", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.output / "originals"
    source.mkdir()
    originals = []
    archive_hashes = {}
    for archive in sorted(args.archives.glob("*.zip")):
        archive_hashes[archive.name] = hashlib.sha256(archive.read_bytes()).hexdigest()
        target = source / archive.stem
        target.mkdir()
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                dest = (target / member.filename).resolve()
                if not dest.is_relative_to(target.resolve()):
                    raise ValueError("Unsafe ZIP path")
            z.extractall(target)
        originals.extend(sorted(target.rglob("full.jpg")))
    extractor = PKLNetROI(threads=2)
    restorer = session(APP / "models/local-palmir-ria.onnx")
    matcher = session(APP / "models/local-palmir-matcher.onnx")
    records, failures = [], []
    panels = []
    for path in originals:
        meta_path = path.parent / "metadata.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        subject, hand, index = meta.get("subject"), meta.get("hand"), meta.get("sample_index")
        if not subject or hand not in ("left", "right") or not index:
            failures.append(dict(source=str(path), reason="missing explicit subject/hand/sample_index"))
            continue
        try:
            roi, quad, diagnostic = extractor.extract(Image.open(path).convert("RGB"))
            if not diagnostic["roi_geometry_valid"]:
                raise ValueError(diagnostic["roi_geometry_reason"])
            rgb = np.repeat(roi[:, :, None], 3, axis=2)
            raw = rgb.transpose(2, 0, 1)[None].astype(np.float32) / 255
            restored = restorer.run(None, {"image": raw})[0]
            key = f"{subject}:{hand}"
            record = dict(identity=key, index=int(index), source=str(path),
                          original_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          raw=embed(matcher, raw), restored=embed(matcher, restored),
                          quad=quad.tolist())
            records.append(record)
            target = args.output / "rois" / f"{subject}_{hand}" / f"{int(index):02d}"
            target.mkdir(parents=True, exist_ok=False)
            before = Image.fromarray(rgb)
            after = Image.fromarray(np.rint(restored[0].transpose(1, 2, 0).clip(0, 1) * 255).astype(np.uint8))
            before.save(target / "original_roi.png")
            after.save(target / "restored_roi.png")
            if int(index) in (1, 6, 10):
                panel = Image.new("RGB", (440, 260), "white")
                panel.paste(before.resize((192, 192)), (12, 50))
                panel.paste(after.resize((192, 192)), (232, 50))
                draw = ImageDraw.Draw(panel)
                draw.text((12, 8), f"{key} #{index} | raw / restored", fill="black")
                panels.append(panel)
            print(f"ROI {len(records)}/{len(originals)} {key} #{index}", flush=True)
        except Exception as error:
            failures.append(dict(source=str(path), reason=str(error)))
    keys = sorted(set(r["identity"] for r in records))
    gallery = {k: next((r for r in records if r["identity"] == k and r["index"] == 1), None) for k in keys}
    if len(keys) < 2 or any(v is None for v in gallery.values()):
        raise ValueError("Need at least two explicitly labelled palms and sample 1 per palm")
    comparisons = []
    for record in records:
        if record["index"] == 1:
            continue
        for identity, reference in gallery.items():
            comparisons.append(dict(probe=record["source"], identity=record["identity"],
                                     gallery=identity, index=record["index"],
                                     split="calibration" if record["index"] <= 5 else "evaluation",
                                     genuine=identity == record["identity"],
                                     raw=float(np.dot(record["raw"], reference["raw"])),
                                     restored=float(np.dot(record["restored"], reference["raw"]))))
    calibration = [r for r in comparisons if r["split"] == "calibration"]
    evaluation = [r for r in comparisons if r["split"] == "evaluation"]
    operating = threshold([r["raw"] for r in calibration if not r["genuine"]])
    summary = dict(model="Local CompactRestorer RIA; raw clean matcher gallery",
                   model_onnx_sha256={name:hashlib.sha256((APP / "models" / name).read_bytes()).hexdigest()
                                      for name in ("local-palmir-ria.onnx", "local-palmir-matcher.onnx")},
                   identity_unit="explicit subject + hand (palm)", n_palms=len(keys),
                   source_originals=len(originals), valid_rois=len(records), failures=failures,
                   protocol="sample 1 raw gallery; 2-5 calibration; 6-10 evaluation; raw calibration impostors set common threshold at target FMR<=1%",
                   caveat="Small same-burst camera sample; thresholds and rates are not validated for the current USB camera, new people or sessions. No statistical independence claim.",
                   archive_sha256=archive_hashes,
                   calibration={name:metrics(calibration, name, operating) for name in ("raw", "restored")},
                   evaluation={name:metrics(evaluation, name, operating) for name in ("raw", "restored")})
    for name in ("raw", "restored"):
        probes = sorted(set(r["probe"] for r in evaluation))
        correct = sum(max((r for r in evaluation if r["probe"] == p), key=lambda r:r[name])["genuine"] for p in probes)
        summary["evaluation"][name].update(rank1_correct=correct, rank1_trials=len(probes))
    with (args.output / "scores.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparisons[0]))
        writer.writeheader(); writer.writerows(comparisons)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if panels:
        sheet = Image.new("RGB", (880, 260 * ((len(panels)+1)//2)), "#e8eeec")
        for n, panel in enumerate(panels):
            sheet.paste(panel, ((n%2)*440, (n//2)*260))
        sheet.save(args.output / "comparison.jpg", quality=92)
    write_report(summary, args.output)
    print(json.dumps(summary, indent=2), flush=True)


def write_report(summary, output):
    raw, restored = summary["evaluation"]["raw"], summary["evaluation"]["restored"]
    if restored["TAR"] > raw["TAR"] and restored["FMR"] > raw["FMR"]:
        conclusion = "本人通过增加，但其他掌纹误通过也增加，不能直接视为改善。"
    elif restored["TAR"] > raw["TAR"]:
        conclusion = "这批小样本观察到本人通过增加，仍需新摄像头和独立采集验证。"
    elif restored["TAR"] == raw["TAR"]:
        conclusion = "这批小样本中，PalmIR 风格恢复没有提高本人通过率。"
    else:
        conclusion = "这批小样本中，恢复后本人通过率下降，不建议默认启用恢复。"
    rows = ""
    for label, result in [("不恢复", raw), ("本地 RIA 恢复", restored)]:
        rows += (f'<tr><td>{label}</td><td>{result["true_accepts"]}/{result["n_genuine"]} '
                 f'({100*result["TAR"]:.1f}%)</td><td>{result["false_accepts"]}/{result["n_impostor"]} '
                 f'({100*result["FMR"]:.1f}%)</td><td>{result["rank1_correct"]}/{result["rank1_trials"]}</td></tr>')
    html = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>历史掌纹恢复测试</title>
<style>body{{font:16px system-ui;max-width:960px;margin:auto;padding:24px;background:#f4f7f5;color:#172d31;line-height:1.7}}section{{background:white;padding:24px;margin:20px 0;border-radius:14px}}table{{border-collapse:collapse;width:100%}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #dce5e3}}img{{width:100%}}a{{color:#17654b}}h1{{font-size:26px}}.note{{color:#5c6f70}}</style>
<a href="/palmir">返回实时恢复</a><h1>历史掌纹图片 · 恢复前后测试</h1><section>
<h2>{conclusion}</h2><p>2026-10-20 · GitHub FYP 历史采集 · 2 人、4 只手、{summary['source_originals']} 张原图；有效 ROI {summary['valid_rois']} 张。</p>
<table><tr><th>方法</th><th>本人通过</th><th>其他掌纹误通过</th><th>首选掌纹正确</th></tr>{rows}</table>
<p>两种方法使用同一个识别器、同一组未恢复的注册图与固定阈值 {raw['threshold']:.6f}。每只手第 1 张注册、第 2–5 张设置阈值，第 6–10 张测试。</p>
<p class="note">这只是少量连续采集图片的探索测试，包含同一人的另一只手作为非匹配掌纹，比较并不独立。不是新 USB 摄像头的通过率，也不能证明对其他人或其他采集批次有效。测试结果不改变实时页面的判定阈值，实时页面仍只比较分数。</p>
<p><a href="/palmir-scores.csv">下载逐项分数 CSV</a> · <a href="https://github.com/2646044472/fyp/tree/main/code/data/pi-captures-2026-10-15">GitHub 原始采集目录</a></p></section>
<section><h2>同一 ROI 的恢复前后示例</h2><p>每格左侧为输入，右侧为本地 RIA 恢复结果。128 × 128 图像放大展示，不代表恢复出真实缺失细节。</p><img src="/palmir-examples.jpg" alt="历史掌纹恢复前后示例"></section></html>'''
    (output / "report.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
