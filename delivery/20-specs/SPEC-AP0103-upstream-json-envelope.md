# SPEC-AP0103 - Upstream: --json envelope and JSON Schemas

## References
- Story ID: AP0103
- Brief: BRIEF-AP0103
- RUN: RUN-AP0103

---

## Status
Done

---

# 1. Goal

Contract 1.0 released in the agentic-skeleton repository: versioned envelope, error envelope, `wf.py version --json`, `next_step.py --json` in the envelope, JSON Schemas for all seven v1.0 outputs, schema tests in CI on Python 3.14, tagged release.

---

# 2. User / Business Value

As a portal (consumer of agentic-skeleton)
I want a released, versioned JSON contract with published schemas
So that I can be built and tested against it and report skeleton and contract versions.

---

# 3. Scope

Included:
- Envelope helper in the skeleton: success `{contract, tool, data}`; error `{contract, tool, error:{code, message}}` with no `data` and non-zero exit; constant `CONTRACT_VERSION = "1.0"`.
- `wf.py version --json`: skeleton version and contract version.
- `next_step.py --json` wrapped in the envelope (existing fields kept under `data`).
- JSON Schema 2020-12 files under `schemas/` for: envelope (success and error), version, next, backlog, check, plan, journal, story chain. Empty states are valid `data` with empty lists.
- Schema tests (stdlib `unittest`, `jsonschema` test-only) with sample envelopes for every schema, including error cases; schema tests reject a `contract` major other than 1.
- Skeleton CI on Python 3.14; Python 3.14 requirement documented.
- Contract rules documented in the skeleton (semver, additive minors, breaking change bumps major).
- Tagged release (contract 1.0).
- Tool names for plan, journal and story chain fixed in the schema file names (see §10).

Out of scope:
- `--json` emission for backlog, check, plan, journal, story chain (AP0109); the schemas here are their target.
- Write commands, gates (AP0105), launcher (AP0106), context, repo_map.
- Portal-side contract client and tests (AP0104), mtime caching.
- Changes in this repository other than delivery artifacts and the ADR-002/architecture reconciliation in persistence.

---

# 4. Acceptance Criteria

- [ ] AC1: Given `next_step.py --json`, when it runs, then it prints an envelope with `contract: 1.x` that validates against `schemas/next`.
- [ ] AC2: Given `wf.py version --json`, when it runs, then the envelope reports skeleton version and contract version and validates against its schema.
- [ ] AC3: Given a tool failure with `--json`, when it runs, then it prints the error envelope (no `data`) and exits non-zero.
- [ ] AC4: Given a breaking output change, when it is released, then the contract major is bumped (rule documented and enforced by a test that pins the schema `contract` const/pattern to the declared major).
- [ ] AC5: Given the skeleton CI on Python 3.14, when it runs, then schema tests for every published schema are green and a tagged release exists.
- [ ] AC6: Given an empty backlog, plan or journal, when the corresponding sample is validated, then empty lists are valid `data`.

---

# 5. Tasks

- `TSK-AP0103-01` Inspect agentic-skeleton (tools, tests, CI, Python baseline, version source); log the findings in the RUN.
- `TSK-AP0103-02` Envelope helper and `CONTRACT_VERSION`; success and error output with exit codes.
- `TSK-AP0103-03` `wf.py version --json`.
- `TSK-AP0103-04` `next_step.py --json` in the envelope.
- `TSK-AP0103-05` Schemas: envelope, version, next.
- `TSK-AP0103-06` Schemas: backlog, check, plan, journal, story chain (shape derived from the current Markdown/TOML sources and ADR-002 table).
- `TSK-AP0103-07` Schema tests with samples (valid, invalid, error, empty states).
- `TSK-AP0103-08` CI on Python 3.14; contract rules and Python requirement documented.
- `TSK-AP0103-09` Tagged release 1.0 (after human review).

---

# 6. Execution Boundaries

The agent is allowed to:
- Change the agentic-skeleton repository (branch, commits) within the scope above.
- Add `jsonschema` as a test/CI dependency only.
- Write delivery artifacts here.

The agent is not allowed to:
- Modify skeleton files from this repository, or add a runtime dependency to the skeleton.
- Implement `--json` for backlog/check/plan/journal/story chain (AP0109), or write commands.
- Push the tag without human review and approval.
- Change ADR-002 or the architecture without owner approval (see stop conditions).

---

# 7. Quality Gates

- [ ] Tests added/updated (schema tests for every schema)
- [ ] Build passes (skeleton CI green on Python 3.14)
- [ ] Public interfaces updated (schemas, tool output, contract docs)
- [ ] Domain invariants respected (semver rules of ADR-002; errors never carry `data`)
- [ ] No breaking changes to existing skeleton commands unless approved (plain `next_step.py` output unchanged)

---

# 8. Stop Conditions

Stop and ask for supervision if:
- ADR-002's contract table needs changes beyond the 2026-10-19 revision (owner approval required)
- Python 3.14 requirement breaks existing skeleton usage in a way that needs a decision
- `next_step.py --json` today's shape cannot be wrapped without a breaking change
- a schema shape for AP0109 tools needs data the sources cannot provide
- the skeleton has no CI to extend
- acceptance criteria are ambiguous or work appears out of scope

---

# 9. Impacted Areas

- Code: agentic-skeleton `tools/` (envelope helper, `wf.py`, `next_step.py`)
- Interfaces: `--json` envelope, `schemas/`, contract version 1.0
- Domain: n/a
- UX: n/a
- Platforms / distribution: skeleton tagged release; portal pins it via `project.toml`
- Tests: skeleton schema tests and CI
- Docs: skeleton contract docs; ADR-002 and architecture reconciled in persistence

---

# 10. Notes / Clarifications

- Schema file names (proposal, fixed here per ADR-002): `envelope`, `version`, `next`, `backlog`, `check`, `plan`, `journal`, `story` (story chain). Tool commands for plan, journal and story chain are named by AP0109; the `tool` field values equal these names.
- Split decision: backlog already applies it; Refined Story's residual point on the split is closed.
- Dependencies: AP0101 (health) and AP0104, AP0105, AP0109 depend on this release.
- 2026-10-19 owner decisions (RUN-AP0103 strategy): replacing the flat `"schema": 1` output of `next_step.py --json` with the envelope is approved; the skeleton baseline stays Python >= 3.11 for now, CI tests 3.11 and 3.14 (supersedes "Python 3.14" in §3 and ADR-002; reconciled in persistence).

---

# 11. Final Reconciliation

To be completed before marking Done.

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- Delivered in agentic-skeleton branch `feat/contract-1.0-envelope` (commit aa8652f, not pushed): envelope and error envelope, `wf.py version --json`, `next_step.py --json` in the envelope, 9 schema files, 9 contract tests, CI on Python 3.11 and 3.14.
- Final state differs from §3/§4 as decided by the owner: tools keep Python >= 3.11; the `v1.0.0` tag and the CI-green part of AC5 move to the end of AP0109; `adopt.py` also installs `VERSION` and `schemas/`.
- TSK-AP0103-09 (tag) deferred. AC1-AC4 and AC6 met locally (29 tests, Python 3.12 and 3.14); AC5 open until push, CI and tag.
