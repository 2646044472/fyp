"""Explicit local safetensors checkpoint I/O; no bundled or downloaded assets."""
import hashlib
import os
from pathlib import Path
import tempfile
import torch
from safetensors.torch import load, save_file
from private_paths import outside_git

_LIMIT = 256 << 20


def load_exact(module, path, digest=None):
    """Load a caller-provided local model only; never deserialize pickle."""
    path = Path(path)
    if path.suffix.casefold() != ".safetensors" or not path.is_file():
        raise ValueError("expected a local .safetensors checkpoint")
    with path.open("rb") as f:
        contents = f.read(_LIMIT + 1)
    if not 0 < len(contents) <= _LIMIT:
        raise ValueError("checkpoint outside byte limit")
    if digest is not None and hashlib.sha256(contents).hexdigest() != digest:
        raise ValueError("checkpoint digest mismatch")
    state = load(contents)
    expected = module.state_dict()
    if set(state) != set(expected):
        raise ValueError("checkpoint parameter keys differ")
    if any(state[k].shape != v.shape or state[k].dtype != v.dtype
           or not torch.isfinite(state[k]).all() for k, v in expected.items()):
        raise ValueError("checkpoint parameter shape, dtype or values are invalid")
    module.load_state_dict(state, strict=True)
    return module


def save_terminal(module, path):
    """Atomic no-overwrite publication strictly OUTSIDE the project source tree."""
    p = Path(path)
    p = p.parent.resolve(strict=True) / p.name
    if not outside_git(p) or p.suffix.casefold() != ".safetensors" or p.exists() or p.is_symlink():
        raise ValueError("select a new .safetensors path outside this source tree")
    state = {k: v.detach().cpu().contiguous().clone() for k, v in module.state_dict().items()}
    if any(not torch.isfinite(x).all() for x in state.values()):
        raise ValueError("nonfinite model state")
    fd, token = tempfile.mkstemp(prefix=".fyp-local-fit-", suffix=".safetensors", dir=p.parent)
    os.close(fd)
    tmp = Path(token)
    try:
        save_file(state, str(tmp), metadata={"artifact": "local encoder weights; do not publish"})
        tmp.chmod(0o600)
        with tmp.open("rb") as f:
            os.fsync(f.fileno())
            data = f.read(_LIMIT + 1)
        roundtrip = load(data)
        if set(roundtrip) != set(state) or any(not torch.equal(state[k], roundtrip[k]) for k in state):
            raise ValueError("checkpoint readback differs")
        os.link(tmp, p, follow_symlinks=False)
        dirfd = os.open(p.parent, os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        tmp.unlink(missing_ok=True)
