---
artifact_type: refined
us_id: STORY_AP0104
title: Skeleton contract client
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0104_skeleton_contract_client.md
  - analysis/20-analysis/ANALYSIS_AP0104_skeleton_contract_client.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md
related_references:
  - reference/architecture/ADR-002-skeleton-contract.md
  - reference/product/functional-requirements.md#FR-27
  - reference/product/functional-requirements.md#FR-25
  - reference/product/non-functional-requirements.md#NFR-13
last_updated: 2026-10-20
---

# Refined Story AP0104 - Skeleton contract client

## 1. References

- ID: AP0104
- Title: Skeleton contract client
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, ADRs listed above
- Missing sources: architecture.md §2/§6, ADR-004
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md

## 2. Refined User Story

### Refined story text

As a portal server, I want to call skeleton tools through the versioned --json envelope, validate it against the JSON Schemas and check the contract version, so that the portal never parses Markdown and detects incompatible, missing or older skeletons.

### Refined description

One L story kept, ordered as: runner + envelope parser + validator, version gate + health fields, fixtures + contract tests in CI. Depends on AP0109 for the full tool set (order AP0109 → AP0104).

## 3. Scope

### In scope

- Subprocess runner (fixed tool table, `sys.executable`, cwd = repo root, 30 s timeout, 5 MB cap, `PYTHONUTF8=1`) returning `Ok(data)` or `ContractError(kind, message)`, kinds `incompatible`, `missing-tool`, `tool-error`, `bad-output`, `timeout`.
- Runtime validation of every envelope with a small stdlib validator for the JSON Schema subset used by `schemas/` (the Spec defines the subset).
- Version gate: read once at start with `wf.py version --json`, re-read on a Settings re-check and after a failed call; same major and minor ≥ `CONTRACT_BUILT_FOR`.
- Incompatible, missing or older skeleton: message shown, data routes answer 409 `contract_incompatible`, health and Settings stay available and manageable, a recovery proposal (exact steps and command) is shown.
- Fill `contract` and `skeleton` in `/api/health`; replace `contract_built_for: "unknown"` in the bundle manifest.
- Contract tests for all eight tools (`version`, `next`, `next-story`, `backlog`, `check`, `plan`, `journal`, `story`) in CI against the pinned skeleton tag with `jsonschema` (test only), plus recorded envelopes.

### Out of scope

- Gate writes, run launching.
- Executing the recovery through an agent run (depends on the runs epic).
- Caching (hook only).

## 4. Confirmed Information

### Facts

- ADR-002 (revised 2026-10-20); tools emitting envelopes today: `version`, `next`, `next-story`; `backlog`/`check` flat until AP0109; `plan`, `journal`, `story` have no emitter until AP0109.
- Skeleton tools keep Python ≥ 3.11; the portal is stdlib only (NFR-08).

### Decisions confirmed during refinement

- Runtime schema validation is added (owner), implemented as a stdlib validator; `jsonschema` stays test-only. ADR-002 revision line recorded.
- Keep one L story.
- Incompatible, missing or older skeleton: message, data calls refused, Settings viewable and manageable, plus a recovery option (owner follow-up).
- All eight tools covered by contract tests; sprint order AP0109 → AP0104 accepted.
- Not overridden, therefore standing (proposal accepted by default): CI contract job at the pinned `SKELETON_PIN`; runner policy; version state machine and 409 shape; forward compatibility (unknown keys ignored, adapters check required keys); no caching.

### Residual assumptions

- A lower minor than built-for is treated as incompatible (ADR rule), not partially usable.
- Data freshness: re-read on each action/refresh, no cache (deferred).

## 5. Confirmed Acceptance Criteria

- Given a recorded envelope of each of the eight contract tools, when the contract tests run, then each validates against its schema in the pinned skeleton checkout.
- Given a skeleton whose contract major differs, or a lower minor, or no `wf.py version`, when the portal starts, then an incompatibility message and a recovery proposal appear in Settings and data calls are refused with 409.
- Given a compatible minor with unknown extra fields, when the portal reads it, then it works.
- Given non-JSON output, a failed tool, an oversized output or a timeout, when a call is made, then a typed `ContractError` is returned.
- Given an envelope that violates its schema, when it is read at runtime, then it is rejected as `bad-output`.
- Given Settings, when I trigger re-check after fixing the skeleton, then the state is re-evaluated.

## 6. Remaining Open Points

### Functional

- Where the user sees the message outside Settings (ADR-002 says Settings only; FR-27 UI belongs to the Settings story): not blocking, the API exposes the state.

### Technical

- Exact recovery steps and which part waits for the runs epic (Brief/Spec decides; AP0104 ships detection, message and proposal).
- The schema subset the validator supports is defined in the Spec and must be checked against `schemas/` in CI.
- Pinned skeleton tag must include AP0109 and AP0105 outputs for the full contract test set.

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Runner and parser; stdlib schema validator; version gate and state; 409 responses; health fields and manifest constant; recovery proposal payload; fixtures; CI contract job; dependency check allowing `jsonschema` for tests only.

### Boundaries to respect

- server/ imports stdlib only; consumers (AP0201–AP0203 and screens) rely on the call API and error shapes defined here.
- No skeleton file edited locally (NFR-14).

## 8. Refinement Outcome

- Story ready with residual open points to track
