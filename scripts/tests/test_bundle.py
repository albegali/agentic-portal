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


class UnsafeNameTest(unittest.TestCase):
    def test_unsafe_entry_name_fails_build(self):  # AC5, runs without web/dist
        bad = ["/abs", "../x", "a/../x", "C:/x", "C:x", "portal_server\\x", "portal_server//x", "other/x"]
        for name in bad:
            with self.subTest(name=name), self.assertRaises(SystemExit):
                build_bundle.check_entry_name(name)
        self.assertEqual(build_bundle.check_entry_name("portal_server/app.py"), "portal_server/app.py")

    def test_build_aborts_and_leaves_no_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            real = build_bundle.bundle_files
            build_bundle.bundle_files = lambda repo: iter([("VERSION", REPO / "VERSION"), ("../evil", REPO / "VERSION")])
            try:
                with self.assertRaises(SystemExit):
                    build_bundle.build(REPO, out)
            finally:
                build_bundle.bundle_files = real
            self.assertEqual(list(out.glob("*.zip")), [])


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

    def test_manifest_format_1(self):  # AC4, AC6
        m = json.loads(self.manifest.read_text())
        self.assertEqual(m["sha256"], build_bundle.sha256(self.zip))
        self.assertEqual(m["asset"], self.zip.name)
        self.assertEqual(m["size"], self.zip.stat().st_size)
        self.assertEqual(m["requires_python"], ">=3.14")
        self.assertEqual(m["manifest"], 1)
        self.assertNotIn("file", m)
        self.assertNotIn("python_min", m)
        self.assertEqual(m["contract_built_for"], build_bundle.CONTRACT_BUILT_FOR)
        self.assertEqual(m["contract_built_for"], "1.0")
        self.assertEqual(m["version"], (REPO / "VERSION").read_text().strip())

    def test_release_verify_accepts_the_built_bundle(self):  # AC1: the check release.yml runs before publishing
        import release_checks
        release_checks.verify(self.zip, self.manifest, REPO)

    def test_layout_and_manifest_match_zip(self):  # AC6
        z = zipfile.ZipFile(self.zip)
        names = z.namelist()
        self.assertIn("VERSION", names)
        self.assertIn("web/dist/index.html", names)
        self.assertIn("portal_server/app.py", names)
        self.assertEqual({n.split("/")[0] for n in names}, {"portal_server", "web", "VERSION"})
        self.assertFalse([n for n in names if "/tests/" in n or "__pycache__" in n or n.endswith(".pyc")])
        self.assertEqual({i.date_time for i in z.infolist()}, {(2020, 1, 1, 0, 0, 0)})
        self.assertEqual({i.external_attr >> 16 for i in z.infolist()}, {0o644})
        m = json.loads(self.manifest.read_text())
        self.assertEqual(m["size"], self.zip.stat().st_size)
        self.assertEqual(m["sha256"], build_bundle.sha256(self.zip))

    def test_server_starts_from_bundle_without_node(self):
        dest = self.out / "extracted"
        zipfile.ZipFile(self.zip).extractall(dest)
        fixture = self.out / "fixture-repo"
        fixture.mkdir()
        (fixture / "project.toml").write_text("[portal]\nversion = \"0.0.0\"\n")
        proc = subprocess.Popen(
            [sys.executable, "-m", "portal_server", "--port", "0", "--repo", str(fixture)],
            cwd=dest, stdout=subprocess.PIPE, text=True,
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
