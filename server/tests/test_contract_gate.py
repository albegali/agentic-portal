import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portal_server.contract import gate  # noqa: E402
from portal_server.contract.runner import ContractError, Ok  # noqa: E402

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"
NEXT = {"contract": "1.0", "tool": "next", "data": {
    "step": "execute", "ids": ["AP0104"], "owner": "agent", "why": "w", "phase": "delivery", "tier": "balanced",
    "models": {}, "command": "/run AP0104", "weekly_due": False, "current_sprint": "S2", "next_sprint": "S3",
    "human_gates": [], "stories": [], "optional": []}}


def script(envelope, exit_code=0):
    return "import json, sys\nprint(json.dumps(%r))\nsys.exit(%d)\n" % (envelope, exit_code)


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "tools").mkdir()
        shutil.copytree(SCHEMAS_DIR, self.repo / "schemas")

    def tearDown(self):
        self.tmp.cleanup()

    def version(self, contract="1.0", skeleton="1.2.0", **extra):
        env = {"contract": contract, "tool": "version", "data": {"skeleton": skeleton, "contract": contract, **extra}}
        (self.repo / "tools" / "wf.py").write_text(script(env))

    def nxt(self, envelope=NEXT, code=0):
        (self.repo / "tools" / "next_step.py").write_text(script(envelope, code))

    def test_evaluate_rules(self):
        self.assertEqual(gate.evaluate({"contract": "1.0"})[0], gate.COMPATIBLE)
        self.assertEqual(gate.evaluate({"contract": "1.3"})[0], gate.COMPATIBLE)
        self.assertEqual(gate.evaluate({"contract": "2.0"})[0], gate.INCOMPATIBLE)
        self.assertEqual(gate.evaluate({"contract": "1.0"}, built_for="1.2")[0], gate.INCOMPATIBLE)  # lower minor
        self.assertEqual(gate.evaluate({"contract": "x"})[0], gate.INCOMPATIBLE)
        self.assertEqual(gate.evaluate({})[0], gate.INCOMPATIBLE)

    def test_compatible_with_unknown_extra_fields_and_data_call_works(self):  # AC3
        self.version(contract="1.4", future_field={"a": 1})
        self.nxt({**NEXT, "contract": "1.4", "extra": 1})
        g = gate.Gate(self.repo)
        snap = g.snapshot()
        self.assertEqual((snap["state"], snap["skeleton_version"], snap["contract_version"]), ("compatible", "1.2.0", "1.4"))
        self.assertIsNone(snap["recovery"])
        self.assertIsInstance(g.call("next"), Ok)

    def test_missing_wf_py(self):  # AC2
        g = gate.Gate(self.repo)
        snap = g.snapshot()
        self.assertEqual(snap["state"], "missing")
        self.assertFalse(snap["recovery"]["runnable"])
        self.assertTrue(snap["recovery"]["steps"] and snap["recovery"]["summary"])
        res = g.call("next")
        self.assertEqual((type(res), res.kind), (ContractError, "incompatible"))

    def test_major_mismatch_and_lower_minor_refuse_calls(self):  # AC2
        self.nxt()
        self.version(contract="2.0")
        g = gate.Gate(self.repo)
        self.assertEqual(g.snapshot()["state"], "incompatible")
        self.assertEqual(g.call("next").kind, "incompatible")
        self.version(contract="1.0")
        self.assertEqual(gate.Gate(self.repo, built_for="1.1").snapshot()["state"], "incompatible")

    def test_unreadable_version_is_incompatible(self):
        (self.repo / "tools" / "wf.py").write_text("print('not json')\n")
        self.assertEqual(gate.Gate(self.repo).snapshot()["state"], "incompatible")

    def test_recheck_recovers_without_restart(self):  # AC6
        self.nxt()
        self.version(contract="2.0")
        g = gate.Gate(self.repo)
        self.assertEqual(g.call("next").kind, "incompatible")
        self.version(contract="1.0")
        self.assertEqual(g.refresh()["state"], "compatible")
        self.assertIsInstance(g.call("next"), Ok)

    def test_schema_violations_are_bad_output(self):  # AC5
        self.version()
        for bad in ({**NEXT, "tool": "backlog"},
                    {"contract": "1.0", "tool": "next", "data": {k: v for k, v in NEXT["data"].items() if k != "step"}},
                    {**NEXT, "data": {**NEXT["data"], "ids": "AP0104"}}):
            self.nxt(bad)
            g = gate.Gate(self.repo)
            res = g.call("next")
            self.assertEqual((type(res), res.kind), (ContractError, "bad-output"), bad)

    def test_failed_call_rereads_version(self):
        self.version()
        self.nxt()
        g = gate.Gate(self.repo)
        self.assertEqual(g.snapshot()["state"], "compatible")
        self.nxt({"contract": "1.0", "tool": "next", "error": {"code": "x", "message": "m"}}, 1)
        self.version(contract="2.0")  # skeleton changed under us
        self.assertEqual(g.call("next").kind, "tool-error")
        self.assertEqual(g.snapshot()["state"], "incompatible")

    def test_missing_schemas_dir_is_incompatible(self):
        self.version()
        shutil.rmtree(self.repo / "schemas")
        self.assertEqual(gate.Gate(self.repo).snapshot()["state"], "incompatible")

    def test_built_for_constant(self):
        from portal_server.contract import CONTRACT_BUILT_FOR
        self.assertEqual(CONTRACT_BUILT_FOR, "1.0")


if __name__ == "__main__":
    unittest.main()
