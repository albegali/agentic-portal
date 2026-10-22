# RUN-AP0105

## References
- Story ID: AP0105
- Spec: SPEC-AP0105
- Started at (datetime): 2026-10-21T18:06
  - Fill only when execution starts after human approval, immediately before the first code or test change.
- Completed at (datetime): 2026-10-22T03:07
  - Fill at `/close`, after the review.
- Branch:            ap0105-upstream-gates-tool (portal: story branch created at approval; skeleton: `feat/ap0105-gates-cli` from `main`, in ~/projects/agentic-skeleton)
- Upstream:          only for a story with `repo = "<name>"` in stories.toml: the commit or tag in that repository
- PR:                portal: https://github.com/albegali/agentic-portal/pull/10; skeleton: https://github.com/albegali/agentic-skeleton/pull/41 (branch `feat/ap0105-gates-cli`, commit 52b71f5)

---

## Status
Persisted

Draft → Strategy Approved → Executing → Tuning → Persisted → Reviewed → Closed  ·  Stopped / Blocked / Cancelled

> A RUN MUST NOT be Closed before Persisted and Reviewed (§11).
> Stopped: the human stopped it at §2 (resume with `/run AP0105 revise: …`). Blocked: a §6 deviation awaits approval
> (`/run AP0105 approve-deviation <n>`). Cancelled: the story was dropped (`/run AP0105 cancel: …`); terminal.

---

# 1. Execution Strategy (Agent)

> MUST be written before any code.

### Required Reads
- [x] Target Spec
- [x] Scoped package `AGENTS.md` files, if applicable:
  - server/AGENTS.md (contract rules; no portal code changes in this story)
- [x] `delivery/templates/RUN-template.md`

### Plan
Work happens in the agentic-skeleton repo (NFR-14); the portal repo only gets this RUN and persistence edits (ADR-002, FR notes).
- TSK-AP0105-01: branch `feat/ap0105-gates-cli` from skeleton `main` (1.17.3); read `gates.py` (`passed`, `approve`), `approve.py`, `next_step.py` (`stage`, `recommend` → `human_gates`), `gate_guard.py`, templates, `check_workflow.py`, schemas; record the confirmed per-gate table (detection, field, approved/draft value) in §3.
- TSK-AP0105-02: move pending-gate detection into `gates.py` (`pending()` returning gate name, artifact, field, current, proposed, story id), `next_step.py` calls it; id `<gate>:<path>`, `workshop` list-only, `since` from `git log -1` on the artifact, fallback mtime; `list --json` via `wf.emit`. Check `next_step.py --json` output byte-identical before/after on fixtures.
- TSK-AP0105-03: extract apply-and-commit from `approve.py` into `gates.py`; `approve.py` and the new `approve` subcommand both call it; owner from `project.toml`, `--by` only if equal, `--expect` stale check, diff in `data`; no git → set field, no commit.
- TSK-AP0105-04: `request-changes`: per-gate draft value as single-field edit, one `## Gates` line (md) or `# Gates` comment block (TOML), temp file + `os.replace`, bytes/CRLF preserved; unsupported gates → `invalid_transition`; add `gate_guard.py` rule for `gates.py approve|request-changes`.
- TSK-AP0105-05: add `## Gates` section to the templates that can receive a line; adjust `check_workflow` only if a template or check fails.
- TSK-AP0105-06: `schemas/gates.schema.json` (list and action results, additive), `CONTRACT_VERSION` 1.1, `tools/VERSION` 1.18.0, `tools/README.md` (table, amended read-only sentence), CHANGELOG.
- TSK-AP0105-07: tests in `tools/tests` (populated, empty, each error code, CRLF, no-git, `make approve` unchanged, schema validation with `jsonschema`); run full suite on Python 3.11 and 3.14 locally if available, then CI via PR.
- TSK-AP0105-08: push the branch and open the skeleton PR, wait for CI; stop before merge and tag (human approval). Portal side: record the upstream commit in this RUN; ADR-002 / FR-13/FR-14 reconciliation only in persistence.

