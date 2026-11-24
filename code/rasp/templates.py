from __future__ import annotations

import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import numpy as np


def safe_user_id(user_id: str) -> str:
    safe = "".join(char for char in str(user_id) if char.isalnum() or char in "-_")
    if not safe:
        raise ValueError("user must contain a letter or number")
    return safe


class TemplateStore:
    def __init__(self, root: str | Path | None = None, *, compression_level: int | None = None) -> None:
        if compression_level is not None and (type(compression_level) is not int or not 1 <= compression_level <= 9):
            raise ValueError('Template compression level must be an integer from 1 to 9')
        self.compression_level = compression_level
        self.root = Path(root) if root is not None else Path(__file__).resolve().parent / "runtime" / "templates"

    def _legacy_paths(self, user_id: str) -> tuple[Path, Path]:
        safe = safe_user_id(user_id)
        return self.root / f"{safe}.npz", self.root / f"{safe}.json"

    def _atomic_path(self, user_id: str) -> Path:
        return self.root / f"{safe_user_id(user_id)}.atomic.npz"

    def paths(self, user_id: str) -> tuple[Path, ...]:
        new = self._atomic_path(user_id)
        legacy = self._legacy_paths(user_id)
        union = self.root / f"{safe_user_id(user_id)}.union2.npz"
        if union.exists():
            raise ValueError("Incompatible union template; use an isolated root")
        if new.exists() and any(p.exists() for p in legacy) and not all(p.is_file() for p in legacy):
            raise ValueError("Incomplete historical template")
        return (new,) if new.exists() else legacy

    def exists(self, user_id: str) -> bool:
        return all(p.is_file() for p in self.paths(user_id))

    def save(self, user_id: str, features: np.ndarray, metadata: dict[str, Any]) -> None:
        new = self._atomic_path(user_id)
        legacy = self._legacy_paths(user_id)
        if (self.root / f"{safe_user_id(user_id)}.union2.npz").exists():
            raise ValueError("Incompatible union template; use an isolated root")
        if new.exists():
            self.load(user_id)  # Refuse to overwrite a damaged or unknown archive.
        elif any(p.exists() for p in legacy):
            if not all(p.is_file() for p in legacy):
                raise ValueError("Incomplete legacy template")
            self.load(user_id)
        raw = json.dumps(metadata, sort_keys=True, allow_nan=False).encode('utf-8')
        if len(raw) > 1024 * 1024:
            raise ValueError('Template metadata too large')
        if not isinstance(metadata, dict):
            raise ValueError("Invalid template metadata")
        self.root.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(dir=self.root, prefix='.template-', suffix='.tmp')
        temp = Path(temp_name)
        try:
            with os.fdopen(fd, 'w+b') as stream:
                with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED,
                                     compresslevel=self.compression_level) as archive:
                    for name, array in (('features.npy', np.asarray(features)),
                                        ('metadata.npy', np.frombuffer(raw, dtype=np.uint8))):
                        with archive.open(name, 'w', force_zip64=True) as target:
                            np.lib.format.write_array(target, array, allow_pickle=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, new)
            if os.name != 'nt':
                directory = os.open(self.root, os.O_RDONLY)
                try: os.fsync(directory)
                finally: os.close(directory)
        finally:
            temp.unlink(missing_ok=True)

    def load(self, user_id: str) -> tuple[np.ndarray, dict[str, Any]]:
        paths = self.paths(user_id)
        if len(paths) == 1:
            with zipfile.ZipFile(paths[0]) as archive:
                infos = archive.infolist()
                if (len(infos) != 2 or {i.filename for i in infos} != {'features.npy', 'metadata.npy'}
                        or archive.getinfo('metadata.npy').file_size > 1024 * 1024 + 4096):
                    raise ValueError('Invalid atomic template members')
                with archive.open('features.npy') as stream:
                    features = np.lib.format.read_array(stream, allow_pickle=False)
                with archive.open('metadata.npy') as stream:
                    raw = np.lib.format.read_array(stream, allow_pickle=False)
                if raw.dtype != np.uint8 or raw.ndim != 1 or raw.size > 1024 * 1024:
                    raise ValueError("Invalid atomic metadata")
                metadata = json.loads(raw.tobytes().decode('utf-8'))
        else:
            data_path, meta_path = paths
            if not data_path.is_file() or not meta_path.is_file():
                raise FileNotFoundError(f"No complete template for {user_id}")
            with np.load(data_path, allow_pickle=False) as archive:
                features = np.asarray(archive["features"])
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError("Invalid template metadata")
        return features, metadata

    def read_metadata(self, user_id: str) -> dict[str, Any]:
        paths = self.paths(user_id)
        if len(paths) == 1:
            with zipfile.ZipFile(paths[0]) as archive:
                infos = archive.infolist()
                if (len(infos) != 2 or {i.filename for i in infos} != {'features.npy', 'metadata.npy'}
                        or archive.getinfo('metadata.npy').file_size > 1024 * 1024 + 4096):
                    raise ValueError('Invalid atomic template members')
                with archive.open('metadata.npy') as stream:
                    raw = np.lib.format.read_array(stream, allow_pickle=False)
                if raw.dtype != np.uint8 or raw.ndim != 1 or raw.size > 1024 * 1024:
                    raise ValueError('Invalid atomic metadata')
                metadata = json.loads(raw.tobytes().decode('utf-8'))
        else:
            data_path, meta_path = paths
            if not data_path.is_file() or not meta_path.is_file():
                raise FileNotFoundError(f"No complete template for {user_id}")
            metadata = json.loads(meta_path.read_text(encoding='utf-8'))
        if not isinstance(metadata, dict):
            raise ValueError('Invalid template metadata')
        return metadata

    def list_users(self) -> list[str]:
        return [user for user in self.list_template_ids() if self.exists(user)]

    def list_template_ids(self) -> list[str]:
        if not self.root.exists(): return []
        users = set()
        for path in self.root.glob('*.npz'):
            name = path.name
            if name.endswith('.atomic.npz'): users.add(name[:-len('.atomic.npz')])
            elif name.endswith('.union2.npz'): users.add(name[:-len('.union2.npz')])
            else: users.add(path.stem)
        users.update(path.stem for path in self.root.glob('*.json'))
        return sorted(users)

    def delete(self, user_id: str) -> None:
        # Explicit deletion removes historical files first: an interruption can
        # never expose an older generation after deleting the current archive.
        union = self.root / f"{safe_user_id(user_id)}.union2.npz"
        if union.exists():
            raise ValueError("Incompatible union template; refusing deletion")
        for path in (*self._legacy_paths(user_id), self._atomic_path(user_id)):
            path.unlink(missing_ok=True)
