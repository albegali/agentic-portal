import argparse
import ipaddress
import json
import mimetypes
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from portal_server.health import health

ROOT = Path(__file__).resolve().parent.parent  # the directory holding server/ content
DEFAULT_PORT = 8765


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


def make_handler(root: Path, static: Path):
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

        def do_HEAD(self):
            self.do_GET()

        def do_GET(self):
            path = self.path.split("?", 1)[0].split("#", 1)[0]
            if path == "/api/health":
                body = json.dumps(health(root)).encode()
                return self._send(200, body, "application/json")
            if path.startswith("/api/"):
                return self._send(404, b'{"error":{"code":"not_found"}}', "application/json")
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


def create_server(host="127.0.0.1", port=DEFAULT_PORT, root: Path = ROOT, static: Path | None = None):
    if not is_loopback(host):
        raise ValueError("refusing non-loopback host %r: the portal binds to loopback only" % host)
    if host == "localhost":
        host = "127.0.0.1"
    return ThreadingHTTPServer((host, port), make_handler(root, static or find_static(root)))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="portal_server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    try:
        server = create_server(args.host, args.port)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print("agentic-portal listening on http://%s:%d" % server.server_address[:2], flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
