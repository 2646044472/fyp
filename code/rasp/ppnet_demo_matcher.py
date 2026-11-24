from runtime_diagnostics import stage
"""Opt-in PPNet demonstration matcher using the frozen Axon score contract."""
from pathlib import Path
import hashlib
import json
import re
import sqlite3

import numpy as np
from PIL import Image

from ppnet_pilot import PPNetPilot


class PPNetDemoMatcher:
    name = "PPNet-Tongji-600-Nearest-experimental"
    default_threshold = 3.3476388454437256
    default_min_margin = 0.30556511878967285
    requires_isolated_demo_runtime = True

    def __init__(self, model_root, *, encoder=None):
        if encoder is None:
            root = Path(model_root)
            metadata = json.loads((root / 'metadata.json').read_text(encoding='utf-8'))
            expected = {
                'source_sha256': 'e83d6905bb0ca22fd202923e6b114324ddb41d90865c96a6685d0feb1f2be6b7',
                'checkpoint_sha256': 'c542c9daf893ac7cacee01402b39a12367bb137313f9d7c8825287263f0d21bb',
            }
            if any(metadata.get(k) != v for k, v in expected.items()):
                raise ValueError('PPNet export does not match the frozen Axon source and checkpoint')
            digest = hashlib.sha256((root / 'ppnet-tongji.onnx').read_bytes()).hexdigest()
            if digest != metadata.get('onnx_sha256'):
                raise ValueError('PPNet ONNX hash does not match its metadata')
            encoder = PPNetPilot(root)
            self.runtime_identity = {
                'matcher': self.name,
                'source_sha256': expected['source_sha256'],
                'checkpoint_sha256': expected['checkpoint_sha256'],
                'onnx_sha256': digest,
                'feature_contract': 'gray-bilinear-128-zero-mask-sample-std-1e-6-raw-512-v1',
                'score_contract': 'raw-512-five-template-min-l2-v1',
                'threshold': self.default_threshold,
                'min_margin': self.default_min_margin,
            }
        else:
            self.runtime_identity = None
        self.encoder = encoder

    @staticmethod
    def _vector(feature):
        vector = np.asarray(feature, dtype=np.float32)
        if vector.shape != (512,) or not np.isfinite(vector).all():
            raise ValueError("PPNet feature must be a finite 512-vector")
        return vector

    @stage
    def extract(self, roi):
        image = roi if isinstance(roi, Image.Image) else Image.fromarray(np.asarray(roi))
        raw, _ = self.encoder.extract(image)
        return self._vector(raw)

    @stage
    def score_enrollment(self, probe, features):
        probe = self._vector(probe)
        gallery = self.prepare_enrollment(features)
        return float(np.linalg.norm(gallery - probe, axis=1).min())

    def prepare_probe(self, probe):
        return self._vector(probe)

    def prepare_enrollment(self, features):
        gallery = np.asarray(features, dtype=np.float32)
        if gallery.shape != (5, 512) or not np.isfinite(gallery).all():
            raise ValueError("PPNet enrollment requires five finite 512-vectors")
        return gallery

    def prepared_bytes(self, gallery):
        return gallery.nbytes

    def score_prepared(self, probe, gallery):
        return float(np.linalg.norm(gallery - probe, axis=1).min())


def _runtime_path(base, namespace):
    base = Path(base)
    if not re.fullmatch(r"ppnet-demo-[A-Za-z0-9_-]+", namespace or ""):
        raise ValueError("PPNet requires a namespace named ppnet-demo-...")
    if (base / "demo_acceptance_policy.json").exists():
        raise ValueError("PPNet cannot use the existing demo acceptance policy")
    root = base.resolve()
    path = base / namespace
    if path.is_symlink() or path.resolve().parent != root:
        raise ValueError("PPNet namespace must be a direct, non-symlink child of runtime")
    return base, path


