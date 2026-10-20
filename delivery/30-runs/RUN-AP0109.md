# RUN-AP0109

## References
- Story ID: AP0109
- Spec: SPEC-AP0109
- Started at (datetime): 2026-10-20T21:50 (approx.)
  - Fill only when execution starts after human approval, immediately before the first code or test change.
- Completed at (datetime): 2026-10-20T22:03
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
- [x] Target Spec (`SPEC-AP0109`, §10 decisions owner-confirmed in chat 2026-10-20)
- [x] Scoped package `AGENTS.md` files, if applicable:
  - none: all code changes are in agentic-skeleton `tools/`, which has no package `AGENTS.md`; `server/AGENTS.md` read only for the AP0104 consumer (not touched)
- [x] `delivery/templates/RUN-template.md`, `delivery/guide/run.md`, ADR-002

Findings (TSK-AP0109-01, read-only inspection of `../agentic-skeleton`, `main` at `bb8a28a`, clean):
- `wf.py` has `dump_envelope`/`fail_envelope`, `CONTRACT_VERSION = "1.0"`, `sprints()`, `stories()`, `md_status()`, `artifact_status()`; `main()` handles `version`. `dump_json` is also used by `context.py` (stays).
- `gen_backlog.py --json` and `check_workflow.py --json` print flat JSON via `wf.dump_json`; only consumer outside tests: the portal's AP0104 runner (expects the envelope).
- `schemas/plan|journal|story.schema.json` exist (AP0103); `tests/test_contract.py` validates samples and the live `next`/`next-story`/`version` output on a temp `Repo()` fixture.
- CI: `.github/workflows` matrix 3.11/3.14 with `WF_REQUIRE_JSONSCHEMA=1`, `make check` + `make test-tools`.
- Existing tags: `v1.1.0`, `v1.1.1`; `tools/VERSION` = 1.2.0 (untagged). No `v1.0.0`.
- PLAN.md sprint table has no release column; release table columns: `Release | Content | Target | Exit criterion`.

### Plan
- Step 1 (branch): in agentic-skeleton, branch `ap0109-upstream-json-read-tools` from `main`.
- Step 2 (TSK-02): `gen_backlog.py --json` → `wf.dump_envelope("backlog", …)`; malformed TOML → `fail_envelope("backlog", "bad_input", …)`. `check_workflow.py --json` → `dump_envelope("check", …)`, exit 1 kept when errors > 0. Docstrings updated.
- Step 3 (TSK-03): `wf.py plan --json` — `releases`: rows of the PLAN.md release table (`id`, `title` = Content, `goal` = Exit criterion, extra `target`, `sprints`); `sprints`: `wf.sprints()` + `release` = the release of their stories in `stories.toml` (first one in the row; omitted when none). No PLAN.md → empty lists.
- Step 4 (TSK-04): `wf.py journal --json` — `context`: concatenated text of `project-journal/context/*.md` except `README.md`, else `null`; `decisions`, `learnings`, `weekly`, `monthly`: `.md` files except `README.md`, sorted by name, items `file`, `title` (first `# ` heading), `date` (frontmatter `date`, else `YYYY-MM-DD` in the file name, else omitted).
- Step 5 (TSK-05): `wf.py story <ID> --json` — `id`, `title` (stories.toml), `stage` (reuse `next_step.stage()` by import), `artifacts` (each existing story/analysis/refined/brief/spec/run with `path` and `status` from `wf.artifact_status`), `tasks` (`TSK-<ID>-NN` lines of Spec §5 with title; `status` = `done`/`deferred` when listed in RUN §9 "Tasks completed"/"Tasks deferred", else `open`). Unknown ID → `fail_envelope("story", "unknown_id", …)`, exit 1. The `artifacts()` helper moves from `gen_backlog.py` to `wf.py` (shared, no behaviour change).
- Step 6 (TSK-06): `test_contract.py`: live output of all five tools validated against schema + envelope on a populated `Repo()` (through inception, with a sprint, a journal weekly, a Spec with tasks and a RUN) and on an empty one; error cases (unknown ID, malformed TOML); `check --json` exit code; plain text of `gen_backlog.py`, `check_workflow.py`, `next_step.py` unchanged (compare before/after on the same fixture).
- Step 7 (TSK-07): `tools/README.md` contract table (commands, fields; remove "flat for now"/"schema only"); `make check` and `make test-tools` on local Python 3.12 and 3.14 (as AP0103).
- Step 8 (TSK-08, after human review): bump `tools/VERSION`, push branch, CI green on 3.11/3.14 + macOS/Windows launcher job, merge to skeleton `main`, tag (see Q1). Then portal-side: delivery artifacts of AP0109 on portal branch `ap0109-upstream-json-read-tools` at `/persist`.

### Assumptions
- Text (non-JSON) output of all tools stays byte-identical; only `--json` changes (AC4).
- Schemas are not changed; extra fields (`target`, `content`) rely on `additionalProperties: true` (no minor bump).
- `next_step.py` imports cleanly from `wf.py` lazily (inside the `story` branch) without side effects.
- The portal's `tools/` copy is updated later through the skeleton release (NFR-14: not edited here).

