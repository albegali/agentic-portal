# BRIEF-AP0105 - Upstream: gates.py

## References
- Story ID: AP0105
- Source: `analysis/30-refined/REFINED_AP0105_upstream_gates_tool.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-20T22:24
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime):

---

## Status
Refined into Spec

---

## Type
Feature

---

## Urgency (Optional)
High

---

# 1. Original Customer Intent

As a portal (consumer of agentic-skeleton), I want a gates.py tool that lists pending human gates and records approve or request-changes exactly as a human edit, attributed to the project.toml owner with date, so that the portal never edits workflow files directly.

---

# 2. Initial Goal

Add `gates.py` to the agentic-skeleton as a contract minor: `list --json` shares one gate detection with `next_step.py`; `approve` and `request-changes` change only the gate field and add one line to a `## Gates` section of the artifact.

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Delivered in the agentic-skeleton repository (NFR-14); AI implements and tags, human + AI review.
- ADR-002 (later minor `gates`, revision 2026-10-20), ADR-006 (gate endpoints, confirm nonce and caller checks are EP-04, not here); FR-13, FR-14, NFR-03, NFR-14.
- Workshop 2026-10-20 decisions: ids `<type>:<artifact path>`; owner from `project.toml` (`--by` accepted only if equal); stale, unknown and invalid actions refused; `WF_AGENT=1` guard (low confidence, may be dropped in the Spec).
- State of the skeleton: `next_step.py` computes gates in `inception()` and `stage()` (`human_gates` in `--json`); contract 1.0, `tools/VERSION` 1.3.0.
- Depends on AP0103 (done); AP0109 tag `v1.3.0` still pending. Consumed by AP0401 (inbox) and the runs epic.

---

# 5. Known Constraints

- Only in agentic-skeleton; stdlib only; Python >= 3.11 (CI on 3.11 and 3.14); no local modification of skeleton files in this repository.
- `next_step.py --json` output keeps its shape.
- Out of scope: portal UI, agent-caller checks, confirm nonce, journal entries and sidecar files.

---

# 6. Expected Fix (Optional)

Gate catalog (type, artifact, field, current/proposed values) and shared detection module; `gates.py list|approve|request-changes`; edit mechanics (atomic, CRLF preserved); `## Gates` section in the templates; schema `gates` and contract minor 1.1; tests; `tools/README.md`.

---

# 7. Open Questions

- Per-gate field and value table (Spec §10, from the skeleton step files and templates).
- `## Gates` for TOML artifacts (`backlog/stories.toml`, `project.toml`); gate resolution for `workshop` and `tuning`; `check_workflow` allowance for the new section (Spec §10).

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.  
> Add clarifications here.

- Addendum 2026-10-21 (re-scope): skeleton 1.17.3 already ships `tools/gates.py` (catalog, library only), `tools/approve.py` and the `gate_guard.py` hook. The tool is therefore a CLI added to the existing `gates.py`: `list --json` over a shared pending detection, `approve` as a wrapper over `make approve` code (owner and date in commit trailers), `request-changes` writing the draft value and a `## Gates` line. The `## Gates` line on approve and the `WF_AGENT` guard are proposed to be dropped; owner confirmation at the Spec gate (SPEC §10).

---

# 9. Derived Artifacts

- Spec: SPEC-AP0105
- RUN: RUN-AP0105
