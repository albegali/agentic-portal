import argparse
import ipaddress
import json
import mimetypes
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from portal_server.contract.gate import COMPATIBLE, bind, gate_for
from portal_server.health import health
from portal_server.http.auth import check_request, is_api
from portal_server.http.token import launch_url, resolve_token

ROOT = Path(__file__).resolve().parent.parent  # the directory holding server/ content
DEFAULT_PORT = 8765

# (method, path) -> callable(root) -> JSON-serialisable body. Every entry except the
# public ones in http.auth goes through the token check; the enumeration test reads this.
# A route may return (status, body) instead of a body. While the skeleton is not compatible every route except
# CONTRACT_EXEMPT answers 409 contract_incompatible (ADR-002 revision 2026-10-20).
API_ROUTES = {
    ("GET", "/api/health"): lambda root: health(root, gate_for(root)),
    ("GET", "/api/contract"): lambda root: gate_for(root).snapshot(),
    ("POST", "/api/contract/recheck"): lambda root: gate_for(root).refresh(),
}
CONTRACT_EXEMPT = {"/api/health", "/api/contract", "/api/contract/recheck"}


def is_loopback(host: str) -> bool:
    """True only if every address the host resolves to is loopback."""
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError:
        return False
    return bool(infos) and all(
        ipaddress.ip_address(i[4][0].split("%")[0]).is_loopback for i in infos
    )


def find_static(root: Path) -> Path:
    for candidate in (root / "web" / "dist", root.parent / "web" / "dist"):
        if candidate.is_dir():
            return candidate.resolve()
    return (root.parent / "web" / "dist").resolve()


def make_handler(root: Path, static: Path, token: str, routes=None):
    routes = API_ROUTES if routes is None else routes

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send(self, code, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _guard(self, path):
            denied = check_request(self.command, path, self.headers, self.server.server_address[1], token)
            if denied is None:
                return True
            sys.stderr.write("portal: %s %s denied: %s\n" % (self.command, path, denied.reason))
            sys.stderr.flush()
            body = json.dumps({"error": {"code": denied.code, "message": denied.reason}}).encode()
            self._send(denied.status, body, "application/json")
            return False

        def _api(self, path):
            route = routes.get(("GET" if self.command == "HEAD" else self.command, path))
            if route is None:
                return self._send(404, b'{"error":{"code":"not_found"}}', "application/json")
            if path not in CONTRACT_EXEMPT:
                snap = gate_for(root).snapshot()
                if snap["state"] != COMPATIBLE:
                    error = {"code": "contract_incompatible", "message": snap["message"], "recovery": snap["recovery"]}
                    return self._send(409, json.dumps({"error": error}).encode(), "application/json")
            result = route(root)
            status, body = result if isinstance(result, tuple) else (200, result)
            self._send(status, json.dumps(body).encode(), "application/json")

        def _other(self):
            path = self.path.split("?", 1)[0].split("#", 1)[0]
            if self._guard(path):
                if is_api(path):
                    return self._api(path)
                self._send(405, b"method not allowed", "text/plain; charset=utf-8")

        do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = _other

        def do_HEAD(self):
            self.do_GET()

        def do_GET(self):
            path = self.path.split("?", 1)[0].split("#", 1)[0]
            if not self._guard(path):
                return
            if is_api(path):
                return self._api(path)
            rel = path.lstrip("/") or "index.html"
            target = (static / rel).resolve()
            if not target.is_relative_to(static) or not target.is_file():
                target = static / "index.html"
            if not target.is_file():
                return self._send(404, b"web/dist not built", "text/plain; charset=utf-8")
            ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
                ctype += "; charset=utf-8"
            self._send(200, target.read_bytes(), ctype)

    return Handler


def create_server(host="127.0.0.1", port=DEFAULT_PORT, root: Path = ROOT, static: Path | None = None,
                  token: str = "", routes=None, repo: Path | None = None):
    if not is_loopback(host):
        raise ValueError("refusing non-loopback host %r: the portal binds to loopback only" % host)
    if host == "localhost":
        host = "127.0.0.1"
    bind(root, repo)  # reads the skeleton version once at start
    return ThreadingHTTPServer((host, port), make_handler(root, static or find_static(root), token, routes))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="portal_server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--repo", type=Path, default=None, help="workflow repository root (default: working directory)")
    args = parser.parse_args(argv)
    token, generated = resolve_token()
    try:
        server = create_server(args.host, args.port, token=token, repo=(args.repo or Path.cwd()).resolve())
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print("agentic-portal listening on http://%s:%d" % server.server_address[:2], flush=True)
    if generated:
        print("open %s" % launch_url(*server.server_address[:2], token), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
