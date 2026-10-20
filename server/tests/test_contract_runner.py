import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portal_server.contract import runner  # noqa: E402
from portal_server.contract.runner import ContractError, Ok  # noqa: E402

ENVELOPE = {"contract": "1.0", "tool": "version", "data": {"skeleton": "1.2.0", "contract": "1.0"}}


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "tools").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def tool(self, body, name="wf.py"):
        (self.repo / "tools" / name).write_text(body, encoding="utf-8")

    def test_ok_envelope_and_cwd_and_utf8(self):
        self.tool("import json, os, sys\nd = %r\nd['data']['cwd'] = os.getcwd()\nd['data']['utf8'] = os.environ.get('PYTHONUTF8')\n"
                  "d['data']['argv'] = sys.argv[1:]\nprint(json.dumps(d))\n" % ENVELOPE)
        res = runner.run_tool(self.repo, "version")
        self.assertIsInstance(res, Ok)
        self.assertEqual(os.path.realpath(res.data["cwd"]), os.path.realpath(self.repo))
        self.assertEqual(res.data["utf8"], "1")
        self.assertEqual(res.data["argv"], ["version", "--json"])

    def test_missing_tool(self):
        res = runner.run_tool(self.repo, "version")
        self.assertEqual((type(res), res.kind), (ContractError, "missing-tool"))

    def test_non_json_output_is_bad_output(self):
        self.tool("print('hello')\n")
        self.assertEqual(runner.run_tool(self.repo, "version").kind, "bad-output")

    def test_json_without_envelope_is_bad_output(self):
        self.tool("print('[1]')\n")
        self.assertEqual(runner.run_tool(self.repo, "version").kind, "bad-output")

    def test_error_envelope_is_tool_error(self):
        self.tool("import json, sys\nprint(json.dumps({'contract':'1.0','tool':'version','error':{'code':'boom','message':'bad'}}))\nsys.exit(1)\n")
        res = runner.run_tool(self.repo, "version")
        self.assertEqual(res.kind, "tool-error")
        self.assertIn("boom", res.message)

    def test_crash_without_json_is_tool_error(self):
        self.tool("raise SystemExit(3)\n")
        self.assertEqual(runner.run_tool(self.repo, "version").kind, "tool-error")

    def test_nonzero_exit_with_data_is_still_ok(self):
        self.tool("import json, sys\nprint(json.dumps(%r))\nsys.exit(1)\n" % ENVELOPE)
        self.assertIsInstance(runner.run_tool(self.repo, "version"), Ok)

    def test_output_over_cap_is_bad_output_and_process_gone(self):
        self.tool("import sys\nsys.stdout.write('x' * 5000)\nsys.stdout.flush()\nimport time; time.sleep(30)\n")
        t = time.monotonic()
        res = runner.run_tool(self.repo, "version", max_output=1000)
        self.assertEqual(res.kind, "bad-output")
        self.assertLess(time.monotonic() - t, 10)

    def test_timeout_kills_the_process_group(self):
        pidfile = self.repo / "child.pid"
        self.tool("import subprocess, sys, time\n"
                  "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
                  "open(%r, 'w').write(str(c.pid))\ntime.sleep(60)\n" % str(pidfile))
        res = runner.run_tool(self.repo, "version", timeout=1.5)
        self.assertEqual(res.kind, "timeout")
        pid = int(pidfile.read_text())
        for _ in range(50):
            if not alive(pid):
                break
            time.sleep(0.1)
        self.assertFalse(alive(pid), "child of the tool survived the timeout")

    def test_story_id_validated_and_placed(self):
        self.assertEqual(runner.argv_for("next-story", ("AP0104",))[1:], ["tools/next_step.py", "AP0104", "--json"])
        for bad in ((), ("AP0104; rm",), ("../x",), (1,)):
            with self.assertRaises(ValueError):
                runner.argv_for("story", bad)
        with self.assertRaises(KeyError):
            runner.argv_for("nope")

    def test_table_covers_the_eight_tools(self):
        self.assertEqual(set(runner.TOOLS), {"version", "next", "next-story", "backlog", "check", "plan", "journal", "story"})


def alive(pid):
    if os.name == "nt":
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:  # a zombie still answers kill(0)
        return Path("/proc/%d/stat" % pid).read_text().split()[2] != "Z" if Path("/proc").exists() else True
    except OSError:
        return False


if __name__ == "__main__":
    unittest.main()
