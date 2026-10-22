# SPEC-AP0105 - Upstream: gates.py

## References
- Story ID: AP0105
- Brief: BRIEF-AP0105
- RUN: RUN-AP0105
- Requirements: FR-13, FR-14, NFR-03, NFR-14

---

## Status
Done

---

# 1. Goal

In the agentic-skeleton repository, `python3 tools/gates.py list --json` returns every pending human gate from one detection shared with `next_step.py`, and `approve` / `request-changes` apply a decision through the same code as `make approve`, attributed to the `project.toml` owner. Released as a contract minor (`1.1`).

---

# 2. User / Business Value

As a portal (consumer of agentic-skeleton)
I want to list and decide human gates through one skeleton tool
So that the portal never edits workflow files directly and gate writes match human and agent edits (FR-13, FR-14).

---

# 3. Scope

Baseline: skeleton 1.17.3 (`tools/gates.py` is today a library module without CLI: catalog `passed`, `allowed_by`, `hint`, `approve`; `tools/approve.py` is the `make approve` wrapper; `gate_guard.py` blocks agent edits). Detection of *pending* gates lives only in `next_step.py` (`human_gates`).

Included:
- Shared pending-gate detection in `gates.py`, used by `next_step.py` and the new CLI; `human_gates` in `next_step.py --json` keeps its shape.
- CLI added to the existing `tools/gates.py` (`list|approve|request-changes`, `--json`); module API used by `approve.py`, `gate_guard.py`, `check_workflow.py --git` unchanged.
- `gates.py list --json`: items `{id, gate, artifact, field, current, proposed, story_id?, since, age_days}`; `gate` is the catalog name (`spec`, `strategy`, `deviation:<n>`, `tuning`, `spike`, `refined`, `inception`, `stack`) plus list-only `workshop`; id `<gate>:<artifact path>` (workshop decision 2026-10-19/20); age from the last commit touching the artifact, fallback mtime; empty state is valid `data`.
- `gates.py approve <gate-id> [--expect <current>] [--by <owner>] [--no-commit]`: thin wrapper over `gates.approve()`; field set and commit alone with `Approved-by`/`Approved-at` trailers (as `approve.py`, which is refactored to share the code); approver is the `project.toml` owner (`--by` only if equal); returns `data.diff` and the commit.
- `gates.py request-changes <gate-id> --comment <text> [--expect <current>] [--by <owner>]`: writes the gate's draft value (never an approval value) plus one line `YYYY-MM-DD — changes requested by <owner>: <comment>` in a `## Gates` section (TOML: trailing `# Gates` comment block); working-tree edit, no commit; not available for `workshop`, `deviation`, `tuning` (`invalid_transition`; the human uses `/run <ID> tuning`).
- Error envelopes, non-zero exit, nothing written: `unknown_gate`, `stale_gate` (also `--expect` mismatch, already resolved), `invalid_transition`, `no_owner`, `comment_required`, `usage`, `bad_input`.
- Atomic write (temp file + replace), line endings and other bytes preserved, only gates returned by `list`, paths resolved inside the repository (NFR-03).
- `gate_guard.py` also blocks agents from `gates.py approve|request-changes` (same rule as `make approve`); no `WF_AGENT` variable.
- Schema `gates` (list and action results), `wf.CONTRACT_VERSION` 1.1, `tools/VERSION` minor bump, `tools/README.md` (contract table; the "Contract tools only read" sentence amended), `## Gates` section in the skeleton templates that can receive a request-changes line, `check_workflow` allowance if needed.
- Tests (stdlib `unittest`, `jsonschema` test-only) on Python 3.11 and 3.14, CRLF fixtures, directory without git.

Out of scope:
- Portal UI, agent-caller checks beyond `gate_guard`, confirm nonce (EP-04); journal entries or sidecar files.
- `context.py` / `repo_map.py --json`; portal-side client changes (AP0104 follow-up in its own story).
- Any change in this repository other than delivery artifacts and ADR-002 reconciliation in persistence.

