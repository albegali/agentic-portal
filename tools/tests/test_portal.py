"""Tests of tools/portal.py: a fake release served locally, a fake portal bundle (stdlib unittest)."""
from __future__ import annotations

import hashlib
import http.server
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile

TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, TOOLS)
import portal  # noqa: E402

FAKE_SERVER = '''
import argparse, json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
ap = argparse.ArgumentParser(); ap.add_argument("--host"); ap.add_argument("--port", type=int); ap.add_argument("--repo")
a = ap.parse_args()
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        b = json.dumps({"status": "ok", "repo": a.repo}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *x): pass
HTTPServer((a.host, a.port), H).serve_forever()
'''


def make_zip(extra: "dict | None" = None, server: str = FAKE_SERVER) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("portal_server/__init__.py", "")
        z.writestr("portal_server/__main__.py", server)
        for k, v in (extra or {}).items():
            z.writestr(k, v)
    return buf.getvalue()


def manifest_for(data: bytes, version: str = "1.0.0", **kw) -> dict:
    m = {"manifest": 1, "version": version, "asset": "agentic-portal-%s.zip" % version, "size": len(data),
         "sha256": hashlib.sha256(data).hexdigest(), "requires_python": ">=3.11"}
    m.update(kw)
    return m


class Release:
    """Serves /v<version>/manifest.json and the asset on a local port."""

    def __init__(self, files: dict) -> None:
        files = dict(files)

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = files.get(self.path)
                if body is None:
                    self.send_response(404); self.end_headers(); return
                self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a): pass

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.base = "http://127.0.0.1:%d" % self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def close(self) -> None:
        self.srv.shutdown(); self.srv.server_close()


def release(data: bytes, version: str = "1.0.0", **kw) -> "tuple[Release, dict]":
    m = manifest_for(data, version, **kw)
    return Release({"/manifest.json": json.dumps(m).encode(), "/" + m["asset"]: data}), m


