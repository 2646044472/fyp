"""Keep local FIT archives and trained artifacts out of source checkouts."""
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]


def outside_git(path):
    path = Path(path).resolve()
    if path.is_relative_to(PROJECT):
        return False
    for parent in (path, *path.parents):
        marker = parent / ".git"
        # A linked worktree has a .git *file*. A normal checkout has a
        # .git/HEAD. An empty directory named ".git" alone is not a checkout.
        if marker.is_file() or (marker / "HEAD").is_file():
            return False
    return True
