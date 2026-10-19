---
artifact_type: refined
us_id: STORY_AP0103
title: Upstream --json envelope and JSON Schemas
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0103_upstream_json_envelope.md
  - analysis/20-analysis/ANALYSIS_AP0103_upstream_json_envelope.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md
related_references:
  - reference/architecture/ADR-002-skeleton-contract.md
  - reference/product/functional-requirements.md#FR-27
  - reference/product/non-functional-requirements.md#NFR-13
  - reference/product/non-functional-requirements.md#NFR-14
last_updated: 2026-10-19
---

# Refined Story AP0103 - Upstream --json envelope and JSON Schemas

## 1. References

- ID: AP0103
- Title: Upstream --json envelope and JSON Schemas
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, ADR-002
- Missing sources: agentic-skeleton repository state (existing tools, test setup, Python baseline)
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md

## 2. Refined User Story

### Refined story text

As a portal (consumer of agentic-skeleton), I want the skeleton tools the portal reads (next, backlog, check, plan, journal, story chain) and `wf.py version` to emit a versioned --json envelope with published JSON Schemas, so that the portal reads state without parsing Markdown and can report skeleton and contract versions.

### Refined description

Delivered in the agentic-skeleton repository. Contract 1.0 tool list is the Story's list plus `wf.py version --json`, which AP0101 needs for health. The owner allowed splitting if possible.

## 3. Scope

### In scope

- Envelope `{contract, tool, data}` with schemas for: next, backlog, check, plan, journal, story chain, and `wf.py version --json` (skeleton version + contract version).
- Error envelope `{contract, tool, error:{code, message}}`, no `data`, non-zero exit; empty states are valid `data` with empty lists.
- Schemas (JSON Schema 2020-12) shipped in the skeleton under `schemas/`; `jsonschema` only as a CI/test dependency; skeleton CI schema tests; tagged release.
- Skeleton tools run on Python 3.14 (owner override of the Analysis).

### Out of scope

- Write commands (including gates approve/request-changes), launcher (AP0106).
- context, repo_map, gates list (later stories).
- Portal-side contract tests and mtime caching (separate/later stories).

## 4. Confirmed Information

### Facts

- ADR-002 rules: semver on `contract`; same major accepted, minor ≥ built-for; minor only adds fields; subprocess calls only.
- Only `next_step.py` has --json today. Skeleton files are changed upstream only (NFR-14).

### Decisions confirmed during refinement

- Tool list for 1.0: the Story's list (owner). The analyst adds `wf.py version --json` as a consequence of the AP0101 decision.
- AI implements and tags in agentic-skeleton; review by human + AI.
- Python 3.14 baseline for skeleton tools.
- Split allowed if possible; if already atomic, keep it.
- Not overridden, therefore standing: runtime check of the `contract` version only; portal constant `CONTRACT_BUILT_FOR`; error envelope as above; portal-side contract tests as a new story.

### Residual assumptions

- The analyst judges the story splittable: (a) envelope + `wf.py version` + schema/CI infrastructure + first tagged release; (b) remaining tools. This is a proposal until the backlog is changed.
- Raising the skeleton to Python 3.14 may break existing workflow repos on older Python (not assessed).

## 5. Confirmed Acceptance Criteria

- Given a skeleton tool with --json, when it runs, then it prints an envelope with `contract: 1.x` that validates against its schema.
- Given `wf.py version --json`, when it runs, then it reports skeleton version and contract version.
- Given a tool failure, when it runs with --json, then it prints the error envelope and exits non-zero.
- Given a breaking output change, when it is released, then the contract major version is bumped.
- Given the skeleton CI on Python 3.14, when it runs, then schema tests for every envelope are green and a tagged release exists.

## 6. Remaining Open Points

### Functional

- Execute the split in `backlog/stories.toml` (backlog change; the human confirms). If done, AC are distributed between the two stories and `wf.py version` goes to part (a), which unblocks AP0101.

### Technical

- ADR-002's contract table must be updated (plan, journal, story chain added; context, repo_map, gates later): architecture change, owner approval required. Blocks the Spec, not Brief intake.
- Need a new portal-side story for contract tests (NFR-13).
- Skeleton tool baseline Python 3.14 vs existing repos: compatibility to check in the Brief.

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Envelope helper, `wf.py version`, schemas and validation tests, skeleton CI, tag; then one task per remaining tool.

### Boundaries to respect

- Only in agentic-skeleton; no portal runtime dependency; breaking changes bump major.

## 8. Refinement Outcome

- Story ready with residual open points to track
