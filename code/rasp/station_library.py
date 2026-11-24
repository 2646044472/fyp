"""Browse and move confirmed photos to local trash, using stable sample numbers."""
from datetime import datetime
from io import BytesIO
import json
import os
import re
import tempfile
from types import SimpleNamespace

from PIL import Image

from enrollment_archive import native_roi_png, sync_directory

IMAGE_SUFFIXES = {"original": "original.jpg", "model": "roi.png", "detail": "roi-native.png"}
PREVIEW_KINDS = {"preview": "original", "detail-preview": "detail"}


class ArchiveEditError(ValueError):
    """A participant metadata edit the user can correct on the station."""


def valid_id(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{32}", value)


def read_manifest(folder):
    manifest = folder / "manifest.json"
    if folder.is_symlink() or manifest.is_symlink():
        raise ValueError("无效归档。")
    return json.loads(manifest.read_text("utf-8"))


def deleted_sample(folder, index):
    return folder / ".deleted" / f"{index:02d}"


def archive_timestamp(data, stat):
    return data.get("saved_at") or datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat()


def list_archives(root):
    archives = []
    if not root.exists():
        return archives
    for folder in root.iterdir():
        if not valid_id(folder.name) or folder.is_symlink() or not folder.is_dir():
            continue
        data = read_manifest(folder)
        samples = [dict(index=i, size=s["analysis_size"], quad=s["roi_quad_at_analysis_size"])
                   for i, s in enumerate(data["samples"], 1) if not deleted_sample(folder, i).exists()]
        if not samples:
            continue
        stat = (folder / "manifest.json").stat()
        archives.append(dict(id=folder.name, participant=data["participant_code"], hand=data["hand"],
                             display_name=data.get("display_name") or data["participant_code"],
                             saved=archive_timestamp(data, stat), revision=str(stat.st_mtime_ns),
                             samples=samples))
    return sorted(archives, key=lambda item: item["saved"], reverse=True)


def archive_image(root, request):
    archive, index, kind = (request.get(k) for k in ("archive", "index", "kind"))
    if not valid_id(archive) or type(index) is not int or index < 1 or not isinstance(kind, str):
        raise ValueError("无效归档照片。")
    folder = root / archive
    samples = read_manifest(folder)["samples"]
    source_kind = PREVIEW_KINDS.get(kind, kind)
    if index > len(samples) or source_kind not in IMAGE_SUFFIXES:
        raise ValueError("无效归档照片。")
    if deleted_sample(folder, index).exists():
        raise FileNotFoundError("照片已移出照片库。")
    suffix = IMAGE_SUFFIXES[source_kind]
    path = folder / f"{index:02d}-{suffix}"
    if path.is_symlink():
        raise ValueError("无效归档文件。")
    source = path
    if source_kind == "detail" and not path.exists():
        # Earlier confirmed sets have the original and the exact crop coordinates.
        sample = samples[index - 1]
        original, _ = archive_image(root, {**request, "kind": "original"})
        photo = SimpleNamespace(payload={"station_original_jpeg": original},
                                frame_size=sample["analysis_size"], roi_quad=sample["roi_quad_at_analysis_size"])
        data, _ = native_roi_png(photo)
        if kind == "detail":
            return data, "image/png"
        source = BytesIO(data)
    if kind in PREVIEW_KINDS:
        with Image.open(source) as image:
            image.thumbnail((480, 360))
            out = BytesIO()
            image.save(out, "JPEG", quality=85)
            return out.getvalue(), "image/jpeg"
    return path.read_bytes(), "image/jpeg" if kind == "original" else "image/png"


def edit_archive(root, request):
    archive, participant, name, hand = (request.get(key) for key in ("archive", "participant", "display_name", "hand"))
    if not valid_id(archive):
        raise ArchiveEditError("这条照片记录无效，请刷新照片库。")
    if not isinstance(participant, str):
        raise ArchiveEditError("请输入参与者编号。")
    participant = participant.strip()
    if not 1 <= len(participant) <= 40 or not all(char.isalnum() or char in "-_" for char in participant):
        raise ArchiveEditError("编号需要 1–40 个字母、数字、汉字、短横线或下划线。")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 60 or not name.strip().isprintable():
        raise ArchiveEditError("请输入 1–60 个可显示字符作为显示名。")
    if hand not in ("left", "right"):
        raise ArchiveEditError("请选择左手或右手。")

    folder = root / archive
    manifest = folder / "manifest.json"
    data = read_manifest(folder)
    stat = manifest.stat()
    if request.get("revision") != str(stat.st_mtime_ns):
        raise ArchiveEditError("这条记录刚被修改。请刷新照片库后再编辑。")
    data.update(participant_code=participant, display_name=name.strip(), hand=hand,
                saved_at=archive_timestamp(data, stat))
    fd, path = tempfile.mkstemp(prefix=".metadata-", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, allow_nan=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(path, manifest)
        sync_directory(folder)
    finally:
        if os.path.exists(path):
            os.unlink(path)
    return {"archive": archive}


def delete_archive(root, request):
    """Move a saved set or one numbered exposure without renumbering its neighbors."""
    archive = request.get("archive")
    index = request.get("index")
    if not valid_id(archive) or ("index" in request and (type(index) is not int or index < 1)):
        raise ValueError("无效归档照片。")
    folder = root / archive
    trash = root / ".trash"
    removed = trash / archive
    if not folder.exists() and removed.is_dir() and not trash.is_symlink():
        return {"remaining": 0}
    data = read_manifest(folder)
    if index is not None:
        if index > len(data["samples"]):
            raise ValueError("无效归档照片。")
        slot = deleted_sample(folder, index)
        if slot.parent.is_symlink() or slot.is_symlink():
            raise ValueError("无效回收目录。")
        slot.parent.mkdir(mode=0o700, exist_ok=True)
        slot.mkdir(mode=0o700, exist_ok=True)
        # Publish the tombstone before moving bytes. A retry can finish a
        # partial move, and neither the browser nor validation can see it again.
        sync_directory(folder)
        sync_directory(slot.parent)
        for suffix in IMAGE_SUFFIXES.values():
            name = f"{index:02d}-{suffix}"
            source = folder / name
            if source.exists():
                os.replace(source, slot / name)
        sync_directory(slot)
        sync_directory(folder)
        remaining = sum(not deleted_sample(folder, i).exists() for i in range(1, len(data["samples"]) + 1))
        if remaining:
            return {"remaining": remaining}
    if trash.is_symlink():
        raise ValueError("无效回收目录。")
    trash.mkdir(mode=0o700, exist_ok=True)
    os.replace(folder, removed)
    sync_directory(trash)
    sync_directory(root)
    return {"remaining": 0}
