from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


def safe_user_id(user_id: str) -> str:
    safe = "".join(char for char in str(user_id) if char.isalnum() or char in "-_")
    if not safe:
        raise ValueError("user must contain a letter or number")
    return safe


class TemplateStore:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path(__file__).resolve().parent / "runtime" / "templates"

    def paths(self, user_id: str) -> tuple[Path, Path]:
        safe = safe_user_id(user_id)
        return self.root / f"{safe}.npz", self.root / f"{safe}.json"

    def exists(self, user_id: str) -> bool:
        data_path, meta_path = self.paths(user_id)
        return data_path.exists() and meta_path.exists()

    def save(self, user_id: str, features: np.ndarray, metadata: dict[str, Any]) -> None:
        data_path, meta_path = self.paths(user_id)
        self.root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=self.root, suffix=".npz", delete=False) as data_file:
            temp_data = Path(data_file.name)
        temp_meta = Path(tempfile.mktemp(dir=self.root, suffix=".json"))
        try:
            np.savez_compressed(temp_data, features=np.asarray(features))
            temp_meta.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
            os.replace(temp_data, data_path)
            os.replace(temp_meta, meta_path)
        finally:
            temp_data.unlink(missing_ok=True)
            temp_meta.unlink(missing_ok=True)

    def load(self, user_id: str) -> tuple[np.ndarray, dict[str, Any]]:
        data_path, meta_path = self.paths(user_id)
        if not data_path.exists() or not meta_path.exists():
            raise FileNotFoundError(f"No complete template for {user_id}")
        with np.load(data_path, allow_pickle=False) as archive:
            features = np.asarray(archive["features"])
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        return features, metadata

    def list_users(self) -> list[str]:
        if not self.root.exists():
            return []
        users = []
        for data_path in self.root.glob("*.npz"):
            if data_path.with_suffix(".json").exists():
                users.append(data_path.stem)
        return sorted(users)

    def delete(self, user_id: str) -> None:
        data_path, meta_path = self.paths(user_id)
        data_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)
