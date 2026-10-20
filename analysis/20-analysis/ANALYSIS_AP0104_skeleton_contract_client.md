---
artifact_type: analysis
us_id: STORY_AP0104
title: Skeleton contract client
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0104_skeleton_contract_client.md
  - reference/project-summary.md
related_references:
  - reference/product/functional-requirements.md#FR-27
  - reference/product/functional-requirements.md#FR-25
  - reference/product/non-functional-requirements.md#NFR-13
  - reference/architecture/ADR-002-skeleton-contract.md
last_updated: 2026-10-20
---

# Analysis AP0104 - Skeleton contract client

## 1. References

- ID: AP0104
- Source story: analysis/10-stories/STORY_AP0104_skeleton_contract_client.md
- Roadmap phase: R1 (sprint S2 in PLAN.md)
- Sources used: Story, project summary, FR-27, FR-25, NFR-13, ADR-002 (with 2026-10-19/20 revisions), Analysis AP0101 and AP0103 §6+, `tools/README.md` (JSON contract), `schemas/`
- Missing sources: Refined AP0103 and workshop minutes read only through ADR-002; architecture.md §2/§6 (module layout, health) and ADR-004 (tool allow-list) not read

## 2. Original User Story

### Story text

As a portal server, I want to call skeleton tools through the versioned --json envelope, validate it against the JSON Schemas and check the contract version, so that the portal never parses Markdown and detects incompatible skeleton versions.

### Description

- Epic: EP-01 — Technical foundations
- Priority (MoSCoW): Must · Release: R1 · Size: L · Type: technical
- Requirements: FR-27, FR-25, NFR-13
- Depends on: AP0101, AP0103
- Notes: ADR-002. Consumes the envelope released by AP0103.
- Out of scope: Gate writes, run launching.

## 3. Intent Understanding

### Functional goal

- Give the rest of the portal one reliable way to read repository state through skeleton tools, and tell the user clearly when the skeleton in their repository cannot be used.

### Actors involved

- Portal server (internal client); owner/developer seeing the incompatibility message; CI (contract tests).

### Expected outcome

- A contract client with version check, error handling and contract tests that every later read-screen story relies on.

## 4. Information Classification

### Facts

- ADR-002 (accepted): subprocess calls to `tools/*.py --json`; envelope `{"contract","tool","data"}`, errors `{"contract","tool","error":{"code","message"}}` with non-zero exit; accept same major and any minor ≥ the built-for minor; schemas ship in the skeleton under `schemas/`; **at runtime the portal checks only the `contract` version** against `CONTRACT_BUILT_FOR`; `jsonschema` is a CI/test dependency only; the mismatch is shown **only in Settings** (FR-27 decision in ADR context).
- Skeleton state (`tools/README.md`): contract 1.0 envelope is emitted today by `wf.py version`, `next_step.py` (`next`, `next-story`); `check` and `backlog` still print the flat `"schema": 1` object; `plan`, `journal`, `story` have schemas but **no emitter** until AP0109; `context`/`repo_map` are flat and outside 1.0; `gates` is a later minor (AP0105).
- Skeleton tools keep Python ≥ 3.11; the portal requires ≥ 3.14 and uses stdlib only (NFR-08).
- The release bundle manifest currently carries `contract_built_for: "unknown"` and `/api/health` reports `unknown` skeleton/contract (AP0101, accepted until AP0103 completes them).
- Portal-side contract tests (NFR-13) were proposed as a new portal story in the AP0103 Analysis; AP0104 is the only candidate (ADR-002 follow-ups name AP0104).

### Clarifications received

- AP0103 workshop: `wf.py version --json` added to the 1.0 list; split into AP0103 + AP0109 accepted.

## 5. Original Acceptance Criteria

- Given a recorded envelope of every contract tool, when the contract tests run, then each validates against its schema.
- Given a skeleton whose contract major differs, when the portal starts, then a clear incompatibility message is shown and data calls are refused.
- Given a compatible minor version with unknown extra fields, when the portal reads it, then it works.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- **"Every contract tool"** (AC 1): today only `version`, `next`, `next-story` emit envelopes; `backlog`, `check` are flat and `plan`, `journal`, `story` do not exist until AP0109, which this story does not depend on. Is the set the tools available at AP0103's release, or all eight schemas?
- **"Validate it against the JSON Schemas"** (Story text) versus ADR-002 "at runtime the portal checks only the contract version": is validation a test-time activity or a runtime behaviour?
- **"Clear incompatibility message is shown"** (AC 2) versus ADR-002/FR-27 "shown only in Settings": where does the user see it when they open the portal on another screen? "Data calls refused" means every screen is empty.
- "Starts": at portal start or lazily at the first request? What happens when the skeleton is upgraded while the portal is running?

### Functional gaps

- No AC for a **missing or older skeleton** (no `wf.py version`, no `--json`), typical of adopted repositories (FR-24): refuse, or degrade?
- No AC for a **lower minor** than built-for (ADR says incompatible) or a malformed envelope / non-JSON output / tool failure (error envelope) / timeout.
- Empty states and "not a workflow repository" are not described for the user.
- No AC for how stale data is handled (caching on file mtimes was deferred to "a later portal story" in AP0103).

### Technical gaps

