# RUN-AP0103

## References
- Story ID: AP0103
- Spec: SPEC-AP0103
- Started at (datetime): 2026-10-19T22:10
  - Fill only when execution starts after human approval, immediately before the first code or test change.
- Completed at (datetime): 2026-10-20T10:00
  - Fill only when the RUN is ready to close after verification, tuning and persistence.
  - If tuning or follow-up changes happen before closure, update this to the latest completion datetime.

---

## Status
Closed

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

---

# 3. Execution Log (Agent)

### Steps
- Step 1 (TSK-02, 04): `wf.CONTRACT_VERSION = "1.0"`, `wf.dump_envelope`, `wf.fail_envelope` (error envelope, no `data`, exit 1); `next_step.py --json` (`next`, `next-story`) in the envelope, fields unchanged under `data`; `dump_json` kept for tools not yet migrated (AP0109).
- Step 2 (TSK-03): `wf.py version [--json]` (skeleton version + contract version).
- Step 3 (TSK-05, 06): 9 schema files in `schemas/` (JSON Schema 2020-12): `envelope`, `version`, `next`, `next-story`, `backlog`, `check`, `plan`, `journal`, `story`.
- Step 4 (TSK-07): `tools/tests/test_contract.py` (9 tests: samples valid/invalid, extra fields, error envelope, empty states, major pinned, tools emit valid envelopes, version command, failure exit code).
- Step 5 (TSK-08): CI matrix Python 3.11 and 3.14 with `jsonschema` and `WF_REQUIRE_JSONSCHEMA=1`; "JSON contract" section of `tools/README.md` rewritten.
- Step 6 (TSK-09): committed in agentic-skeleton (73c5f4c, merged as ad43875); no tag (see §9).

### Changes (high-level)
- Code: agentic-skeleton `tools/wf.py`, `tools/next_step.py`, `tools/adopt.py`; merged into this repository from the `skeleton` remote.
- Interfaces: `--json` envelope, error envelope, `schemas/`, contract 1.0.
- Domain: none.
- Tests: `tools/tests/test_contract.py`, `tools/tests/test_workflow.py` (envelope assertions).
- Specs: ADR-002 (contract table, Python baseline, version file), Spec §10/§11.

---

# 4. Verification

- Build: OK
- Tests: OK (portal: 30 tools tests on 3.12 with contract tests required; skeleton: 29 on 3.12; `make test`/`make lint` OK on 3.14; `make check` OK)
- Interfaces / target platforms: contract tests skipped on local 3.14 (no `jsonschema` there); Python 3.11 not available locally; CI on 3.11/3.14 not run (not pushed)
- Manual (if any): n/a

Notes:
- AC1-AC4 and AC6 verified locally; AC5 (CI green, tag) pending push and the end of AP0109.

---

# 5. Tuning Log (If needed)

> Only within scope.

### Entry #1
- Issue: review 2026-10-20: `VERSION` merge conflict (the skeleton's file collided with the portal's own `VERSION`); `make test-tools` failed 7 tests in this repository (fixture copied the portal's project state and `node_modules`); `next-story` contract check was conditional and never ran; AC4 test did not tie the schemas to `wf.CONTRACT_VERSION`.
- Fix: skeleton version moved to `tools/VERSION` (`wf.py`, `adopt.py`, README, ADR-002); `Repo` test fixture resets its copy to a fresh skeleton and skips `node_modules`; unconditional `next-story` check; major pinned against `wf.CONTRACT_VERSION`. Same edits in agentic-skeleton, branch `fix/tools-version-fresh-fixture`.
- Impact: tools suite 205 s → 14 s; `workflow-check` expected green on `main`.
- Verified: Yes (locally)

---

# 6. Deviations

- What changed: (1) tools keep Python >= 3.11 (Spec/ADR-002 said 3.14); (2) `v1.0.0` tag and the CI part of AC5 move to the end of AP0109; (3) `adopt.py` also installs `tools/VERSION` and `schemas/`; (4) breaking change of `next_step.py --json` (flat `"schema": 1` → envelope).
- Why: owner decisions 2026-10-19 (1, 2, 4); installing version and schemas keeps adopted repositories in step with the contract (3); (1) also applies the 2026-10-20 version file location.
- Scope impact: None (all approved by the owner; Spec §10 and ADR-002 reconciled)

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- Spec §4 ticked (AC5 marked as deferred), §10/§11 updated; Brief §9 and "Closed at" set; ADR-002 revised (2026-10-19 and 2026-10-20); `architecture.md` has no reference to the touched items, no change; specs index updated.

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied (AC5 deferred to AP0109 by the owner)
- [x] Tests passing
- [x] No scope creep
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0103-01 to TSK-AP0103-08

Tasks deferred:
- TSK-AP0103-09 (tag `v1.0.0`) and CI-green confirmation: after AP0109, once every v1.0 tool emits the envelope.

Goal achieved:
- [ ] Yes
- [x] Partial
- [ ] No

Summary:
- Envelope, error envelope, `wf.py version`, `next_step.py --json` and the 9 schemas with contract tests are delivered and verified locally; release tag and CI confirmation remain.

---

# 10. Next Steps

- Follow-ups: commit and push the portal merge and the agentic-skeleton fix branch, confirm `workflow-check` on 3.11 and 3.14; AP0109 (remaining `--json` tools, then tag `v1.0.0`); AP0104 (portal contract client).
- Risks: `plan`, `journal`, `story` schemas precede their emitters and may need an additive minor; this repository's docs say Python >= 3.14 while the skeleton baseline is 3.11.
- Improvements: install `jsonschema` for 3.14 locally so the contract tests do not skip.
