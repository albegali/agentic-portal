"""Contract tests: recorded envelopes of the eight tools against the skeleton schemas, and a live run."""
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portal_server.contract import runner  # noqa: E402
from portal_server.contract.validator import Validator, load_schemas  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = REPO / "schemas"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "envelopes"
TOOLS = ("version", "next", "next-story", "backlog", "check", "plan", "journal", "story")

try:
    import jsonschema
    from referencing import Registry, Resource
except ImportError:  # test-only dependency; CI sets WF_REQUIRE_JSONSCHEMA=1 where it must be there
    jsonschema = None


def schema_file(tool):
    return "%s.schema.json" % tool


def fixture(tool):
    return json.loads((FIXTURES / (tool + ".json")).read_text(encoding="utf-8"))


class RecordedEnvelopesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.own = Validator(load_schemas(SCHEMAS_DIR))

    def test_every_tool_has_a_fixture(self):
        self.assertEqual({p.stem for p in FIXTURES.glob("*.json")}, set(TOOLS))
        self.assertEqual(set(TOOLS), set(runner.TOOLS))

    def test_fixtures_are_envelopes_of_their_tool(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                env = fixture(tool)
                self.assertEqual(env["tool"], tool)
                self.assertEqual(self.own.errors(env, "envelope.schema.json"), [])
                self.assertEqual(self.own.errors(env, schema_file(tool)), [])

    def test_own_validator_agrees_with_jsonschema(self):
        if jsonschema is None:
            self.assertFalse(os.environ.get("WF_REQUIRE_JSONSCHEMA"), "jsonschema required but not installed")
            self.skipTest("jsonschema not installed")
        raw = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in SCHEMAS_DIR.glob("*.schema.json")}
        registry = Registry().with_resources([(name, Resource.from_contents(s)) for name, s in raw.items()])
        for tool in TOOLS:
            with self.subTest(tool=tool):
                jsonschema.Draft202012Validator(raw[schema_file(tool)], registry=registry).validate(fixture(tool))


class LiveToolsTest(unittest.TestCase):
    """Runs the eight tools for real. SKELETON_DIR (CI: checkout at SKELETON_PIN) overrides this repository."""

    def test_every_tool_runs_against_the_skeleton(self):
        root = Path(os.environ.get("SKELETON_DIR") or REPO)
        if not (root / "tools" / "wf.py").exists():
            self.skipTest("no skeleton checkout at %s" % root)
        validator = Validator(load_schemas(root / "schemas"))
        backlog = runner.run_tool(root, "backlog")
        self.assertIsInstance(backlog, runner.Ok, backlog)
        stories = backlog.data["stories"]
        for tool in TOOLS:
            with self.subTest(tool=tool):
                needs_id = tool in ("next-story", "story")
                if needs_id and not stories:
                    result = runner.run_tool(root, tool, ("ZZ0000",))
                    self.assertIsInstance(result, runner.ContractError)
                    self.assertIn("unknown_id", result.message)
                    continue
                args = (stories[0]["id"],) if needs_id else ()
                result = runner.run_tool(root, tool, args)
                self.assertIsInstance(result, runner.Ok, result)
                env = result.envelope
                self.assertEqual(env["tool"], tool)
                self.assertEqual(validator.errors(env, "envelope.schema.json"), [])
                self.assertEqual(validator.errors(env, schema_file(tool)), [])


if __name__ == "__main__":
    unittest.main()