- Where the schemas come from at test time: the pinned skeleton tag (checkout in CI), a vendored copy, or recorded envelopes only. The contract (NFR-13) says CI covers it; the skeleton `v1.0.0` tag follows AP0109, i.e. possibly after this story's sprint.
- Fixtures: recorded envelopes drift unless regenerated from the live tools.
- Subprocess policy: executable (`sys.executable`), cwd, env, timeout, max output size, UTF-8 on Windows, concurrency limit, allow-list of tool names (ADR-004/006).
- `jsonschema` as a dev dependency conflicts with NFR-08 only if imported by `server/`; the dependency check (AP0101) must allow it for tests only.
- Health fields `contract.skeleton` / `built_for` must now be filled; owner of that change is unclear (AP0101 left it to "AP0103").
- Size L: client, version check, health integration, fixtures, CI job and per-tool schemas are separable.

### Dependencies or ownership points to clarify

- Depends on AP0103 (released upstream) but needs AP0109 for the full tool set and tag; ordering inside S2 and the portal pinning of the skeleton version are open.
- Interplay with AP0102: the client runs only behind the authenticated API.
- Consumers: AP0201, AP0202, AP0203 and every screen story depend on the client's call API and error shapes.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions only: an answer from the PO / stakeholder is mandatory.

- [High impact] When the skeleton contract is incompatible, missing or older (e.g. an adopted repository without `wf.py version`), should the user get (a) a blocking screen replacing all data views, (b) a persistent banner with the views empty, or (c) Settings-only, as the ADR says? — decides the user-visible behaviour of FR-27 and whether older skeletons are usable at all.
- [High impact] Which tools must be covered by the contract tests in this story: only those released with AP0103 (`version`, `next`, `next-story`), or all eight, which forces the sprint order AP0109 → AP0104? — scope and sprint ordering across two repositories.
- [Medium impact] Is a skeleton with a **lower minor** than the portal was built for refused entirely, or may views whose tool exists keep working? — user impact of an older-but-same-major skeleton.
- [Medium impact] How fresh must data be (re-read on every action/refresh vs. on file change)? — decides whether caching is in this story or deferred.
- [Low impact] Should the incompatibility message tell the user which version to install or pin (portal version ↔ skeleton version table)? — wording and support burden.

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Runtime validation — **Proposal**: no schema validation at runtime (consistent with ADR-002): the client checks the envelope shape (`contract`, `tool`, `data` or `error`), the major/minor rule, and the expected `tool` name; full JSON Schema validation is a test-time activity · **Why**: NFR-08, ADR-002; the Story's "validate" is met by the contract tests · **Alternatives**: minimal stdlib validator for the schema subset (cost, drift) · **Confidence**: medium
- [High impact] Contract-test sources — **Proposal**: CI job "contract" checks out `agentic-skeleton` at the tag pinned in `project.toml`/a portal constant (`SKELETON_PIN`), runs each available tool with `--json` on a fixture repository, validates against that checkout's `schemas/` with `jsonschema` (dev requirement), and also validates the committed recorded envelopes used by unit tests; a tool without emitter is skipped with an explicit marker that fails once AP0109's tag is pinned · **Why**: NFR-13 "contract tests in CI"; avoids drift · **Alternatives**: recorded fixtures only · **Confidence**: high
- [High impact] Split of the L story — **Proposal**: keep one story but order tasks: (1) subprocess runner + envelope parser + errors, (2) version gate and health fields, (3) fixtures + contract tests CI; if AP0109 is late, close with the tools available and track the rest as a task on AP0109's portal side · **Why**: avoids blocking S2 · **Alternatives**: formal split into AP0104a/b · **Confidence**: medium
- [Medium impact] Runner policy — **Proposal**: argument lists only, tool name from a fixed table (`version`, `next`, `next-story`, `backlog`, `check`, `plan`, `journal`, `story`), `sys.executable`, cwd = repo root, 30 s timeout, 5 MB output cap, `PYTHONUTF8=1`, one result object `Ok(data)` / `ContractError(kind, message)` with kinds `incompatible`, `missing-tool`, `tool-error`, `bad-output`, `timeout` · **Why**: ADR-004/006 conventions; uniform API errors for screens · **Alternatives**: per-tool wrappers · **Confidence**: high
- [Medium impact] Version rule and state — **Proposal**: the version is read once with `wf.py version --json` at startup and re-read on a Settings "re-check" action and on a failed call; same major and minor ≥ `CONTRACT_BUILT_FOR` is compatible, otherwise state `incompatible` and `/api` data routes answer 409 `contract_incompatible` with the message; health and Settings stay available · **Why**: ADR-002 rule; data calls refused as in AC 2 · **Alternatives**: check on every call (extra process) · **Confidence**: medium
- [Medium impact] Health fields — **Proposal**: this story fills `contract` and `skeleton` in `/api/health` from the client state and replaces `contract_built_for: "unknown"` in `scripts/build_bundle.py`/manifest with the real constant · **Why**: closes the AP0101 "unknown until AP0103" assumption · **Alternatives**: separate story · **Confidence**: high
- [Medium impact] Forward compatibility — **Proposal**: parsed data kept as plain dicts, unknown keys ignored, required keys per tool checked by the screens' adapters, not by the client · **Why**: AC 3, "minors only add fields" · **Confidence**: high
- [Low impact] Caching — **Proposal**: none in this story; the runner API leaves a hook for an mtime-keyed cache in a later story · **Why**: AP0103 already deferred it · **Confidence**: high

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-20)

See `analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md` and the Refined Story. Owner decisions recorded there change §7 proposals; the rest stands.
