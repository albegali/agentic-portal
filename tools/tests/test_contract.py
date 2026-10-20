"""Contract 1.x tests: every published schema validates its samples, the tools emit valid envelopes.

`jsonschema` is a test/CI dependency only (the tools themselves stay stdlib). Without it these tests are skipped
locally; CI installs it and fails if it is missing (WF_REQUIRE_JSONSCHEMA=1).
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import unittest

try:
    import jsonschema
    from referencing import Registry, Resource
except ImportError:  # pragma: no cover
    jsonschema = None

sys.path.insert(0, os.path.dirname(__file__))
from test_workflow import Repo  # noqa: E402
import wf  # noqa: E402  (tools/ is on sys.path via test_workflow)

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCHEMAS = os.path.join(SRC, "schemas")
NAMES = ["version", "next", "next-story", "backlog", "check", "plan", "journal", "story"]
C = "1.0"

SAMPLES = {
    "version": {"skeleton": "1.0.0", "contract": C},
    "next": {"step": "kickoff", "owner": "agent", "ids": [], "why": "x", "phase": "inception", "tier": "balanced",
             "models": {"claude-code": "sonnet"}, "command": "/kickoff", "weekly_due": False, "current_sprint": None,
             "next_sprint": None, "human_gates": []},
    "next-story": {"step": "done", "ids": ["AP0101"], "why": "x", "owner": "human", "deps": [], "deps_done": True},
    "backlog": {"status": None, "epics": [], "stories": []},
    "check": {"ok": True, "errors": 0, "warnings": 0, "counts": {"stories": 0}, "issues": []},
    "plan": {"releases": [], "sprints": []},
    "journal": {"context": None, "decisions": [], "learnings": [], "weekly": [], "monthly": []},
    "story": {"id": "AP0101", "artifacts": [{"kind": "story", "path": "analysis/10-stories/STORY_AP0101_x.md", "status": None}],
              "tasks": [{"id": "TSK-AP0101-01"}]},
}


def load(name: str) -> dict:
    with open(os.path.join(SCHEMAS, f"{name}.schema.json"), encoding="utf-8") as f:
        return json.load(f)


@unittest.skipIf(jsonschema is None and not os.environ.get("WF_REQUIRE_JSONSCHEMA"), "jsonschema not installed")
class ContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(jsonschema, "WF_REQUIRE_JSONSCHEMA is set but jsonschema is missing")
        reg = Registry()
        for name in ["envelope", *NAMES]:
            s = load(name)
            reg = reg.with_resource(s["$id"], Resource.from_contents(s))
        self.registry = reg

    def validate(self, name: str, doc: dict) -> None:
        jsonschema.validate(doc, load(name), registry=self.registry, cls=jsonschema.Draft202012Validator)

    def invalid(self, name: str, doc: dict) -> None:
        with self.assertRaises(jsonschema.ValidationError):
            self.validate(name, doc)

    def test_all_schemas_are_listed_and_valid(self) -> None:
        files = sorted(os.path.basename(p)[:-len(".schema.json")] for p in glob.glob(os.path.join(SCHEMAS, "*.schema.json")))
        self.assertEqual(files, sorted(["envelope", *NAMES]))
        for n in files:
            jsonschema.Draft202012Validator.check_schema(load(n))

    def test_samples_validate_in_envelope_and_alone(self) -> None:
        for name, data in SAMPLES.items():
            env = {"contract": C, "tool": name, "data": data}
            self.validate(name, env)
            self.validate("envelope", env)

    def test_extra_fields_are_allowed_and_wrong_types_rejected(self) -> None:
        for name, data in SAMPLES.items():
            self.validate(name, {"contract": "1.7", "tool": name, "data": {**data, "added_later": 1}})
        self.invalid("check", {"contract": C, "tool": "check", "data": {**SAMPLES["check"], "ok": "yes"}})
        self.invalid("version", {"contract": C, "tool": "version", "data": {"skeleton": "1.0.0"}})
        self.invalid("next", {"contract": C, "tool": "backlog", "data": SAMPLES["next"]})  # wrong tool name

    def test_contract_major_is_pinned_to_1(self) -> None:
        # a major bump in the tools must come with new schemas (and this test): the emitted major must match the published one
        self.assertEqual(wf.CONTRACT_VERSION.split(".")[0], "1", "contract major changed: publish new schemas")
        self.assertEqual(C, wf.CONTRACT_VERSION)
        for name, data in SAMPLES.items():
            self.invalid(name, {"contract": "2.0", "tool": name, "data": data})
            self.invalid(name, {"contract": "1", "tool": name, "data": data})
        self.invalid("envelope", {"contract": "2.0", "tool": "x", "data": {}})

    def test_error_envelope(self) -> None:
        err = {"contract": C, "tool": "next", "error": {"code": "boom", "message": "failed"}}
        self.validate("envelope", err)
        self.invalid("envelope", {**err, "data": {}})                       # error and data are exclusive
        self.invalid("envelope", {"contract": C, "tool": "next", "error": {"code": "boom"}})
        self.invalid("envelope", {"contract": C, "tool": "next"})

    def test_empty_states_are_valid(self) -> None:
        for name in ("backlog", "plan", "journal"):
            self.validate(name, {"contract": C, "tool": name, "data": SAMPLES[name]})

    def test_tools_emit_valid_envelopes(self) -> None:
        r = Repo()
        self.addCleanup(__import__("shutil").rmtree, r.dir, True)
        r.through_inception()
        env = json.loads(r.run("tools/next_step.py", "--json").stdout)
        self.assertEqual((env["contract"], env["tool"]), (C, "next"))
        self.validate("next", env)
        self.validate("envelope", env)
        story = json.loads(r.run("tools/next_step.py", "DM0101", "--json").stdout)
        self.assertEqual(story["tool"], "next-story")
        self.validate("next-story", story)
        self.validate("envelope", story)

    def test_version_command(self) -> None:
        r = Repo()
        self.addCleanup(__import__("shutil").rmtree, r.dir, True)
        env = json.loads(r.run("tools/wf.py", "version", "--json").stdout)
        self.validate("version", env)
        self.validate("envelope", env)
        with open(os.path.join(SRC, "tools", "VERSION"), encoding="utf-8") as f:
            self.assertEqual(env["data"]["skeleton"], f.read().strip())
        self.assertIn("contract 1.0", r.run("tools/wf.py", "version").stdout)

    def test_failure_prints_error_envelope_and_exits_non_zero(self) -> None:
        r = Repo()
        self.addCleanup(__import__("shutil").rmtree, r.dir, True)
        r.through_inception()
        p = r.run("tools/next_step.py", "ZZ9999", "--json", ok=False)
        self.assertNotEqual(p.returncode, 0)
        env = json.loads(p.stdout)
        self.assertNotIn("data", env)
        self.assertEqual(env["error"]["code"], "unknown_id")
        self.validate("envelope", env)


if __name__ == "__main__":
    unittest.main()
