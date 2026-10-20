from datetime import datetime, timezone
from pathlib import Path

from portal_server.contract import CONTRACT_BUILT_FOR

UNKNOWN = "unknown"


def read_version(root: Path) -> str:
    for candidate in (root / "VERSION", root.parent / "VERSION"):
        try:
            return candidate.read_text(encoding="utf-8").strip() or UNKNOWN
        except OSError:
            continue
    return UNKNOWN


def health(root: Path, gate=None) -> dict:
    try:
        snap = gate.snapshot() if gate else {}
        return {
            "status": "ok",
            "datetime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "portal_version": read_version(root),
            "contract_version": snap.get("contract_version") or UNKNOWN,
            "skeleton_version": snap.get("skeleton_version") or UNKNOWN,
            "contract": {"built_for": CONTRACT_BUILT_FOR, "skeleton_contract": snap.get("contract_version") or UNKNOWN},
            "skeleton": snap.get("skeleton_version") or UNKNOWN,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": {"code": "health_failed", "message": str(exc)}}
