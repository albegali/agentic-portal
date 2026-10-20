"""Build the release bundle: agentic-portal-<version>.zip + manifest.json.

Usage: python scripts/build_bundle.py [--out DIR]
Requires web/dist/ to be built (npm --prefix web run build).
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "server"))

from portal_server.contract import CONTRACT_BUILT_FOR  # noqa: E402
PYTHON_MIN = "3.14"


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
    for p in sorted((repo / "server").rglob("*")):
        rel = p.relative_to(repo)
        if p.is_file() and "tests" not in rel.parts and "__pycache__" not in rel.parts and p.suffix != ".pyc":
            yield rel.as_posix(), p
    for p in sorted(dist.rglob("*")):
        if p.is_file():
            yield p.relative_to(repo).as_posix(), p


def build(repo: Path = REPO, out: Path | None = None):
    out = out or repo / "release"
    out.mkdir(parents=True, exist_ok=True)
    version = (repo / "VERSION").read_text(encoding="utf-8").strip()
    zip_path = out / ("agentic-portal-%s.zip" % version)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, src in bundle_files(repo):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))  # reproducible
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, src.read_bytes())
    manifest = {
        "version": version,
        "file": zip_path.name,
        "sha256": sha256(zip_path),
        "python_min": PYTHON_MIN,
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
