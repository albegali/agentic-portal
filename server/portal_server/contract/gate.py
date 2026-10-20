"""Version gate and the single call function for skeleton tools (hook point for a later cache; none today)."""
import os
import threading
from pathlib import Path

from portal_server.contract import CONTRACT_BUILT_FOR, runner
from portal_server.contract.runner import ContractError, Ok
from portal_server.contract.validator import UnsupportedSchemaKeyword, Validator, load_schemas

COMPATIBLE, INCOMPATIBLE, MISSING = "compatible", "incompatible", "missing"


def parse_version(text):
    """`1.2` or `1.2.3` -> (1, 2); None when it is not major.minor[.patch]."""
    try:
        parts = [int(p) for p in str(text).split(".")]
    except ValueError:
        return None
    return (parts[0], parts[1]) if len(parts) >= 2 and all(p >= 0 for p in parts) else None


def evaluate(version_data, built_for=CONTRACT_BUILT_FOR):
    """State and message from `wf.py version` data: same major, minor >= built-for; extra fields are ignored."""
    have, want = parse_version(version_data.get("contract")), parse_version(built_for)
    if have is None:
        return INCOMPATIBLE, "The skeleton reports no valid contract version (%r)." % version_data.get("contract")
    if have[0] != want[0]:
        return INCOMPATIBLE, "Skeleton contract %d.%d has a different major than the portal expects (%s)." % (*have, built_for)
    if have[1] < want[1]:
        return INCOMPATIBLE, "Skeleton contract %d.%d is older than the %s this portal was built for." % (*have, built_for)
    return COMPATIBLE, ""


def recovery(state, pin=None):
    """Proposal only (runnable is always False): executing it through an agent run waits for the runs epic."""
    target = pin or "<SKELETON_PIN>"
    if state == MISSING:
        summary = "The skeleton tools are missing in this repository."
        steps = ["Restore tools/ and schemas/ from the agentic-skeleton release pinned for this project (%s)." % target]
    else:
        summary = "The skeleton does not match the contract this portal supports."
        steps = ["Update or re-pin the skeleton to the pinned release (%s)." % target,
                 "Re-check from Settings once the files are in place."]
    return {"summary": summary, "steps": steps, "command": "git checkout %s -- tools schemas" % target, "runnable": False}


class Gate:
    def __init__(self, repo, built_for=CONTRACT_BUILT_FOR):
        self.repo, self.built_for = Path(repo), built_for
        self._lock = threading.RLock()
        self.state, self.message = MISSING, "not checked yet"
        self.skeleton_version = self.contract_version = None
        self._validator = None
        self.refresh()

    # -- state ---------------------------------------------------------------------------------------------
    def refresh(self):
        """Re-read `wf.py version --json` and recompute the state (start, Settings re-check, after a failed call)."""
        with self._lock:
            self.skeleton_version = self.contract_version = None
            self._validator = None
            res = self._run("version")
            if isinstance(res, ContractError):
                self.state = MISSING if res.kind == "missing-tool" else INCOMPATIBLE
                self.message = ("The skeleton tools are missing: %s" if self.state == MISSING
                                else "The skeleton version cannot be read: %s") % res.message
                return self.snapshot()
            data = res.data
            self.skeleton_version, self.contract_version = data.get("skeleton"), data.get("contract")
            self.state, self.message = evaluate(data, self.built_for)
            return self.snapshot()

    def snapshot(self):
        with self._lock:
            return {"state": self.state, "message": self.message, "built_for": self.built_for,
                    "skeleton_version": self.skeleton_version, "contract_version": self.contract_version,
                    "recovery": None if self.state == COMPATIBLE else recovery(self.state, os.environ.get("SKELETON_PIN"))}

    # -- calls ---------------------------------------------------------------------------------------------
    def call(self, tool, *args):
        """Ok(envelope) or ContractError. Refuses while not compatible; re-reads the version after a failed call."""
        with self._lock:
            if self.state != COMPATIBLE:
                return ContractError("incompatible", self.message)
        res = self._run(tool, *args)
        if isinstance(res, ContractError):
            self.refresh()
        return res

    def _run(self, tool, *args):
        res = runner.run_tool(self.repo, tool, args)
        if isinstance(res, ContractError):
            return res
        problems = self._violations(res.envelope, tool)
        if isinstance(problems, ContractError):
            return problems
        if problems:
            return ContractError("bad-output", "%s output violates its schema: %s" % (tool, "; ".join(problems[:3])))
        return res

    def _violations(self, envelope, tool):
        try:
            if self._validator is None:
                self._validator = Validator(load_schemas(self.repo / "schemas"))
            found = self._validator.errors(envelope, "envelope.schema.json")
            return found or self._validator.errors(envelope, "%s.schema.json" % tool)
        except (OSError, KeyError, ValueError, UnsupportedSchemaKeyword) as exc:
            return ContractError("incompatible", "cannot load the skeleton schemas: %s" % exc)


# One gate per repository root, shared by the routes (the route table is static, see app.py).
_GATES = {}
_GATES_LOCK = threading.Lock()


def bind(root, repo=None):
    """Create (and read the version for) the gate of `root`; `repo` is where the skeleton lives (default: root)."""
    gate = Gate(repo or root)
    with _GATES_LOCK:
        _GATES[Path(root)] = gate
    return gate


def gate_for(root):
    with _GATES_LOCK:
        gate = _GATES.get(Path(root))
    return gate if gate is not None else bind(root)
