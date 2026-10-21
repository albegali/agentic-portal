"""Build the release bundle: agentic-portal-<version>.zip + manifest.json.

Usage: python scripts/build_bundle.py [--out DIR]
Requires web/dist/ to be built (npm --prefix web run build).

Layout (manifest format 1, read by the skeleton launcher tools/portal.py): the zip root holds
portal_server/, web/dist/ and VERSION.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "server"))

from portal_server.contract import CONTRACT_BUILT_FOR  # noqa: E402
REQUIRES_PYTHON = ">=3.14"
MANIFEST_FORMAT = 1
ROOT_ENTRIES = ("portal_server", "web", "VERSION")


def check_entry_name(name: str) -> str:
    """The launcher's safe-extraction rules: relative, forward slashes, no `..`, no drive letter."""
    parts = name.split("/")
    if (
        not name or name.startswith("/") or "\\" in name or re.match(r"^[A-Za-z]:", name)
        or any(p in ("", ".", "..") for p in parts) or "\0" in name
    ):
        raise SystemExit("unsafe bundle entry name: %r" % name)
    if parts[0] not in ROOT_ENTRIES:
        raise SystemExit("bundle entry outside the bundle layout: %r" % name)
    return name


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bundle_files(repo: Path):
    """(archive name, source path) pairs; server without tests/caches."""
    dist = repo / "web" / "dist"
    if not (dist / "index.html").is_file():
        raise SystemExit("web/dist/ is missing: run `npm --prefix web run build` first")
    yield "VERSION", repo / "VERSION"
    package = repo / "server" / "portal_server"
    for p in sorted(package.rglob("*")):
        rel = p.relative_to(package)
        if p.is_file() and "tests" not in rel.parts and "__pycache__" not in rel.parts and p.suffix != ".pyc":
            yield ("portal_server/" + rel.as_posix()), p
    for p in sorted(dist.rglob("*")):
        if p.is_file():
            yield p.relative_to(repo).as_posix(), p


def build(repo: Path = REPO, out: Path | None = None):
    out = out or repo / "release"
    out.mkdir(parents=True, exist_ok=True)
    version = (repo / "VERSION").read_text(encoding="utf-8").strip()
    zip_path = out / ("agentic-portal-%s.zip" % version)
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, src in bundle_files(repo):
                check_entry_name(name)
                info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))  # reproducible
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, src.read_bytes())
    except BaseException:
        zip_path.unlink(missing_ok=True)  # never leave a half-built bundle behind
        raise
    manifest = {
        "manifest": MANIFEST_FORMAT,
        "version": version,
        "asset": zip_path.name,
        "size": zip_path.stat().st_size,
        "sha256": sha256(zip_path),
        "requires_python": REQUIRES_PYTHON,
        "contract_built_for": CONTRACT_BUILT_FOR,
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return zip_path, manifest_path


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    zip_path, manifest_path = build(out=args.out)
    print(zip_path)
    print(manifest_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
