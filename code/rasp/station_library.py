"""Read confirmed image sets inside this station's private enrollment archive."""
from datetime import datetime
from io import BytesIO
import json
import re
from types import SimpleNamespace

from PIL import Image

from enrollment_archive import native_roi_png


def valid_id(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{32}", value)


def read_manifest(folder):
    manifest = folder / "manifest.json"
    if folder.is_symlink() or manifest.is_symlink():
        raise ValueError("无效归档。")
    return json.loads(manifest.read_text("utf-8"))


def list_archives(root):
    archives = []
    if not root.exists():
        return archives
    for folder in root.iterdir():
        if not valid_id(folder.name) or folder.is_symlink() or not folder.is_dir():
            continue
        data = read_manifest(folder)
        archives.append(dict(id=folder.name, participant=data["participant_code"], hand=data["hand"],
                             saved=datetime.fromtimestamp(folder.stat().st_mtime).astimezone().isoformat(),
                             samples=[dict(size=s["analysis_size"], quad=s["roi_quad_at_analysis_size"])
                                      for s in data["samples"]]))
    return sorted(archives, key=lambda item: item["saved"], reverse=True)


def archive_image(root, request):
    archive, index, kind = (request.get(k) for k in ("archive", "index", "kind"))
    if not valid_id(archive) or type(index) is not int or not 1 <= index <= 5:
        raise ValueError("无效归档照片。")
    folder = root / archive
    samples = read_manifest(folder)["samples"]
    if index > len(samples) or kind not in ("original", "preview", "detail", "model"):
        raise ValueError("无效归档照片。")
    suffix = {"original": "original.jpg", "preview": "original.jpg", "model": "roi.png", "detail": "roi-native.png"}
    path = folder / f"{index:02d}-{suffix[kind]}"
    if path.is_symlink():
        raise ValueError("无效归档文件。")
    if kind == "detail" and not path.exists():
        # Earlier confirmed sets have the original and the exact crop coordinates.
        sample = samples[index - 1]
        original, _ = archive_image(root, {**request, "kind": "original"})
        photo = SimpleNamespace(payload={"station_original_jpeg": original},
                                frame_size=sample["analysis_size"], roi_quad=sample["roi_quad_at_analysis_size"])
        return native_roi_png(photo)[0], "image/png"
    if kind == "preview":
        with Image.open(path) as image:
            image.thumbnail((480, 360))
            out = BytesIO()
            image.save(out, "JPEG", quality=85)
            return out.getvalue(), "image/jpeg"
    return path.read_bytes(), "image/jpeg" if kind == "original" else "image/png"
