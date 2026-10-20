"""Test helper: a throwaway repository holding a compatible skeleton (tools/wf.py + schemas/)."""
import shutil
from pathlib import Path

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"
VERSION_ENVELOPE = {"contract": "1.0", "tool": "version", "data": {"skeleton": "1.2.0", "contract": "1.0"}}


def make_skeleton(repo, contract="1.0"):
    env = {**VERSION_ENVELOPE, "contract": contract, "data": {**VERSION_ENVELOPE["data"], "contract": contract}}
    tools = Path(repo) / "tools"
    tools.mkdir(exist_ok=True)
    (tools / "wf.py").write_text("import json\nprint(json.dumps(%r))\n" % env, encoding="utf-8")
    shutil.copytree(SCHEMAS_DIR, Path(repo) / "schemas", dirs_exist_ok=True)