---

# 4. Acceptance Criteria

- [x] AC1: Given a repository with pending gates, when `gates.py list --json` runs, then each gate carries artifact, gate, field, current, proposed and age in a `{contract, tool: "gates", data}` envelope that validates against its schema; `next_step.py --json` `human_gates` is unchanged.
- [x] AC2: Given a pending gate, when `gates.py approve` runs, then only the gate field changes to the approved value, the change is committed alone with the owner in `Approved-by` and the date in `Approved-at`, and the result carries the diff.
- [x] AC3: Given a pending gate that supports it, when `gates.py request-changes` runs with a comment, then the comment is recorded in `## Gates`, the field holds its draft value and no approval value is written.
- [x] AC4: Given an unknown, stale or already resolved gate, a missing owner or a missing comment, when an action runs, then the matching error envelope is returned, the exit code is non-zero and no file changes.
- [x] AC5: Given CRLF files and a directory without git, when an action or `list` runs, then line endings and all other bytes are preserved, `since` falls back to mtime and `approve` sets the field without a commit.
- [x] AC6: Given the skeleton CI on Python 3.11 and 3.14, when it runs, then it is green; the release tag follows human approval.

---

# 5. Tasks

- `TSK-AP0105-01` Inspect the skeleton 1.17.3 (branch from `main`): `next_step.py` human stages, `gates.py`, `approve.py`, `gate_guard.py`, templates, `check_workflow.py`, schemas; log the final per-gate table (detection, field, approved/draft value) in the RUN.
- `TSK-AP0105-02` Shared pending detection in `gates.py` and `list --json` (ids, age); `next_step.py` reuses it, output unchanged.
- `TSK-AP0105-03` `approve` wrapper: `approve.py` refactor to a shared apply-and-commit function, owner attribution, `--expect`, `--by`, diff output.
- `TSK-AP0105-04` `request-changes`: per-gate draft value, atomic write, CRLF, `## Gates` line (md and TOML), error codes; `gate_guard` rule.
- `TSK-AP0105-05` Templates get the `## Gates` section; `check_workflow` allowance if needed.
- `TSK-AP0105-06` Schema `gates`, contract `1.1`, `tools/VERSION`, `tools/README.md`.
- `TSK-AP0105-07` Tests for AC1–AC5 (populated, empty, errors, CRLF, no-git) and CI on 3.11 and 3.14.
- `TSK-AP0105-08` Push, CI green, tag — only after human review and approval.

---

# 6. Execution Boundaries

The agent is allowed to:
- Change the agentic-skeleton repository (branch, commits) within the scope above, including `approve.py` and `gate_guard.py` as stated.
- Add the `## Gates` section to skeleton templates and a minimal `check_workflow` allowance.
- Write delivery artifacts here.

The agent is not allowed to:
- Modify skeleton files from this repository, or add a runtime dependency.
- Change the shape of `next_step.py --json`, the behaviour of `make approve`, existing schemas (beyond additive minor), or bump the contract major.
- Run `approve` / `request-changes` on real repositories during development (fixtures only).
- Push the tag or release without human approval.
- Change ADR-002 or the architecture without owner approval.

---

# 7. Quality Gates

- [x] Tests added/updated
- [x] Build passes (skeleton CI green on 3.11 and 3.14)
- [x] Public interfaces updated (`gates` schema, `tools/README.md`, templates)
- [x] Domain invariants respected (approve changes only the gate field, as `make approve`; request-changes only the gate field and one `## Gates` line; errors never carry `data`)
- [x] No breaking changes unless explicitly approved

---

# 8. Stop Conditions

Stop and ask for supervision if:
- a gate cannot be applied as a single-field edit, or a pending gate cannot be detected reliably
- refactoring `approve.py` / `next_step.py` would change `make approve` behaviour or `--json` shape
- adding `## Gates` breaks `check_workflow` or a template consumer
- the schema needs a breaking change
- security or permission rules are unclear
- acceptance criteria are ambiguous or work appears out of scope

