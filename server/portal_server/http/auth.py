from typing import NamedTuple

from portal_server.http.token import tokens_match

STATE_CHANGING = frozenset({"POST", "PUT", "PATCH", "DELETE"})
# Documented exception to NFR-02 (ADR-006 revision): no repository data, Host-checked.
PUBLIC_ROUTES = frozenset({("GET", "/api/health"), ("HEAD", "/api/health")})


class Denied(NamedTuple):
    status: int
    code: str
    reason: str


def is_api(path: str) -> bool:
    return path == "/api" or path.startswith("/api/")


def allowed_hosts(port: int) -> frozenset:
    return frozenset({"127.0.0.1:%d" % port, "localhost:%d" % port})


def check_request(method: str, path: str, headers, port: int, token: str):
    """Host → token → Origin/content type. Returns None when allowed, else Denied."""
    hosts = allowed_hosts(port)
    if headers.get("Host", "").lower() not in hosts:
        return Denied(403, "bad_host", "host not allowed")
    if not is_api(path):
        return None
    if (method, path) not in PUBLIC_ROUTES:
        auth = headers.get("Authorization", "")
        scheme, _, given = auth.partition(" ")
        if scheme.lower() != "bearer" or not given:
            return Denied(401, "unauthorized", "missing token")
        if not tokens_match(given.strip(), token):
            return Denied(401, "unauthorized", "invalid token")
    if method in STATE_CHANGING:
        origin = headers.get("Origin", "")
        if origin.lower() not in {"http://" + h for h in hosts}:
            return Denied(403, "bad_origin", "origin not allowed")
        ctype = headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if ctype != "application/json":
            return Denied(403, "bad_content_type", "content type must be application/json")
    return None
