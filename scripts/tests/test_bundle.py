import json
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build_bundle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


class ManifestConstantTest(unittest.TestCase):
    def test_manifest_uses_the_portal_constant_not_a_literal(self):  # AP0104 AC7, runs without web/dist
        from portal_server.contract import CONTRACT_BUILT_FOR
        self.assertIs(build_bundle.CONTRACT_BUILT_FOR, CONTRACT_BUILT_FOR)
        self.assertNotIn('"unknown"', (REPO / "scripts" / "build_bundle.py").read_text().split("contract_built_for")[1][:40])


class BundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (REPO / "web" / "dist" / "index.html").is_file():
            raise unittest.SkipTest("web/dist not built")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.zip, cls.manifest = build_bundle.build(REPO, cls.out / "release")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_manifest_matches_zip(self):
        m = json.loads(self.manifest.read_text())
        self.assertEqual(m["sha256"], build_bundle.sha256(self.zip))
        self.assertEqual(m["file"], self.zip.name)
        self.assertEqual(m["python_min"], "3.14")
        self.assertEqual(m["contract_built_for"], build_bundle.CONTRACT_BUILT_FOR)
        self.assertEqual(m["contract_built_for"], "1.0")
        self.assertEqual(m["version"], (REPO / "VERSION").read_text().strip())

    def test_layout(self):
        names = zipfile.ZipFile(self.zip).namelist()
        self.assertIn("VERSION", names)
        self.assertIn("web/dist/index.html", names)
        self.assertIn("server/portal_server/app.py", names)
        self.assertFalse([n for n in names if "/tests/" in n or "__pycache__" in n])

    def test_server_starts_from_bundle_without_node(self):
        dest = self.out / "extracted"
        zipfile.ZipFile(self.zip).extractall(dest)
        proc = subprocess.Popen(
            [sys.executable, "-m", "portal_server", "--port", "0"],
            cwd=dest / "server", stdout=subprocess.PIPE, text=True,
        )
        try:
            line = proc.stdout.readline()
            base = line.split()[-1]
            for _ in range(20):
                try:
                    health = json.load(urllib.request.urlopen(base + "/api/health", timeout=2))
                    break
                except OSError:
                    time.sleep(0.2)
            self.assertEqual(health["status"], "ok")
            self.assertEqual(health["portal_version"], (REPO / "VERSION").read_text().strip())
            self.assertIn(b"<div id=\"root\">", urllib.request.urlopen(base + "/").read())
        finally:
            proc.terminate()
            proc.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
