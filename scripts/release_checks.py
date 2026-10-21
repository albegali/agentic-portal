"""Release checks used by .github/workflows/release.yml (and its dry run).

Usage: python scripts/release_checks.py tag TAG | ancestor TAG | prerelease | verify ZIP MANIFEST
Exit 0 = ok, 1 = check failed (message on stderr). Stdlib only.
"""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_bundle import MANIFEST_FORMAT, REQUIRES_PYTHON, check_entry_name  # noqa: E402

MANIFEST_KEYS = {"manifest", "version", "asset", "size", "sha256", "requires_python"}


class CheckError(Exception):
    pass


def version_of(repo: Path = REPO) -> str:
    return (repo / "VERSION").read_text(encoding="utf-8").strip()


def check_tag(tag: str, repo: Path = REPO) -> None:
    if tag != "v" + version_of(repo):
        raise CheckError("tag %s does not match VERSION (expected v%s)" % (tag, version_of(repo)))


def check_ancestor(tag: str, repo: Path = REPO, main_ref: str = "origin/main") -> None:
    """The tagged commit must be reachable from origin/main."""
    r = subprocess.run(["git", "merge-base", "--is-ancestor", tag + "^{commit}", main_ref], cwd=repo, capture_output=True, text=True)
    if r.returncode == 1:
        raise CheckError("tag %s is not an ancestor of %s" % (tag, main_ref))
    if r.returncode != 0:
        raise CheckError("cannot compare %s with %s: %s" % (tag, main_ref, r.stderr.strip()))


def prerelease_flag(version: str) -> str:
    """`--prerelease` for 0.x (pre-releases until R1 closes), else empty."""
    return "--prerelease" if version.split(".")[0] == "0" else ""


def verify(zip_path: Path, manifest_path: Path, repo: Path = REPO) -> None:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    missing = MANIFEST_KEYS - manifest.keys()
    if missing:
        raise CheckError("manifest lacks %s" % sorted(missing))
    if manifest["manifest"] != MANIFEST_FORMAT:
        raise CheckError("manifest format %r, expected %d" % (manifest["manifest"], MANIFEST_FORMAT))
    if manifest["requires_python"] != REQUIRES_PYTHON:
        raise CheckError("requires_python %r, expected %r" % (manifest["requires_python"], REQUIRES_PYTHON))
    zip_path = Path(zip_path)
    if manifest["asset"] != zip_path.name:
        raise CheckError("manifest asset %r is not %r" % (manifest["asset"], zip_path.name))
    if manifest["version"] != version_of(repo) or zip_path.name != "agentic-portal-%s.zip" % manifest["version"]:
        raise CheckError("version mismatch between VERSION, manifest and asset name")
    if manifest["size"] != zip_path.stat().st_size:
        raise CheckError("size %s does not match the zip (%s)" % (manifest["size"], zip_path.stat().st_size))
    if manifest["sha256"] != hashlib.sha256(zip_path.read_bytes()).hexdigest():
        raise CheckError("sha256 does not match the zip")
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        if z.testzip() is not None:
            raise CheckError("corrupt zip entry")
        for name in names:
            try:
                check_entry_name(name)
            except SystemExit as exc:
                raise CheckError(str(exc))
        for must in ("VERSION", "portal_server/app.py", "web/dist/index.html"):
            if must not in names:
                raise CheckError("zip lacks %s" % must)
        if [n for n in names if "/tests/" in n or "__pycache__" in n]:
            raise CheckError("zip contains tests or caches")
        if z.read("VERSION").decode("utf-8").strip() != manifest["version"]:
            raise CheckError("VERSION inside the zip differs from the manifest")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv[:1] == ["tag"] and len(argv) == 2:
            check_tag(argv[1])
        elif argv[:1] == ["ancestor"] and len(argv) == 2:
            check_ancestor(argv[1])
        elif argv[:1] == ["prerelease"] and len(argv) == 1:
            print(prerelease_flag(version_of()))
        elif argv[:1] == ["verify"] and len(argv) == 3:
            verify(Path(argv[1]), Path(argv[2]))
        else:
            print(__doc__, file=sys.stderr)
            return 2
    except CheckError as exc:
        print("release check failed: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