def create_demo_runtime(base, namespace, *, runtime_identity=None):
    """Create a fresh dedicated namespace; never open an existing demo store."""
    _base, path = _runtime_path(base, namespace)
    path.mkdir(exist_ok=False)
    marker = {"format_version": 1, "namespace": namespace,
              "runtime_identity": runtime_identity}
    temporary = path / ".ppnet-demo-runtime.tmp"
    temporary.write_text(json.dumps(marker, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path / ".ppnet-demo-runtime")
    return path


def open_demo_runtime(base, namespace, *, runtime_identity):
    """Open only a previously marked PPNet runtime with the identical model contract."""
    identity_fields = {
        'matcher', 'source_sha256', 'checkpoint_sha256', 'onnx_sha256',
        'feature_contract', 'score_contract', 'threshold', 'min_margin',
    }
    if not isinstance(runtime_identity, dict) or set(runtime_identity) != identity_fields:
        raise ValueError("PPNet namespace recovery requires a verified model identity")
    _base, path = _runtime_path(base, namespace)
    marker_path = path / ".ppnet-demo-runtime"
    if not path.is_dir() or marker_path.is_symlink() or not marker_path.is_file():
        raise ValueError("PPNet recovery requires an existing isolated runtime marker")
    if marker_path.stat().st_nlink > 1:
        raise ValueError("PPNet runtime marker cannot be hard-linked")
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("PPNet runtime marker is invalid or legacy") from error
    if (marker != {"format_version": 1, "namespace": namespace,
                   "runtime_identity": runtime_identity}):
        raise ValueError("PPNet runtime model/score identity does not match")
    if (path / "demo_acceptance_policy.json").exists():
        raise ValueError("PPNet namespace recovery rejects acceptance policies")

    template_root = path / "demo_templates"
    if template_root.is_symlink():
        raise ValueError("PPNet template directory cannot be a symlink")
    feature_ids: set[str] = set()
    if template_root.exists():
        if not template_root.is_dir():
            raise ValueError("PPNet template path must be a directory")
        files = list(template_root.iterdir())
        if any(item.is_symlink() for item in files):
            raise ValueError("PPNet template files cannot be symlinks")
        if any(item.is_file() and item.stat().st_nlink > 1 for item in files):
            raise ValueError("PPNet template files cannot be hard-linked")
        from templates import TemplateStore
        store = TemplateStore(template_root)
        for item in files:
            if item.is_file() and item.name.startswith('.template-') and item.name.endswith('.tmp'):
                continue  # Abandoned temporary archive after process interruption.
            if not item.is_file() or not (item.name.endswith('.npz') or item.name.endswith('.json')):
                raise ValueError("PPNet namespace contains unexpected template files")
            if item.name.endswith('.union2.npz'):
                raise ValueError("PPNet namespace contains incompatible template files")
        for user_id in store.list_template_ids():
            if not store.exists(user_id):
                raise ValueError("PPNet namespace contains incomplete template files")
            features, metadata = store.load(user_id)
            if (metadata.get("algorithm") != runtime_identity["matcher"]
                    or not isinstance(metadata.get("capture_profile"), str)
                    or not metadata["capture_profile"]
                    or not isinstance(metadata.get("roi_geometry"), str)
                    or not metadata["roi_geometry"]
                    or metadata.get("matcher_runtime_identity") != runtime_identity):
                raise ValueError("PPNet namespace contains a template for another matcher")
            if features.shape != (5, 512) or not np.isfinite(features).all():
                raise ValueError("PPNet namespace contains an invalid feature template")
            feature_ids.add(user_id)

    db_path = path / "demo_payment.sqlite3"
    for candidate in (db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")):
        if candidate.is_symlink():
            raise ValueError("PPNet database files cannot be symlinks")
        if candidate.exists() and candidate.stat().st_nlink > 1:
            raise ValueError("PPNet database files cannot be hard-linked")
    if db_path.exists():
        if not db_path.is_file():
            raise ValueError("PPNet database path must be a file")
        connection = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
        try:
            tables = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            if not {"users", "accounts", "transactions"}.issubset(tables):
                raise ValueError("PPNet runtime database schema is incomplete")
            user_ids = {row[0] for row in connection.execute("SELECT user_id FROM users")}
            account_ids = {row[0] for row in connection.execute("SELECT user_id FROM accounts")}
        except sqlite3.DatabaseError as error:
            raise ValueError("PPNet runtime database is invalid") from error
        finally:
            connection.close()
        if user_ids != account_ids or user_ids != feature_ids:
            raise ValueError("PPNet accounts and templates are incomplete or inconsistent")
    elif feature_ids:
        raise ValueError("PPNet templates exist without their payment database")
    return path
