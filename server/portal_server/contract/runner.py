"""Run one skeleton tool through its `--json` envelope: no shell, own process group, timeout, output cap."""
import json
import os
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

TIMEOUT_S = 30
MAX_OUTPUT = 5 * 1024 * 1024

# tool name -> argv after the interpreter; "{id}" is filled from the call arguments.
# The only commands the portal runs for project state (allow-list, server/AGENTS.md).
TOOLS = {
    "version": ["tools/wf.py", "version", "--json"],
    "next": ["tools/next_step.py", "--json"],
    "next-story": ["tools/next_step.py", "{id}", "--json"],
    "backlog": ["tools/gen_backlog.py", "--json"],
    "check": ["tools/check_workflow.py", "--json"],
    "plan": ["tools/wf.py", "plan", "--json"],
    "journal": ["tools/wf.py", "journal", "--json"],
    "story": ["tools/wf.py", "story", "{id}", "--json"],
}
KINDS = ("incompatible", "missing-tool", "tool-error", "bad-output", "timeout")


@dataclass(frozen=True)
class Ok:
    envelope: dict

    @property
    def data(self) -> dict:
        return self.envelope["data"]


@dataclass(frozen=True)
class ContractError:
    kind: str
    message: str


def argv_for(tool: str, args: tuple = ()) -> list:
    """Interpreter + script + fixed arguments; raises KeyError for an unknown tool, ValueError for a bad id."""
    template = TOOLS[tool]
    ident = args[0] if args else None
    if "{id}" in template:
        if not isinstance(ident, str) or not ident.isalnum():
            raise ValueError("tool %r needs an alphanumeric story id" % tool)
    return [sys.executable] + [ident if part == "{id}" else part for part in template]


def kill_group(proc: subprocess.Popen) -> None:
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, check=False)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, ProcessLookupError):
        pass
    try:
        proc.kill()
    except OSError:
        pass


def run_tool(repo: Path, tool: str, args: tuple = (), timeout: float = TIMEOUT_S, max_output: int = MAX_OUTPUT):
    """Return Ok(envelope) or ContractError. The process (group) is gone when this returns."""
    argv = argv_for(tool, args)
    script = Path(repo) / argv[1]
    if not script.is_file():
        return ContractError("missing-tool", "%s not found in the repository" % TOOLS[tool][0])
    popen_kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    try:
        proc = subprocess.Popen(argv, cwd=str(repo), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, env={**os.environ, "PYTHONUTF8": "1"}, **popen_kw)
    except OSError as exc:
        return ContractError("missing-tool", "cannot start %s: %s" % (TOOLS[tool][0], exc))
    chunks, size, overflow = [], 0, threading.Event()

    def pump():
        nonlocal size
        while chunk := proc.stdout.read1(65536):
            size += len(chunk)
            if size > max_output:
                overflow.set()
                kill_group(proc)
                return
            chunks.append(chunk)

    reader = threading.Thread(target=pump, daemon=True)
    reader.start()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_group(proc)
        proc.wait()
        reader.join()
        proc.stdout.close()
        return ContractError("timeout", "%s did not finish within %d s" % (TOOLS[tool][0], timeout))
    reader.join()
    proc.stdout.close()
    if overflow.is_set():
        return ContractError("bad-output", "%s output over %d bytes" % (TOOLS[tool][0], max_output))
    return parse(tool, proc.returncode, b"".join(chunks))


def parse(tool: str, code: int, raw: bytes):
    try:
        envelope = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        if code != 0:
            return ContractError("tool-error", "%s exited with %d" % (tool, code))
        return ContractError("bad-output", "%s did not print JSON" % tool)
    if not isinstance(envelope, dict):
        return ContractError("bad-output", "%s printed JSON that is not an object" % tool)
    err = envelope.get("error")
    if isinstance(err, dict) and "data" not in envelope:
        return ContractError("tool-error", "%s: %s" % (err.get("code", "error"), err.get("message", "")))
    if "data" not in envelope:
        return ContractError("bad-output" if code == 0 else "tool-error", "%s printed no envelope" % tool)
    return Ok(envelope)  # a non-zero exit with data is valid (check reports problems that way)
