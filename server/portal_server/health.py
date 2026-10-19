from datetime import datetime, timezone
from pathlib import Path

UNKNOWN = "unknown"


def read_version(root: Path) -> str:
    for candidate in (root / "VERSION", root.parent / "VERSION"):
        try:
            return candidate.read_text(encoding="utf-8").strip() or UNKNOWN
        except OSError:
            continue
    return UNKNOWN


def health(root: Path) -> dict:
    try:
        return {
            "status": "ok",
            "datetime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "portal_version": read_version(root),
            "contract_version": UNKNOWN,
            "skeleton_version": UNKNOWN,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": {"code": "health_failed", "message": str(exc)}}
