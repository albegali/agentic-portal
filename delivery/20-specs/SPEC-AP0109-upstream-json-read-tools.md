# SPEC-AP0109 - Upstream: --json for backlog, check, plan, journal, story chain

## References
- Story ID: AP0109
- Brief: BRIEF-AP0109
- RUN: RUN-AP0109

---

## Status
Done

---

# 1. Goal

In the agentic-skeleton repository, `backlog`, `check`, `plan`, `journal` and `story` (story chain) print the contract 1.0 envelope with `--json`, validate against the schemas in `schemas/`, and the release `v1.0.0` is tagged after human review.

---

# 2. User / Business Value

As a portal (consumer of agentic-skeleton)
I want the five remaining read tools to emit the versioned envelope
So that the portal views read state without parsing Markdown and AP0104 can pin a complete release.

---

# 3. Scope

Included:
- `gen_backlog.py --json` → `wf.dump_envelope("backlog", …)`; `check_workflow.py --json` → `wf.dump_envelope("check", …)`. `data` keeps today's fields. `check` keeps its exit code (1 on errors); the envelope is a success envelope (`data.ok` false), since the tool ran correctly.
- New emitters, stdlib only, reusing `wf.sprints()`, `wf.stories()` and the `artifacts()` logic of `gen_backlog.py`:
  - plan: `releases` (from PLAN.md §2 table: id, title, goal, sprints) and `sprints` (`wf.sprints()` + `release`).
  - journal: `context` (text of `project-journal/context/` or null), `decisions`, `learnings`, `weekly`, `monthly` (items `file`, `title`, `date`; empty lists when none).
  - story chain for one ID: `id`, `title`, `stage`, `artifacts` (kind, path, status), `tasks` (id, title, status from the RUN task table); unknown ID → error envelope `unknown_id`, non-zero exit.
- Entry points (decision, §10): `wf.py plan --json`, `wf.py journal --json`, `wf.py story <ID> --json`.
- Tools are read-only: they write nothing.
- Error path: any failure with `--json` prints the error envelope (no `data`) and exits non-zero.
- Tests (stdlib `unittest`, `jsonschema` test-only): every tool's real output validated against its schema on a populated fixture repository and on an empty one (no stories, no PLAN.md, no journal entries); plain (non-JSON) output of `make backlog` and `make check` unchanged.
- Docs: `tools/README.md` contract table updated (drop "flat for now" and "schema only").
- Skeleton CI green on Python 3.11 and 3.14; AC5 of AP0103 closed here; tag (after human approval; `v1.3.0`, see §10).

Out of scope:
- Write commands, `gates.py` (AP0105), `context.py`/`repo_map.py --json`.
- Schema changes beyond minor additions (a needed addition is a minor bump and is logged).
- Portal-side client, caching and views (AP0104, AP0201+).
- Any change in this repository other than delivery artifacts and ADR-002/architecture reconciliation in persistence.

---

# 4. Acceptance Criteria

- [x] AC1: Given each of backlog, check, plan, journal and story chain with `--json`, when it runs on a populated repository, then it prints a one-line envelope `{contract: "1.0", tool, data}` that validates against its published schema.
- [x] AC2: Given an empty state (no stories, no PLAN.md rows, no journal entries, no tasks), when each tool runs with `--json`, then it returns valid `data` with empty lists (and `null`/empty strings only where the schema allows).
- [x] AC3: Given a failure (e.g. `story` with an unknown ID, malformed `backlog/stories.toml`), when a tool runs with `--json`, then it prints the error envelope with no `data` and exits non-zero.
- [x] AC4: Given the text output of `gen_backlog.py`, `check_workflow.py` and `next_step.py` without `--json`, when they run, then it is unchanged, and `check --json` keeps exit code 1 when `data.errors > 0`.
- [x] AC5: Given the skeleton CI on Python 3.11 and 3.14, when it runs, then schema tests for every envelope are green and, after human approval, the tag exists. CI part met (3.11, 3.14, macOS and Windows launcher jobs green on the story branch); tag `v1.3.0` on d00c402 created 2026-10-21 on the owner's go (TSK-AP0109-08).

---

# 5. Tasks

- `TSK-AP0109-01` Inspect the agentic-skeleton tools, schemas and tests (branch from `main`, `tools/VERSION` 1.2.0); log findings, the PLAN.md release table and RUN task-table formats in the RUN.
- `TSK-AP0109-02` `backlog` and `check` in the envelope (`--json` only), exit codes preserved.
- `TSK-AP0109-03` `plan` emitter (`wf.py plan --json`).
- `TSK-AP0109-04` `journal` emitter (`wf.py journal --json`).
- `TSK-AP0109-05` Story chain emitter (`wf.py story <ID> --json`) incl. tasks and error envelope.
- `TSK-AP0109-06` Contract tests for AC1–AC4 (populated and empty fixtures, schema validation, unchanged text output).
- `TSK-AP0109-07` `tools/README.md` contract table; CI check on 3.11 and 3.14.
- `TSK-AP0109-08` Push, CI green, tag — only after human review and approval (tag `v1.3.0`, see §10).

