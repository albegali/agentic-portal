import contextlib
import http.client
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portal_server import app  # noqa: E402
from portal_server.http import auth, token  # noqa: E402
from portal_server.store.paths import OutsideRoot, safe_path, write_guard  # noqa: E402

TOKEN = "s3cr3t-" + "x" * 36
EXTRA = {("GET", "/api/extra"): lambda root: {"ok": True}, ("POST", "/api/extra"): lambda root: {"ok": True}}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "web" / "dist").mkdir(parents=True)
        (self.root / "web" / "dist" / "index.html").write_text("<h1>hi</h1>")
        routes = {**app.API_ROUTES, **EXTRA}
        self.server = app.create_server("127.0.0.1", 0, self.root, self.root / "web" / "dist", token=TOKEN, routes=routes)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def request(self, method, path, headers=None, body=None, host=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.putrequest(method, path, skip_host=True)
        conn.putheader("Host", host or "127.0.0.1:%d" % self.port)
        for k, v in (headers or {}).items():
            conn.putheader(k, v)
        data = body.encode() if body is not None else None
        conn.putheader("Content-Length", str(len(data or b"")))
        conn.endheaders(data)
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        return resp.status, resp.getheaders(), raw

    def bearer(self, **extra):
        return dict({"Authorization": "Bearer " + TOKEN}, **extra)

    def origin(self):
        return "http://127.0.0.1:%d" % self.port


class BindTest(Base):
    def test_bound_to_loopback_only(self):
        self.assertEqual(self.server.socket.getsockname()[0], "127.0.0.1")


class TokenTest(Base):
    def test_missing_and_wrong_token_rejected_with_log_free_of_token(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            for headers in ({}, {"Authorization": "Bearer nope"}, {"Authorization": "Basic " + TOKEN}):
                status, _, raw = self.request("GET", "/api/extra", headers)
                self.assertEqual(status, 401)
                self.assertEqual(json.loads(raw)["error"]["code"], "unauthorized")
            self.request("GET", "/api/extra", {"Authorization": "Bearer wrong-value"})
        log = err.getvalue()
        self.assertIn("GET /api/extra denied", log)
        self.assertNotIn("wrong-value", log)
        self.assertNotIn(TOKEN, log)

    def test_valid_token_accepted(self):
        self.assertEqual(self.request("GET", "/api/extra", self.bearer())[0], 200)

    def test_unknown_api_path_needs_token_first(self):
        self.assertEqual(self.request("GET", "/api/nope")[0], 401)
        self.assertEqual(self.request("GET", "/api/nope", self.bearer())[0], 404)

    def test_health_is_public_but_post_is_not(self):
        self.assertEqual(self.request("GET", "/api/health")[0], 200)
        self.assertEqual(self.request("HEAD", "/api/health")[0], 200)
        self.assertEqual(self.request("POST", "/api/health")[0], 401)

    def test_route_enumeration_every_api_route_rejects_missing_and_invalid_token(self):
        routes = {**app.API_ROUTES, **EXTRA}
        protected = [r for r in routes if r not in auth.PUBLIC_ROUTES]
        self.assertTrue(protected)
        for method, path in protected:
            for headers in ({}, {"Authorization": "Bearer invalid"}):
                self.assertEqual(self.request(method, path, headers)[0], 401, (method, path))
        # the real route table: nothing besides health is public
        self.assertEqual({r for r in app.API_ROUTES if r in auth.PUBLIC_ROUTES}, {("GET", "/api/health")})

    def test_static_files_need_no_token(self):
        self.assertEqual(self.request("GET", "/")[0], 200)


class HostOriginTest(Base):
    def test_foreign_host_rejected_on_every_method_and_before_token(self):
        for method in ("GET", "HEAD", "POST", "OPTIONS"):
            for path in ("/", "/api/health", "/api/extra"):
                status, _, _ = self.request(method, path, self.bearer(), host="evil.example:%d" % self.port)
                self.assertEqual(status, 403, (method, path))
        self.assertEqual(self.request("GET", "/api/extra", host="evil.example")[0], 403)

    def test_localhost_host_accepted(self):
        self.assertEqual(self.request("GET", "/api/extra", self.bearer(), host="localhost:%d" % self.port)[0], 200)

    def test_wrong_port_in_host_rejected(self):
        self.assertEqual(self.request("GET", "/api/health", host="127.0.0.1:1")[0], 403)

    def test_state_changing_origin_and_content_type(self):
        ok = self.bearer(Origin=self.origin(), **{"Content-Type": "application/json"})
        self.assertEqual(self.request("POST", "/api/extra", ok, "{}")[0], 200)
        bad_origin = self.bearer(Origin="http://evil.example", **{"Content-Type": "application/json"})
        self.assertEqual(self.request("POST", "/api/extra", bad_origin, "{}")[0], 403)
        no_origin = self.bearer(**{"Content-Type": "application/json"})
        self.assertEqual(self.request("POST", "/api/extra", no_origin, "{}")[0], 403)
        form = self.bearer(Origin=self.origin(), **{"Content-Type": "text/plain"})
        self.assertEqual(self.request("POST", "/api/extra", form, "{}")[0], 403)

    def test_token_checked_before_origin(self):
        status, _, raw = self.request("POST", "/api/extra", {"Origin": "http://evil.example"}, "{}")
        self.assertEqual((status, json.loads(raw)["error"]["code"]), (401, "unauthorized"))

    def test_no_cors_headers(self):
        _, headers, _ = self.request("GET", "/api/health")
        self.assertFalse([k for k, _ in headers if k.lower().startswith("access-control-")])


class TokenSourceTest(unittest.TestCase):
    def test_env_token_used(self):
        self.assertEqual(token.resolve_token({"PORTAL_TOKEN": " abc "}), ("abc", False))

    def test_generated_when_unset(self):
        t1, g1 = token.resolve_token({})
        t2, _ = token.resolve_token({})
        self.assertTrue(g1)
        self.assertGreaterEqual(len(t1), 43)
        self.assertNotEqual(t1, t2)

    def test_main_prints_url_once_only_when_generated(self):
        for env, expect in (({}, True), ({"PORTAL_TOKEN": "preset-token"}, False)):
            out = io.StringIO()
            real = app.create_server

            def stop(*a, **k):
                s = real(*a, **k)
                s.serve_forever = lambda: None
                return s

            old = dict(os.environ)
            os.environ.pop("PORTAL_TOKEN", None)
            os.environ.update(env)
            app.create_server = stop
            try:
                with contextlib.redirect_stdout(out):
                    app.main(["--port", "0"])
            finally:
                app.create_server = real
                os.environ.clear()
                os.environ.update(old)
            self.assertEqual("#token=" in out.getvalue(), expect)
            self.assertNotIn("preset-token", out.getvalue())

    @unittest.skipUnless(os.name == "posix", "POSIX modes")
    def test_token_file_reader(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertIsNone(token.read_token_file(root))
            f = root / ".portal" / "token"
            f.parent.mkdir()
            f.write_text("filetoken\n")
            f.chmod(0o644)
            self.assertIsNone(token.read_token_file(root))
            f.chmod(0o600)
            self.assertEqual(token.read_token_file(root), "filetoken")


class SafePathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.outside = Path(self.tmp.name) / "outside"
        self.outside.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_inside_and_portal_state_allowed(self):
        self.assertEqual(safe_path(self.root, "a/b.md"), (self.root / "a" / "b.md").resolve())
        self.assertEqual(write_guard(self.root, ".portal/runs/x.json"), (self.root / ".portal" / "runs" / "x.json").resolve())

    def test_traversal_refused(self):
        for rel in ("../outside/x", "a/../../outside/x", "..", "a/../.."):
            with self.assertRaises(OutsideRoot, msg=rel):
                write_guard(self.root, rel)

    def test_absolute_refused(self):
        for rel in (str(self.outside / "x"), "/etc/passwd", "\\windows\\x", "C:\\x"):
            with self.assertRaises(OutsideRoot, msg=rel):
                write_guard(self.root, rel)

    def test_empty_and_nul_refused(self):
        for rel in ("", "a\0b"):
            with self.assertRaises(OutsideRoot):
                write_guard(self.root, rel)

    def test_sibling_prefix_not_confused_with_root(self):
        sibling = Path(self.tmp.name) / "repo-evil"
        sibling.mkdir()
        with self.assertRaises(OutsideRoot):
            safe_path(self.root, "../repo-evil/x")

    @unittest.skipIf(os.name == "nt", "symlinks need privileges on Windows")
    def test_symlink_escape_refused_and_nothing_written(self):
        (self.root / "link").symlink_to(self.outside, target_is_directory=True)
        with self.assertRaises(OutsideRoot):
            write_guard(self.root, "link/x.txt")
        self.assertEqual(list(self.outside.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "case-insensitive file systems")
    def test_windows_case_variant_inside_root_allowed(self):
        self.assertEqual(safe_path(self.root, "A/B").parent.parent, self.root.resolve())


if __name__ == "__main__":
    unittest.main()
