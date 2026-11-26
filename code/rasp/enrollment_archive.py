"""Private, complete image-pair archives for explicitly confirmed enrollments."""
from base64 import b64decode
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4

from PIL import Image


def write_file(path, data):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def sync_directory(path):
    if os.name != "nt":
        directory = os.open(path, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)


def native_roi_png(candidate):
    """Rectify the selected quad directly from its camera JPEG at source density."""
    return rectified_roi_png(candidate, candidate.payload["station_original_jpeg"])


def rectified_roi_png(candidate, jpeg):
    import cv2
    import numpy as np

    with Image.open(BytesIO(jpeg)) as image:
        scale = np.asarray(image.size) / candidate.frame_size
        rgb = np.asarray(image.convert("RGB"))
    corners = ((np.asarray(candidate.roi_quad) + .5) * scale - .5).astype(np.float32)
    sides = np.linalg.norm(np.roll(corners, -1, axis=0) - corners, axis=1)
    width, height = (max(1, round(float(v))) for v in (sides[::2].mean(), sides[1::2].mean()))
    target = np.float32(((0, 0), (width, 0), (width, height), (0, height)))
    crop = cv2.warpPerspective(rgb, cv2.getPerspectiveTransform(corners, target), (width, height))
    out = BytesIO()
    Image.fromarray(crop).save(out, "PNG")
    return out.getvalue(), (width, height)


def save_enrollment(root, store, user_id, batch, metadata, session, *, update_template=True, include_native_roi=False):
    frame_ids = session["selected_frame_ids"]
    candidates = {candidate.frame_id: candidate for candidate in session["photo_candidates"]}
    target = session.get("station_target_count", 5)
    if len(frame_ids) != target or len(set(frame_ids)) != target or any(frame_id not in candidates for frame_id in frame_ids):
        raise ValueError("An original or ROI is missing from a photo pair. Capture it again before saving.")

    root = Path(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    archive_id = uuid4().hex
    target = root / archive_id
    temp = Path(tempfile.mkdtemp(dir=root, prefix=".enrollment-"))
    try:
        samples = []
        for index, (frame_id, selected_roi) in enumerate(zip(frame_ids, session["selected_roi_images"], strict=True), 1):
            candidate = candidates[frame_id]
            payload = candidate.payload
            jpeg = payload.get("station_original_jpeg")
            if not jpeg or not selected_roi or selected_roi != payload.get("encoded_roi"):
                raise ValueError("An original or ROI is missing from a photo pair. Capture it again before saving.")
            with Image.open(BytesIO(jpeg)) as image:
                if image.format != "JPEG":
                    raise ValueError("Could not save the original: the camera did not return a JPEG.")
                size = list(image.size)
            original_name, roi_name = f"{index:02d}-original.jpg", f"{index:02d}-roi.png"
            write_file(temp / original_name, jpeg)
            write_file(temp / roi_name, b64decode(selected_roi, validate=True))
            samples.append({"frame_id": frame_id, "original": original_name, "roi": roi_name,
                            "original_size": size, "native_camera_jpeg": payload["station_native_original"],
                            "analysis_size": list(candidate.frame_size),
                            "roi_quad_at_analysis_size": candidate.roi_quad.tolist()})
            if include_native_roi:
                detail, detail_size = native_roi_png(candidate)
                name = f"{index:02d}-roi-native.png"
                write_file(temp / name, detail)
                samples[-1].update(native_roi=name, native_roi_size=detail_size)
        manifest = {"participant_code": user_id, "display_name": metadata["display_name"],
                    "hand": session["hand"], "samples": samples}
        write_file(temp / "manifest.json", json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8"))
        sync_directory(temp)
        os.replace(temp, target)
        try:
            sync_directory(root)
            if update_template:
                store.save(user_id, batch, {**metadata, "enrollment_archive_id": archive_id})
        except Exception:
            # If save failed after the atomic replace, preserve its associated image set.
            try:
                committed = store.read_metadata(user_id).get("enrollment_archive_id") == archive_id
            except FileNotFoundError:
                committed = False
            except (ValueError, OSError):
                committed = True  # Commit outcome unknown; do not discard captured images.
            if not committed:
                shutil.rmtree(target)
            raise
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return archive_id
