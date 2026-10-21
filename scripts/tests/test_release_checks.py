import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build_bundle  # noqa: E402
import release_checks as rc  # noqa: E402


def git(repo, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=repo, check=True, capture_output=True)


def make_bundle(tmp: Path, version="1.2.3", mutate=None):
    """A minimal valid zip + manifest in tmp, with VERSION in a fake repo root."""
    (tmp / "VERSION").write_text(version + "\n")
    zp = tmp / ("agentic-portal-%s.zip" % version)
    entries = {"VERSION": version + "\n", "portal_server/app.py": "", "web/dist/index.html": "<html>"}
    if mutate:
        entries = mutate(entries)
    with zipfile.ZipFile(zp, "w") as z:
        for name, body in entries.items():
            z.writestr(zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0)), body)
    manifest = {
        "manifest": 1, "version": version, "asset": zp.name, "size": zp.stat().st_size,
        "sha256": build_bundle.sha256(zp), "requires_python": ">=3.14",
    }
    mp = tmp / "manifest.json"
    mp.write_text(json.dumps(manifest))
    return zp, mp, manifest


class TagTest(unittest.TestCase):  # AC1
    def test_tag_must_match_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "VERSION").write_text("0.2.0\n")
            rc.check_tag("v0.2.0", Path(tmp))
            for bad in ("0.2.0", "v0.2.1", "v0.2.0-rc1"):
                with self.assertRaises(rc.CheckError, msg=bad):
                    rc.check_tag(bad, Path(tmp))

    def test_ancestor_of_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, "init", "-q", "-b", "main")
            git(repo, "commit", "-q", "--allow-empty", "-m", "a")
            git(repo, "tag", "v1")
            git(repo, "commit", "-q", "--allow-empty", "-m", "b")
            git(repo, "switch", "-q", "-c", "side")
            git(repo, "commit", "-q", "--allow-empty", "-m", "c")
            git(repo, "tag", "v2")
            rc.check_ancestor("v1", repo, main_ref="main")
            with self.assertRaises(rc.CheckError):
                rc.check_ancestor("v2", repo, main_ref="main")
            with self.assertRaises(rc.CheckError):
                rc.check_ancestor("v1", repo, main_ref="origin/main")  # unknown ref is an error, not a pass


class PrereleaseTest(unittest.TestCase):
    def test_zero_major_is_prerelease(self):
        self.assertEqual(rc.prerelease_flag("0.1.0"), "--prerelease")
        self.assertEqual(rc.prerelease_flag("1.0.0"), "")
        self.assertEqual(rc.prerelease_flag("10.0.0"), "")


class VerifyTest(unittest.TestCase):
    def check(self, mutate=None, manifest_edit=None):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            zp, mp, manifest = make_bundle(tmp, mutate=mutate)
            if manifest_edit:
                manifest_edit(manifest)
                mp.write_text(json.dumps(manifest))
            rc.verify(zp, mp, tmp)

    def test_valid(self):
        self.check()

    def test_rejects_each_defect(self):
        cases = {
            "format": (None, lambda m: m.update(manifest=2)),
            "sha": (None, lambda m: m.update(sha256="0" * 64)),
            "size": (None, lambda m: m.update(size=1)),
            "asset": (None, lambda m: m.update(asset="other.zip")),
            "python": (None, lambda m: m.update(requires_python=">=3.11")),
            "key": (None, lambda m: m.pop("size")),
            "prefix": (lambda e: {"server/" + k: v for k, v in e.items()}, None),
            "unsafe": (lambda e: {**e, "../evil": ""}, None),
            "tests": (lambda e: {**e, "portal_server/tests/t.py": ""}, None),
            "inner version": (lambda e: {**e, "VERSION": "9.9.9\n"}, None),
        }
        for name, (mutate, edit) in cases.items():
            with self.subTest(name), self.assertRaises(rc.CheckError):
                self.check(mutate, edit)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            zp, mp, _ = make_bundle(Path(tmp))
            self.assertEqual(rc.main(["verify", str(zp), str(mp)]), 1)  # VERSION of this repo differs from the fixture's
            self.assertEqual(rc.main(["bogus"]), 2)


if __name__ == "__main__":
    unittest.main()