---

# 9. Impacted Areas

- Code: agentic-skeleton `tools/gates.py` (CLI added), `tools/approve.py`, `tools/next_step.py`, `tools/gate_guard.py`, `tools/wf.py` (contract version), `tools/check_workflow.py`
- Interfaces: `gates.py` CLI, envelope tool `gates`, `schemas/gates.schema.json`, contract 1.1
- Domain: gate catalog (§10)
- UX: n/a
- Platforms / distribution: skeleton release (next minor after 1.17.3; `SKELETON_PIN` update belongs to the portal stories that consume it)
- Tests: skeleton contract and unit tests, CI
- Docs: `tools/README.md`, skeleton templates; ADR-002 and FR-13/FR-14 notes reconciled in persistence

---

# 10. Notes / Clarifications

Re-scope against skeleton 1.17.3 (written 2026-10-21, after the Spec draft) → done 2026-10-21: built on existing `gates.py`/`approve.py`/`gate_guard.py`; the original new-tool plan and the `WF_AGENT` guard are dropped.

Proposed gate catalog, to be confirmed from the code in TSK-01. Source: `gates.approve()` and `next_step.py`.

| Gate | Artifact | Approve (`gates.approve`, committed with trailers) | Request-changes (draft value + `## Gates` line) |
|---|---|---|---|
| inception | vision, FR/NFR, mockup map, architecture, PLAN.md, ADR | frontmatter `status` → `approved` (ADR `accepted`) | `draft` (ADR `proposed`) |
| inception | `backlog/stories.toml` | `status = "approved"` | `status = "draft"` + `# Gates` block |
| stack | `project.toml` | `[stack] decided = true` | `false` + `# Gates` block |
| spec | Spec | `## Status` → `Ready` | `Draft` |
| strategy | RUN (and Spec) | §2 `[x] Approved`, Reviewer/Date, RUN `Strategy Approved`, Spec `In Progress` | §2 `[x] Revisions requested`, RUN `Draft` |
| deviation:n | RUN §6 | `Approved by`/`Date` filled | not supported |
| tuning | RUN §5 | `Tuning accepted by`/`Date` filled | not supported |
| spike | spike note | `Accepted` | `Draft` |
| refined | Refined Story | frontmatter `approved` | `draft` |
| workshop | Analysis | list only (resolves when the Refined Story exists) | not supported |

Doubts for the human review (Spec gate):
1. **Departure from the Refined Story / workshop decision**: approve no longer adds a `## Gates` line and sets the same fields as `make approve` (owner and date in commit trailers, RUN §2 Reviewer/Date, `Tuning accepted by`). Only request-changes writes `## Gates`. Confirm, or restore the line for approve (then `approve.py` stays unchanged and the portal approve differs from the human one).
2. **Commit on approve**: the portal approve commits like `make approve`, on the current branch (needed for `check --git`: approval before code). Confirm, or default to `--no-commit` and let the portal commit.
3. **Request-changes scope** limited to spec, strategy, inception, stack, spike, refined (no deviation, tuning, workshop). Confirm.
4. **Version**: next minor after 1.17.3 is 1.18.0 with contract 1.1; confirm number.
5. **Attribution**: `Approved-by` uses the `project.toml` owner (portal) while `make approve` uses the git user; the CLI takes the owner (confirm).

---

# 11. Final Reconciliation

Completed at persistence 2026-10-22.

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- Delivered in agentic-skeleton on `feat/ap0105-gates-cli` (skeleton 1.18.0, contract 1.1): `gates.py list|approve|request-changes`, schema `gates`, `## Gates` in 11 templates, `gate_guard` rule, 12 new tests. Deferred: TSK-08 tag and release (owner), `SKELETON_PIN` bump (portal story). ADR-002 reconciled.
