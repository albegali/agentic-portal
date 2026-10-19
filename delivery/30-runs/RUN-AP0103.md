# RUN-AP0103

## References
- Story ID: AP0103
- Spec: SPEC-AP0103
- Started at (datetime): 2026-10-19T22:10
  - Fill only when execution starts after human approval, immediately before the first code or test change.
- Completed at (datetime): 2026-10-19T22:30
  - Fill only when the RUN is ready to close after verification, tuning and persistence.
  - If tuning or follow-up changes happen before closure, update this to the latest completion datetime.

---

## Status
Persisted

> A RUN MUST NOT be Closed before Persisted.

---

# 1. Execution Strategy (Agent)

> MUST be written before any code.

### Required Reads
- [x] Target Spec
- [x] Scoped package `AGENTS.md` files, if applicable:
  - none apply: the work is in `../agentic-skeleton` (its root `AGENTS.md` only; no `tools/AGENTS.md`). `server/AGENTS.md` and `web/AGENTS.md` are not touched.
- [x] `delivery/templates/RUN-template.md`

### Findings from the skeleton (TSK-AP0103-01, read-only inspection of `../agentic-skeleton`, branch `main`, ahead of origin by 2)
- `tools/wf.py` already has `SCHEMA = 1` and `dump_json()`, which prints a flat `{"schema":1, ...fields}`. Used by `next_step.py`, `check_workflow.py`, `gen_backlog.py`, `context.py`, `repo_map.py`; documented in `tools/README.md` "JSON contract".
- `wf.py` is a helper module (no CLI, no `version` command, no `VERSION` file). No git tags. Tests: `tools/tests/test_workflow.py` (unittest, `make test-tools`).
- CI: `.github/workflows/workflow-check.yml` on Python 3.12 (`make check`, `make test-tools`). Baseline stated as Python >= 3.11 (Makefile, wf.py docstring).
- `check_workflow.py --json` and `gen_backlog.py --json` already exist in the flat form, so AP0109 is partly done upstream already; the contract still needs them in the envelope.

### Plan
- Step 1 (TSK-02, 04): add `wf.CONTRACT_VERSION = "1.0"`, `wf.dump_envelope(tool, data)` and `wf.fail(tool, code, message)` (error envelope, no `data`, exit 1). Switch `next_step.py --json` (both forms) to the envelope, with the existing fields unchanged under `data`. Keep `dump_json` for tools not yet migrated (AP0109 migrates them). Verify: unit tests on output shape and exit codes.
- Step 2 (TSK-03): `wf.py` becomes runnable (`python3 tools/wf.py version [--json]`) and reports the skeleton version (new root `VERSION`) and the contract version. Text form prints one line. Importing `wf` stays unchanged.
- Step 3 (TSK-05, 06): `schemas/` (JSON Schema 2020-12): `envelope`, `version`, `next` (+ `next-story` for `next_step.py <ID>`), `backlog`, `check`, `plan`, `journal`, `story`. Shapes for `backlog` and `check` follow today's `gen_backlog` and `check_workflow` output; `plan`, `journal` and `story` are derived from the ADR-002 table and the Markdown/TOML sources. `data` objects use `additionalProperties: true` (minors only add fields).
- Step 4 (TSK-07): schema tests in `tools/tests/` using `jsonschema` (test dependency, skipped locally with a clear message if absent; required in CI). Samples for every schema, valid, invalid, error and empty states, plus a test that every schema pins `contract` to major 1. Verify: `make test-tools`.
- Step 5 (TSK-08): CI matrix Python 3.11 and 3.14 (baseline stays >= 3.11, owner 2026-10-19), install `jsonschema` for the tests; document the contract in `tools/README.md` (replacing the "JSON contract" section, the breaking change and migration from `"schema": 1` noted).
- Step 6 (TSK-09): commit on a branch in the skeleton; stop for human review. No tag in this RUN: `v1.0.0` is tagged at the end of AP0109, when every v1.0 tool emits the envelope (recommendation, avoids a release whose schemas `check`/`backlog` do not yet match). AC5's "tagged release exists" is then deferred to AP0109 and logged in §6. I never push or tag myself.

### Assumptions
- Replacing `"schema": 1` with the envelope for `next_step.py --json` is accepted (owner, 2026-10-19). Consumers in the skeleton: only `tools/tests/test_workflow.py` and `tools/README.md`; adopted repos keep their copied tools until they update.
- `VERSION` file with `1.0.0` is the source of the skeleton version; the git tag mirrors it.
- Tool names are the schema names (`next`, `backlog`, `check`, `plan`, `journal`, `story`, `version`).
- Python 3.11 and 3.14 interpreters available locally, or CI is the 3.14 check (verified at execution time).

### Risks / Open Questions
- Breaking change of `next_step.py --json`: approved by the owner (2026-10-19). Residual: scripts in adopted repos reading `"schema": 1` break when they update the skeleton (documented in the README).
- Python baseline stays >= 3.11 (owner, 2026-10-19), against ADR-002 and Spec §3 ("Python 3.14"): logged as a deviation in §6 at execution; ADR-002 and Spec reconciled in persistence. The portal launcher (AP0106) keeps requiring 3.14.
- Tag timing: tagging after AP0109 defers part of AC5; if the owner prefers tagging here, Step 6 tags `v1.0.0` with `check`/`backlog` still flat (mixed state).
- The skeleton `main` is 2 commits ahead of origin: work goes on a branch from the current `main`; the human decides the merge and push order.
- `jsonschema` availability on the 3.14 CI runner (pip install); no runtime dependency.
- Schemas for `plan`, `journal` and `story` are written before their emitters exist (AP0109), so the shapes might need an additive minor later.

### Scoped Agent Rules Check
- Applies: Yes (root `AGENTS.md` of agentic-skeleton)
- Files read:
  - `../agentic-skeleton/AGENTS.md` (listed, not required beyond the workflow rules above), `tools/wf.py`, `tools/README.md`, `.github/workflows/workflow-check.yml`, `Makefile`
- Notes:
  - Changes stay in agentic-skeleton; this repository only gets delivery artifacts until persistence.

---

# 2. Human Approval

- [x] Strategy reviewed
- [x] Scope correctly understood
- [x] No out-of-scope work detected

Decision:
- [x] Approved
- [ ] Revisions requested
- [ ] Stopped

Notes:
- 2026-10-19 owner decisions; strategy approved with `/run AP0103 approve` (no "tag here" given: no tag in this RUN): breaking change of `next_step.py --json` approved; skeleton stays on Python >= 3.11.

Reviewer: Alberto Galimberti
Date: 2026-10-19
