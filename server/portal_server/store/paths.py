import os
from pathlib import Path

PORTAL_STATE = ".portal"


class OutsideRoot(ValueError):
    pass


def _key(path: Path) -> str:
    return os.path.normcase(str(path))


def safe_path(root: Path, rel) -> Path:
    """Resolve `rel` under `root`; raise OutsideRoot on traversal, absolute or symlink escape."""
    rel = os.fspath(rel)
    if not rel or "\0" in rel:
        raise OutsideRoot("invalid path")
    if os.path.isabs(rel) or Path(rel).is_absolute() or Path(rel).drive or rel[1:2] == ":" or rel.startswith(("/", "\\")):
        raise OutsideRoot("absolute paths are not allowed")
    base = Path(root).resolve()
    target = (base / rel).resolve()
    base_key, target_key = _key(base), _key(target)
    if target_key != base_key and not target_key.startswith(base_key.rstrip(os.sep) + os.sep):
        raise OutsideRoot("path escapes the repository root")
    return target


def write_guard(root: Path, rel) -> Path:
    """Path a write may use: inside the repo root (`.portal/` is portal-owned state, also allowed)."""
    return safe_path(root, rel)