### Risks / Open Questions
- Q1 (owner, at approval): tag name. ADR-002 says "`v1.0.0` follows AP0109", but the skeleton already has `v1.1.0`/`v1.1.1` and `tools/VERSION` 1.2.0, so `v1.0.0` would sort below existing tags. Proposal: bump `tools/VERSION` to **1.3.0** and tag `v1.3.0` (contract stays `1.0`); ADR-002 and SPEC-AP0103 AC5 reconciled at `/persist` with a revision line.
- R1: AP0104's uncommitted runner (`server/portal_server/contract/runner.py`) calls `tools/plan.py`, `tools/journal.py`, `tools/story.py`; with the confirmed decision they become `tools/wf.py plan|journal|story …`. Fixed inside AP0104 (its RUN), not here; noted in §10 at persistence.
- R2: Markdown/TOML layouts of PLAN.md and journal are free text; parsing is best-effort and covered by tests on the template layouts only.
- R3: the CI "launcher" job on Windows was flaky in AP0110; a red unrelated job stops the merge (AGENTS.md §3).

### Scoped Agent Rules Check
- Applies: No (no package `AGENTS.md` in skeleton `tools/`)
- Files read:
  - `server/AGENTS.md` (consumer context only; no change)
- Notes:
  - No changes in this repository except delivery artifacts.

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
- Q1: tag `v1.3.0` with `tools/VERSION` 1.3.0, contract stays `1.0` (owner, chat 2026-10-20).

Reviewer: Alberto Galimberti
Date: 2026-10-20

---

# 3. Execution Log (Agent)

### Steps
- Step 1: skeleton branch `ap0109-upstream-json-read-tools` from `main` (`bb8a28a`).
- Step 2 (TSK-02): `gen_backlog.py --json` and `check_workflow.py --json` print the envelope; malformed input → error `bad_input`; `check` exit 1 on workflow errors kept.
- Step 3 (TSK-03): `wf.py plan --json` (`releases()`, `sprints_with_release()`).
- Step 4 (TSK-04): `wf.py journal --json` (`journal()`, `journal_entries()`).
- Step 5 (TSK-05): `wf.py story <ID> --json` (`story_chain()`, `tasks()`, `task_ids()`); `artifacts()` moved from `gen_backlog.py` to `wf.py` (pattern table `CHAIN`). RUN §9 ranges (`TSK-X-01 to TSK-X-08`) handled: found on this repo's RUN-AP0103.
- Step 6 (TSK-06): contract tests: populated repo (all five tools, values asserted), empty repo, errors (unknown ID, malformed TOML for backlog/check/plan/story, check with workflow errors); `test_workflow.py` reads `data` of the new envelopes.
- Step 7 (TSK-07): `tools/README.md`: `wf.py` row, contract table (no more "flat for now"/"schema only"), error codes, migration note; `tools/VERSION` 1.3.0 (Q1). Not committed, not pushed (TSK-08 waits for review).

### Changes (high-level)
- Code: agentic-skeleton `tools/wf.py`, `tools/gen_backlog.py`, `tools/check_workflow.py`, `tools/VERSION`
- Interfaces: `--json` envelopes `backlog`, `check`, `plan`, `journal`, `story`; error codes `unknown_id`, `bad_input`, `usage`; schemas unchanged
- Domain: n/a
- Tests: `tools/tests/test_contract.py` (+3 tests), `tools/tests/test_workflow.py` (envelope `data`)
- Specs: none (Spec §10 decisions recorded before execution)

---

# 4. Verification

- Build: OK (`compileall`, `make check` in the skeleton)
- Tests: OK — 63 tests, `WF_REQUIRE_JSONSCHEMA=1`, on Python 3.12 and 3.14 (venv with `jsonschema`); 3.11 and CI pending push
- Interfaces / target platforms: OK — text output of `gen_backlog.py --deps`, `check_workflow.py`, `next_step.py` (+ `<ID>`), `wf.py version` byte-identical to `main` on this repository (AC4); macOS/Windows via CI after push
- Manual (if any): OK — all five tools run against this repository (`WF_ROOT`): valid envelopes; `story AP0103` tasks 01–08 done, 09 deferred

Notes:
- AC1–AC4 met locally; AC5 needs push, CI green and the `v1.3.0` tag (TSK-08, after your review).

If FAIL → move to Tuning.

---

# 5. Tuning Log (If needed)

> Only within scope.

---

# 6. Deviations

- What changed:
- Why:
- Scope impact: None / Minor / Requires approval

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- Spec §10/§11 and AC reconciled (tag `v1.3.0`; AC5 open on the tag only). Index row set to Done.
- ADR-002: stale sentence about the flat outputs and `v1.0.0` corrected, revision line added (owner decision Q1). SPEC-AP0103: AC5 and §11 note the CI part and the new tag name.
- Tuning: none needed.

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied (AC5: tag pending the owner)
- [x] Tests passing (63 locally on 3.12/3.14; CI green on 3.11, 3.14, macOS, Windows)
- [x] No scope creep
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0109-01 to TSK-AP0109-07

Tasks deferred:
- TSK-AP0109-08 (tag `v1.3.0`): push, CI and merge done; the tag waits for the owner's explicit approval.

Goal achieved:
- [ ] Yes
- [x] Partial
- [ ] No

Summary:
- All five read tools emit the contract 1.0 envelope and are merged in agentic-skeleton `main` (`d00c402`); only the release tag is pending.

---

# 10. Next Steps

- Follow-ups: owner approves the tag, then `git tag v1.3.0 d00c402 && git push origin v1.3.0` in agentic-skeleton (or ask the agent); AP0104 sets `SKELETON_PIN` to `v1.3.0` and switches its runner to `tools/wf.py plan|journal|story`.
- Risks: until the tag exists AP0104's CI job `contract` has no pin to check out.
- Improvements: none.

---

# 11. Addendum (Post-Closure Only)
