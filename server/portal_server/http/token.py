import hmac
import os
import secrets
import stat
from pathlib import Path

TOKEN_ENV = "PORTAL_TOKEN"
TOKEN_FILE = Path(".portal") / "token"


def resolve_token(env=None):
    """Return (token, generated): PORTAL_TOKEN if set, else a fresh 256-bit token."""
    env = os.environ if env is None else env
    token = env.get(TOKEN_ENV, "").strip()
    if token:
        return token, False
    return secrets.token_urlsafe(32), True


def read_token_file(root: Path):
    """Token of a running portal from the user-only `.portal/` file, or None.

    Refused when the file is readable by group or others (POSIX); on Windows the
    file is restricted by the writer (AP0110) and cannot be checked from here.
    """
    path = Path(root) / TOKEN_FILE
    try:
        if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) & 0o077:
            return None
        return path.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def launch_url(host: str, port: int, token: str) -> str:
    return "http://%s:%d/#token=%s" % (host, port, token)


def tokens_match(given: str, expected: str) -> bool:
    return hmac.compare_digest(given.encode(), expected.encode())