### Assumptions
- Skeleton 1.17.3 is the baseline and the working tree of `~/projects/agentic-skeleton` is clean on `main`.
- Gate catalog in Spec §10 matches the code; any difference is logged in §3 and, if it changes scope, raised as a deviation.
- Spec §10 doubts 1–5 are settled by the Spec being `Ready` (approve like `make approve`, commit on current branch, request-changes limited, version 1.18.0 / contract 1.1, owner attribution).
- Tests use fixture repositories in temp dirs; no `approve` / `request-changes` against real repos.

### Risks / Open Questions
- Moving detection out of `next_step.py` may alter `human_gates` ordering or text; mitigated by a before/after snapshot comparison.
- `## Gates` in templates could trip `check_workflow` heading rules or template consumers (stop condition).
- Python 3.11 vs 3.14 differences (only 3.14 may be installed locally); CI is the check.
- Stale detection for `workshop` and combined gates (strategy touches RUN and Spec) needs one atomic multi-file apply; roll back on partial failure.
- The tag and the portal's `SKELETON_PIN` bump are outside this story and wait for the owner.

### Scoped Agent Rules Check
- Applies: Yes (skeleton repo has its own tool conventions; portal `server/AGENTS.md` not touched)
- Files read:
  - server/AGENTS.md
  - reference/architecture/ADR-002-skeleton-contract.md
- Notes:
  - Skeleton `AGENTS.md` / `tools/README.md` are read in TSK-01 before any change there.

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
- …

Reviewer: Alberto Galimberti
Date: 2026-10-21

---

# 3. Execution Log (Agent)

### Steps
Skeleton repo `~/projects/agentic-skeleton`, branch `feat/ap0105-gates-cli` from `main` (1.17.3), commit 52b71f5 (local, not pushed).
- TSK-01: read `gates.py`, `approve.py`, `next_step.py`, `gate_guard.py`, templates, schemas. Catalog in Spec §10 matches the code (`passed`/`approve`); detection of pending gates sits in `next_step.inception()` / `stage()`.
- TSK-02: `gates.pending()` built on `next_step.inception()` and `recommend()["human_gates"]` (same detection; `next_step.py --json` untouched, test compares `human_gates`). Ids `<gate>:<path>`; `since` from `git log -1`, fallback mtime.
- TSK-03: `gates.commit_paths` / `in_git` shared; `approve.py` uses them; CLI `approve` (owner, `--by`, `--expect`, `--no-commit`, diff).
- TSK-04: `request_changes` (draft value + `## Gates` line, TOML `# Gates` block), `gate_guard` rule for `gates.py approve|request-changes`.
- TSK-05: `## Gates` section appended to 11 templates, `# Gates` block in `stories.toml`; `check_workflow` needed no change.
- TSK-06: `schemas/gates.schema.json`, `CONTRACT_VERSION` 1.1, `tools/VERSION` 1.18.0, README, CHANGELOG.
- TSK-07: `tools/tests/test_gates.py` (12 tests), `test_contract.py` updated to 1.1 and `gates`.
- TSK-08: not started (push, PR, CI, tag belong to `/persist` and the owner).

### Changes (high-level)
- Code: skeleton `tools/gates.py` (CLI, pending, request-changes, atomic CRLF-preserving io), `approve.py`, `gate_guard.py`, `wf.py`.
- Interfaces: `gates.py list|approve|request-changes`, envelope tool `gates`, schema `gates`, contract 1.1.
- Domain: none.
- Tests: ${PY:-python3} -m unittest discover -s server/tests -q && ${PY:-python3} scripts/check_deps.py server && ${PY:-python3} -m unittest discover -s scripts/tests -q && npm --prefix web test -- --run → pass
- Specs: none (ADR-002 / FR notes reconciled in persistence).

Notes (no scope change, for review):
- Pending detection lives in `gates.pending()` and calls `next_step`; `next_step` itself was not refactored (its `human_gates` shape is guaranteed unchanged). `refined` and `workshop` items are added in `list` only.
- `make approve` now also keeps CRLF and writes atomically, and stages a not yet tracked artifact before committing it (previously a failure).
- Action commands always print an envelope (no `--json` flag); `list` prints text without `--json`.

---

# 4. Verification

- Build: OK (`check_workflow.py` OK in the skeleton)
- Tests: OK (skeleton full suite on Python 3.12: 127 tests; `test_gates` also on 3.14: 12 tests; 3.11 not installed locally, CI runs it)
- Interfaces / target platforms: OK (envelopes validate against `gates.schema.json`)
- Manual (if any): not run (fixtures only, no real repository touched)