class PortalCase(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tempfile.mkdtemp(prefix="portal-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.project('[portal]\nversion = "1.0.0"\n')
        self.env = {k: v for k, v in os.environ.items() if k not in ("PORTAL_BUNDLE", "PORTAL_RELEASE_BASE")}

    def project(self, text: str) -> None:
        with open(os.path.join(self.root, "project.toml"), "w") as f:
            f.write(text)

    def launch(self, *args: str, base: "str | None" = None, timeout: int = 60, **env) -> subprocess.CompletedProcess:
        e = dict(self.env, **env)
        if base:
            e["PORTAL_RELEASE_BASE"] = base
        return subprocess.run([sys.executable, os.path.join(TOOLS, "portal.py"), *args], cwd=self.root, env=e,
                              capture_output=True, text=True, timeout=timeout)

    def popen(self, base: str, *args: str) -> subprocess.Popen:
        e = dict(self.env, PORTAL_RELEASE_BASE=base)
        p = subprocess.Popen([sys.executable, os.path.join(TOOLS, "portal.py"), "--no-browser", *args], cwd=self.root,
                             env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop, p)
        return p

    @staticmethod
    def stop(p: subprocess.Popen) -> None:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=15)
            except subprocess.TimeoutExpired:
                p.kill(); p.wait()
        for s in (p.stdout, p.stderr):
            if s:
                s.close()

    def wait_run_file(self, p: subprocess.Popen, timeout: float = 30) -> dict:
        import time
        path = os.path.join(self.root, ".portal", "run.json")
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if os.path.exists(path):
                with open(path) as f:
                    return json.load(f)
            if p.poll() is not None:
                self.fail("launcher exited early: %s" % p.stderr.read())
            time.sleep(0.1)
        self.fail("run.json not written")


class Download(PortalCase):
    def test_ac1_download_verify_cache_start(self):  # AC1
        data = make_zip()
        rel, m = release(data)
        self.addCleanup(rel.close)
        p = self.popen(rel.base)
        info = self.wait_run_file(p)
        self.assertTrue(os.path.isfile(os.path.join(self.root, ".portal", "1.0.0", "portal_server", "__main__.py")))
        self.assertFalse(os.path.exists(os.path.join(self.root, ".portal", "1.0.0.tmp")))
        self.assertTrue(portal.healthy(info["url"], 3))
        self.assertEqual(info["version"], "1.0.0")
        h = json.loads(__import__("urllib.request").request.urlopen(info["url"] + "/api/health").read())
        self.assertEqual(os.path.realpath(h["repo"]), os.path.realpath(self.root))  # --repo passed because the bundle supports it
        p.terminate(); p.wait(timeout=15)
        self.assertFalse(os.path.exists(os.path.join(self.root, ".portal", "run.json")))  # cleaned on exit

    def test_ac2_tampered_download(self):  # AC2
        data = make_zip()
        m = manifest_for(data)
        rel = Release({"/manifest.json": json.dumps(m).encode(), "/" + m["asset"]: data[:-1] + b"X"})
        self.addCleanup(rel.close)
        r = self.launch("--no-browser", base=rel.base)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("integrity", r.stderr)
        self.assertEqual(os.listdir(os.path.join(self.root, ".portal")), [])  # nothing cached, no leftovers

    def test_size_mismatch_is_integrity_error(self):
        data = make_zip()
        m = manifest_for(data, size=len(data) + 1)
        rel = Release({"/manifest.json": json.dumps(m).encode(), "/" + m["asset"]: data})
        self.addCleanup(rel.close)
        self.assertEqual(self.launch("--no-browser", base=rel.base).returncode, 2)

    def test_ac5_no_network_no_cache(self):  # AC5
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            dead = "http://127.0.0.1:%d" % s.getsockname()[1]
        r = self.launch("--no-browser", base=dead)
        self.assertEqual(r.returncode, 1)
        self.assertIn("cannot reach", r.stderr)

    def test_ac5_cache_starts_without_network(self):  # AC5
        data = make_zip()
        rel, m = release(data)
        portal.install(self.root, "1.0.0", self._zip(data), m)
        rel.close()
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            dead = "http://127.0.0.1:%d" % s.getsockname()[1]
        p = self.popen(dead)
        self.assertTrue(portal.healthy(self.wait_run_file(p)["url"], 3))

    def _zip(self, data: bytes) -> str:
        path = os.path.join(self.root, "b.zip")
        with open(path, "wb") as f:
            f.write(data)
        return path

    def test_ac6_missing_version(self):  # AC6
        self.project("[portal]\n")
        r = self.launch("--no-browser")
        self.assertEqual(r.returncode, 1)
        self.assertIn("version", r.stderr)

    def test_ac6_version_not_found(self):  # AC6
        rel = Release({})
        self.addCleanup(rel.close)
        r = self.launch("--no-browser", base=rel.base)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not found", r.stderr)

    def test_no_project_toml(self):
        os.remove(os.path.join(self.root, "project.toml"))
        d = tempfile.mkdtemp(prefix="isolated-")
        self.addCleanup(shutil.rmtree, d, True)
        self.root = d
        self.assertEqual(self.launch("--no-browser").returncode, 1)

    def test_manifest_major_unsupported(self):
        rel = Release({"/manifest.json": json.dumps({"manifest": 2}).encode()})
        self.addCleanup(rel.close)
        self.assertEqual(self.launch("--no-browser", base=rel.base).returncode, 2)


class Override(PortalCase):
    def test_ac7_bundle_zip_verified_no_download(self):  # AC7
        data = make_zip()
        d = os.path.join(self.root, "dl"); os.mkdir(d)
        m = manifest_for(data)
        with open(os.path.join(d, m["asset"]), "wb") as f:
            f.write(data)
        with open(os.path.join(d, "manifest.json"), "w") as f:
            json.dump(m, f)
        zp = os.path.join(d, m["asset"])
        p = subprocess.Popen([sys.executable, os.path.join(TOOLS, "portal.py"), "--no-browser"], cwd=self.root,
                             env=dict(self.env, PORTAL_BUNDLE=zp, PORTAL_RELEASE_BASE="http://127.0.0.1:1"),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop, p)
        self.assertTrue(portal.healthy(self.wait_run_file(p)["url"], 3))
        self.assertTrue(os.path.isdir(os.path.join(self.root, ".portal", "local")))

    def test_ac7_bundle_zip_tampered(self):  # AC7
        data = make_zip()
        d = os.path.join(self.root, "dl"); os.mkdir(d)
        m = manifest_for(data)
        with open(os.path.join(d, "x.zip"), "wb") as f:
            f.write(data + b"junk")
        with open(os.path.join(d, "manifest.json"), "w") as f:
            json.dump(m, f)
        r = self.launch("--no-browser", PORTAL_BUNDLE=os.path.join(d, "x.zip"))
        self.assertEqual(r.returncode, 2)

    def test_ac7_bundle_missing(self):
        self.assertEqual(self.launch("--no-browser", PORTAL_BUNDLE=os.path.join(self.root, "nope")).returncode, 1)


class Extraction(PortalCase):
    def attack(self, name: str):
        data = make_zip({name: "x"})
        rel, m = release(data)
        self.addCleanup(rel.close)
        r = self.launch("--no-browser", base=rel.base)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("unsafe", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.root, ".portal", "1.0.0")))
        self.assertFalse(os.path.exists(os.path.join(self.root, ".portal", "1.0.0.tmp")))
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.root), "evil.txt")))

    def test_ac9_dotdot(self):  # AC9
        self.attack("../evil.txt")

    def test_ac9_absolute(self):  # AC9
        self.attack("/tmp/evil.txt")

    def test_ac9_drive_letter(self):  # AC9
        self.attack("C:/evil.txt")

    def test_ac9_symlink(self):  # AC9
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            i = zipfile.ZipInfo("link"); i.external_attr = (0o120777 << 16)
            z.writestr(i, "/etc/passwd")
        rel, m = release(buf.getvalue())
        self.addCleanup(rel.close)
        r = self.launch("--no-browser", base=rel.base)
        self.assertEqual(r.returncode, 2)
        self.assertIn("symbolic", r.stderr)