---

# 6. Execution Boundaries

The agent is allowed to:
- Change the agentic-skeleton repository (branch, commits) within the scope above.
- Add a minor, additive schema field only if a source cannot be expressed otherwise (logged as a deviation).
- Write delivery artifacts here.

The agent is not allowed to:
- Modify skeleton files from this repository, or add a runtime dependency (stdlib only; `jsonschema` test-only).
- Break a schema or the plain text output of existing commands; bump the contract major.
- Implement write commands, `gates.py`, `context`/`repo_map` JSON.
- Push the tag or release without human approval.
- Change ADR-002 or the architecture without owner approval.

---

# 7. Quality Gates

- [x] Tests added/updated (every tool, populated and empty)
- [x] Build passes (skeleton CI green on 3.11 and 3.14)
- [x] Public interfaces updated (`--json` outputs, `tools/README.md`, contract docs)
- [x] Domain invariants respected (errors never carry `data`; tools read-only)
- [x] No breaking changes to existing skeleton commands (text output, exit codes)

---

# 8. Stop Conditions

Stop and ask for supervision if:
- a schema cannot represent what the sources provide, or needs a breaking change (major bump)
- the flat `backlog`/`check` output is consumed somewhere that the envelope would break
- the PLAN.md release table or RUN task table format cannot be parsed reliably
- ADR-002 needs changes beyond the 2026-10-20 revision
- acceptance criteria are ambiguous or work appears out of scope

---

# 9. Impacted Areas

- Code: agentic-skeleton `tools/gen_backlog.py`, `tools/check_workflow.py`, `tools/wf.py`
- Interfaces: `--json` envelopes for backlog, check, plan, journal, story; `schemas/`
- Domain: n/a
- UX: n/a
- Platforms / distribution: skeleton release `v1.0.0`; the portal pins it as `SKELETON_PIN` (AP0104)
- Tests: skeleton contract tests and CI
- Docs: skeleton `tools/README.md`; ADR-002 follow-up note and AP0103 AC5/§11 reconciled in persistence

---

# 10. Notes / Clarifications

- Decision (owner-confirmed in chat 2026-10-20): the new commands live in `wf.py` (`plan`, `journal`, `story`) rather than new scripts, so the tool names `plan`, `journal`, `story` equal the subcommands and the install footprint (`adopt.py`) does not change. ADR-002 leaves the command names to this story.
- Decision (owner-confirmed in chat 2026-10-20): `check --json` returns a success envelope even when the workflow has errors: the contract reports the check result as data, and the non-zero exit is kept for scripts.
- `next-story` already exists (AP0103); it is not part of this story.
- Decision (owner, RUN §2, 2026-10-20): the tag is `v1.3.0` with `tools/VERSION` 1.3.0 (the skeleton already had `v1.1.0`, `v1.1.1` and version 1.2.0); the contract stays `1.0`. Supersedes "`v1.0.0`" in ADR-002 and in §1/§3 above.
- AP0104's CI job needs this tag; keep AP0109 before AP0104 (PLAN.md order).

---

# 11. Final Reconciliation

To be completed before marking Done.

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- Delivered in agentic-skeleton (branch `ap0109-upstream-json-read-tools`, merged into `main` at `d00c402`): `gen_backlog.py --json` and `check_workflow.py --json` in the envelope; new `wf.py plan | journal | story <ID> --json`; error codes `unknown_id`, `bad_input`, `usage`; `artifacts()` moved to `wf.py`; skeleton `tools/VERSION` 1.3.0. 63 tests (3 new contract tests for populated, empty and error cases); CI green on 3.11, 3.14, macOS and Windows.
- Text output of the existing commands is unchanged; schemas are unchanged (extra `target` on releases uses `additionalProperties`).
- TSK-AP0109-08 only partly done: pushed, CI green and merged; the tag `v1.3.0` waits for the owner (AC5 open on the tag only).
- AP0104's runner still calls `tools/plan.py`, `journal.py`, `story.py`: to become `tools/wf.py plan|journal|story` in AP0104.

---

## Revisions

- 2026-10-21: AC5 met: agentic-skeleton tag `v1.3.0` on d00c402. Source: project-journal/decisions/2026-10-21-close-open-points.md.