Notes:
- Nothing pushed, no PR, no tag.

If FAIL → move to Tuning.

---

# 5. Tuning Log (If needed)

> Only within scope. The acceptance is the human's: fill it when they run `/persist` (or say the result is accepted).

Tuning accepted by: Alberto Galimberti
Date: 2026-10-22

### Entry #1
- Issue:
- Fix:
- Impact:
- Verified: Yes / No

### Entry #2
- …

---

# 6. Deviations

> One entry per deviation or stop condition. `Requires approval` sets the RUN to Blocked until a human approves it.

### Deviation #1
- What changed:
- Why:
- Plan impact:
- Scope impact: None / Minor / Requires approval
- Approved by:
- Date:

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Reference docs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- Spec §11 and status Done; ADR-002 tool table and a 2026-10-22 revision line (approve without `## Gates` line, request-changes scope). FR-13/FR-14 text needed no change.

---

# 8. Quality Gates Check

Facts, not ticks (`make check` reads them):

- AC: 6/6 met (AC1–AC5 by `tools/tests/test_gates.py`; AC6 by skeleton CI on 3.11 and 3.14, see CI)
- Tests: skeleton `python -m unittest discover` → pass (127 tests, Python 3.12; `test_gates` 12 tests also on 3.14)
- Out-of-scope changes: none
- CI: red — skeleton PR https://github.com/albegali/agentic-skeleton/pull/41: `other-os (windows-latest)` fails in `test_gates.test_approve_commits_the_field_alone_as_the_owner` (test compares `\\` and `/` path separators; code is fine); check 3.11, 3.14, macOS green, `secrets` pending. Portal PR https://github.com/albegali/agentic-portal/pull/10: all checks green except `e2e` still queued at the time of writing.

---

### Gates
> Written by `make gates` on 2026-10-22T16:54+02:00; do not edit by hand.
- test: `${PY:-python3} -m unittest discover -s server/tests -q && ${PY:-python3} scripts/check_deps.py server && ${PY:-python3} -m unittest discover -s scripts/tests -q && npm --prefix web test -- --run` → pass (OK)
- lint: `${PY:-python3} -m compileall -q server scripts && npm --prefix web run lint && npm --prefix web run typecheck` → pass (> tsc --noEmit)
- secrets: `/opt/homebrew/opt/python@3.14/bin/python3.14 tools/secret_scan.py --branch` → pass (secret scan: OK)




# 9. Outcome

Tasks completed:
- TSK-AP0105-01 … TSK-AP0105-07; TSK-AP0105-08 up to the skeleton PR and CI

Tasks deferred:
- TSK-AP0105-08: merge of skeleton PR #41, tag 1.18.0 and release (owner); `SKELETON_PIN` bump (portal story that consumes it)

Goal achieved:
- [ ] Yes
- [x] Partial
- [ ] No

Summary:
- `gates.py list|approve|request-changes` delivered in skeleton 1.18.0 (contract 1.1) on PR #41; Partial until the owner merges, tags and releases.

---

# 10. Next Steps

- Follow-ups: `/run AP0105 tuning: normalize path separators in test_gates (Windows CI)`, then `/persist AP0105` again.
- Risks:
- Improvements:

---

# 11. Review

> Written by `/review-story` (review mode), one entry per review, newest last. `ok-to-close` → RUN `Reviewed`;
> `changes-requested` → RUN `Tuning`, findings applied with `/run AP0105 tuning: …`, then `/persist` and a new review.

### Review #1
- Date:
- Reviewer:
- Outcome: `ok-to-close` / `changes-requested`
- Findings:
  - …

---

## Pending owner actions

> Actions only a person can do that the story still waits for (a tag, a release, a setting, a sign-off), one per line.
> `make next` lists the open ones of every RUN; a RUN cannot close with Goal achieved `Yes` while one is open.
- [ ] Merge skeleton PR #41, tag and release 1.18.0 (then bump `SKELETON_PIN` in a portal story) — owner: Alberto Galimberti — since: 2026-10-22

---

## Revisions

> Post-closure only: factual corrections (links, typos, recorded results), one line each with date and source.
> A change in behaviour is a new story with `supersedes = "AP0105"` in `backlog/stories.toml`, never a revision.