class Running(PortalCase):
    def test_ac8_running_instance_is_reused_and_stale_replaced(self):  # AC8
        rel, m = release(make_zip())
        self.addCleanup(rel.close)
        p = self.popen(rel.base)
        info = self.wait_run_file(p)
        r = self.launch("--no-browser", base=rel.base)  # second launch: opens the running one, starts nothing
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(info["url"], r.stdout)
        with open(os.path.join(self.root, ".portal", "run.json")) as f:
            self.assertEqual(json.load(f)["pid"], info["pid"])
        p.kill(); p.wait()  # launcher crash: run.json stays; the orphaned server still answers, so it is still reused
        self.assertEqual(portal.running_instance(self.root), info["url"])
        os.kill(info["pid"], 15)  # server gone too: run.json is now stale
        import time
        for _ in range(50):
            if not portal.healthy(info["url"], 0.2):
                break
            time.sleep(0.1)
        self.assertTrue(os.path.exists(os.path.join(self.root, ".portal", "run.json")))
        self.assertIsNone(portal.running_instance(self.root))
        self.assertFalse(os.path.exists(os.path.join(self.root, ".portal", "run.json")))

    def test_port_in_use_picks_next(self):
        with socket.socket() as probe:
            probe.bind((portal.HOST, 0))
            base = probe.getsockname()[1]
        old, portal.DEFAULT_PORT = portal.DEFAULT_PORT, base  # 8765 may be taken on a developer machine
        self.addCleanup(setattr, portal, "DEFAULT_PORT", old)
        with socket.socket() as s:
            s.bind((portal.HOST, base))
            s.listen()
            self.assertGreater(portal.pick_port(), base)
        self.assertEqual(portal.pick_port(), base)


class Units(unittest.TestCase):
    def test_ac4_python_guard_in_source(self):  # AC4: the guard precedes every import that needs a newer Python
        with open(os.path.join(TOOLS, "portal.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertLess(src.index("sys.version_info < (3, 11)"), src.index("import tomllib"))

    def test_min_python(self):
        self.assertEqual(portal.min_python({"requires_python": ">=3.14"}), (3, 14))
        self.assertEqual(portal.min_python(None), (3, 11))

    def test_pick_python_unsatisfiable(self):
        with self.assertRaises(portal.LauncherError) as c:
            portal.pick_python((9, 9))
        self.assertEqual(c.exception.code, 1)

    def test_version_rejects_path_tricks(self):
        d = tempfile.mkdtemp(prefix="v-")
        self.addCleanup(shutil.rmtree, d, True)
        with open(os.path.join(d, "project.toml"), "w") as f:
            f.write('[portal]\nversion = "../x"\n')
        with self.assertRaises(portal.LauncherError):
            portal.portal_config(d)


if __name__ == "__main__":
    unittest.main()
