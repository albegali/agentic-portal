import io
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portal_server import app  # noqa: E402
from portal_server.__main__ import check_python  # noqa: E402


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "VERSION").write_text("9.9.9\n")
        (root / "web" / "dist").mkdir(parents=True)
        (root / "web" / "dist" / "index.html").write_text("<h1>hi</h1>")
        (root / "secret.txt").write_text("secret")
        self.server = app.create_server("127.0.0.1", 0, root, root / "web" / "dist")
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = "http://127.0.0.1:%d" % self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def get(self, path):
        return urllib.request.urlopen(self.base + path)

    def test_listens_on_loopback_only(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_health_shape(self):
        data = json.load(self.get("/api/health"))
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["portal_version"], "9.9.9")
        self.assertEqual(data["contract_version"], "unknown")
        self.assertEqual(data["skeleton_version"], "unknown")
        self.assertRegex(data["datetime"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_serves_index(self):
        self.assertIn(b"<h1>hi</h1>", self.get("/").read())

    def test_path_traversal_does_not_leak(self):
        body = self.get("/..%2Fsecret.txt").read()
        self.assertNotIn(b"secret", body)

    def test_unknown_api_404(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.get("/api/nope")
        self.assertEqual(cm.exception.code, 404)


class HostTest(unittest.TestCase):
    def test_refuses_non_loopback(self):
        for host in ("0.0.0.0", "192.168.1.10", "::"):
            with self.assertRaises(ValueError, msg=host):
                app.create_server(host, 0)

    def test_main_exits_nonzero_on_bad_host(self):
        self.assertEqual(app.main(["--host", "0.0.0.0"]), 2)

    def test_accepts_loopback_names(self):
        for host in ("127.0.0.1", "localhost"):
            s = app.create_server(host, 0)
            self.assertEqual(s.server_address[0], "127.0.0.1")
            s.server_close()


class PythonCheckTest(unittest.TestCase):
    def test_old_python_exits_with_message(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            check_python((3, 13, 0), err)
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("3.14", err.getvalue())

    def test_new_python_ok(self):
        check_python((3, 14, 0))


if __name__ == "__main__":
    unittest.main()
