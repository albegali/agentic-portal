"""End-to-end smoke test of the real chain: skeleton launcher -> portal bundle -> /api/health (AP0107).

Run by CI job `launcher` on Linux, macOS and Windows (not discovered by `unittest discover`: it needs the built bundle
and a skeleton checkout).

    python scripts/tests/launcher_smoke.py --skeleton <skeleton checkout or this repo> [--bundle ZIP]

Without --bundle the bundle is built from web/dist (build it first). Node is removed from PATH for the launcher, so the
run also proves NFR-09. Needs Python >= 3.14 (the launcher then starts the server with the same interpreter).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import build_bundle  # noqa: E402

LOCAL = urllib.request.build_opener(urllib.request.ProxyHandler({}))
TIMEOUT = 90


def path_without_node() -> str:
    """PATH minus every directory that provides `node`."""
    dirs, out = os.environ.get("PATH", "").split(os.pathsep), []
    for d in dirs:
        if d and not any((Path(d) / n).exists() for n in ("node", "node.exe", "npm", "npm.cmd")):
            out.append(d)
    return os.pathsep.join(out)


def get_json(url, token=None):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token} if token else {})
    with LOCAL.open(req, timeout=5) as r:
        return json.loads(r.read())


def make_fixture(tmp: Path, skeleton: Path, portal_version: str, other_major: bool) -> Path:
    repo = tmp / ("repo-incompatible" if other_major else "repo")
    (repo / "tools").mkdir(parents=True)
    (repo / "project.toml").write_text('[project]\nname = "fixture"\n\n[portal]\nversion = "%s"\n' % portal_version)
    if other_major:  # a skeleton that speaks another contract major: only `wf.py version` is needed at start
        env = {"contract": "2.0", "tool": "version", "data": {"skeleton": "9.0.0", "contract": "2.0"}}
        (repo / "tools" / "wf.py").write_text("import json\nprint(json.dumps(%r))\n" % env)
        shutil.copytree(skeleton / "schemas", repo / "schemas")
    else:
        shutil.copytree(skeleton / "tools", repo / "tools", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "tests"))
        shutil.copytree(skeleton / "schemas", repo / "schemas")
    return repo


def run_launcher(skeleton: Path, repo: Path, bundle: Path, check):
    env = {**os.environ, "PORTAL_BUNDLE": str(bundle), "PATH": path_without_node(), "PYTHONUTF8": "1"}
    env.pop("PORTAL_TOKEN", None)
    flags = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {}
    proc = subprocess.Popen([sys.executable, str(skeleton / "tools" / "portal.py"), "--no-browser"], cwd=repo, env=env, **flags)
    try:
        run_json, deadline = repo / ".portal" / "run.json", time.monotonic() + TIMEOUT
        while not run_json.is_file():  # the launcher writes it once /api/health answers
            if proc.poll() is not None:
                raise SystemExit("launcher exited early with code %s" % proc.returncode)
            if time.monotonic() > deadline:
                raise SystemExit("launcher did not start the portal within %ds" % TIMEOUT)
            time.sleep(0.3)
        url = json.loads(run_json.read_text())["url"]
        token = (repo / ".portal" / "token").read_text().strip()
        check(url, token)
    finally:
        if proc.poll() is None:
            if os.name == "nt":
                os.kill(proc.pid, __import__("signal").CTRL_BREAK_EVENT)
            else:
                proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skeleton", type=Path, default=REPO, help="checkout holding tools/portal.py, tools/ and schemas/")
    ap.add_argument("--bundle", type=Path, help="bundle zip (default: build one)")
    args = ap.parse_args(argv)
    if sys.version_info < (3, 14):
        raise SystemExit("run with Python >= 3.14")
    skeleton = args.skeleton.resolve()
    version = (REPO / "VERSION").read_text().strip()
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        bundle = args.bundle or build_bundle.build(REPO, tmp / "release")[0]
        skeleton_version = (skeleton / "tools" / "VERSION").read_text().strip()

        repo = make_fixture(tmp, skeleton, version, other_major=False)

        def compatible(url, token):
            health = get_json(url + "/api/health")
            assert health["status"] == "ok", health
            assert health["portal_version"] == version, health
            assert health["skeleton_version"] == skeleton_version, "serves another repository? %s" % health  # read from the fixture
            contract = get_json(url + "/api/contract", token)
            assert contract["state"] == "compatible", contract
            print("compatible fixture ok:", url, health["portal_version"], "skeleton", health["skeleton_version"])

        run_launcher(skeleton, repo, bundle, compatible)

        repo = make_fixture(tmp, skeleton, version, other_major=True)

        def incompatible(url, token):
            health = get_json(url + "/api/health")
            # health stays public and answers; a 2.x envelope fails the 1.x schemas, so the version may read "unknown"
            assert health["status"] == "ok" and health["contract"]["skeleton_contract"] != "1.0", health
            assert health["contract"]["built_for"] == build_bundle.CONTRACT_BUILT_FOR, health
            contract = get_json(url + "/api/contract", token)
            assert contract["state"] == "incompatible", contract
            print("incompatible fixture ok:", contract["message"])

        run_launcher(skeleton, repo, bundle, incompatible)
        manifest = json.loads((Path(bundle).parent / "manifest.json").read_text()) if (Path(bundle).parent / "manifest.json").is_file() else {}
        if manifest:
            assert manifest["contract_built_for"] == build_bundle.CONTRACT_BUILT_FOR, manifest
    print("launcher smoke OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
