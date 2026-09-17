"""Small local file store for Fast-CC template features.

Only feature arrays and non-sensitive metadata belong here. Camera captures and
debug images should stay in the ignored runtime/data directories.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np


_USER_ID = re.compile(r"^[A-Za-z0-9_-]+$")


class TemplateStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_user_id(user_id: str) -> str:
        if not isinstance(user_id, str) or not _USER_ID.fullmatch(user_id):
            raise ValueError("user_id must contain only letters, numbers, '-' or '_'")
        return user_id

    def _paths(self, user_id: str) -> tuple[Path, Path]:
        safe_id = self._validate_user_id(user_id)
        return self.root / f"{safe_id}.npz", self.root / f"{safe_id}.json"

    def save(self, user_id: str, features: np.ndarray, metadata: dict[str, Any]) -> None:
        data_path, metadata_path = self._paths(user_id)
        array = np.asarray(features)
        if array.size == 0 or array.ndim == 0:
            raise ValueError("at least one template feature is required")
        np.savez_compressed(data_path, features=array)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    def load(self, user_id: str) -> tuple[np.ndarray, dict[str, Any]]:
        data_path, metadata_path = self._paths(user_id)
        if not data_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(f"template files for {user_id!r} are incomplete or missing")
        with np.load(data_path, allow_pickle=False) as archive:
            if "features" not in archive:
                raise ValueError(f"template file for {user_id!r} has no 'features' array")
            features = np.asarray(archive["features"])
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError(f"metadata for {user_id!r} must be a JSON object")
        return features, metadata

    def list_users(self) -> list[str]:
        users: list[str] = []
        for data_path in sorted(self.root.glob("*.npz")):
            user_id = data_path.stem
            if (self.root / f"{user_id}.json").exists():
                users.append(user_id)
        return users

    def load_all(self) -> dict[str, tuple[np.ndarray, dict[str, Any]]]:
        return {user_id: self.load(user_id) for user_id in self.list_users()}

    def exists(self, user_id: str) -> bool:
        data_path, metadata_path = self._paths(user_id)
        return data_path.exists() and metadata_path.exists()

    def delete(self, user_id: str) -> None:
        data_path, metadata_path = self._paths(user_id)
        data_path.unlink(missing_ok=True)
        metadata_path.unlink(missing_ok=True)
