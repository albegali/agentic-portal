---
artifact_type: analysis
us_id: STORY_AP0103
title: Upstream --json envelope and JSON Schemas
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0103_upstream_json_envelope.md
  - reference/project-summary.md
related_references:
  - reference/product/functional-requirements.md#FR-27
  - reference/product/functional-requirements.md#FR-25
  - reference/product/non-functional-requirements.md#NFR-13
  - reference/product/non-functional-requirements.md#NFR-14
  - reference/architecture/ADR-002-skeleton-contract.md
last_updated: 2026-10-19
---

# Analysis AP0103 - Upstream --json envelope and JSON Schemas

## 1. References

- ID: AP0103
- Source story: analysis/10-stories/STORY_AP0103_upstream_json_envelope.md
- Roadmap phase: R1
- Sources used: project summary, Story, FR-27, FR-25, NFR-13, NFR-14, ADR-002
- Missing sources: agentic-skeleton repository state (existing tools, release process, test setup); PLAN.md; analysis of AP0101/AP0106

## 2. Original User Story

### Story text

As a portal (consumer of agentic-skeleton), I want the skeleton tools the portal reads (next, backlog, check, plan, journal, story chain) to emit a versioned --json envelope with published JSON Schemas, so that the portal reads state without parsing Markdown.

### Description

Epic EP-01 · Must · R1 · L · technical · FR-27, FR-25, NFR-13, NFR-14 · Depends on: — · Delivered in the agentic-skeleton repository; the portal pins the released skeleton version · Out of scope: write commands, launcher.

## 3. Intent Understanding

### Functional goal

- Give the portal a stable, versioned, machine-readable read interface to skeleton state.

### Actors involved

- Portal (consumer); skeleton maintainers (owner of the upstream change); humans/agents using the same CLIs.

### Expected outcome

- A tagged skeleton release whose tools emit schema-valid envelopes with `contract: 1.x`.

## 4. Information Classification

### Facts

- ADR-002 (accepted): tools emit `{"contract","tool","data"}`; semver on `contract`; same major accepted, minor ≥ built-for; minor only adds fields; subprocess calls, no module import.
- Only `next_step.py` has `--json` today (ADR-002).
- Skeleton files must not be modified locally; changes go upstream (NFR-14); contract tests required in CI (NFR-13).
- Version mismatch is shown clearly (FR-27); ADR-002 says only in Settings.

### Clarifications received

- Contract design delegated to /architecture (owner 2026-10-19), resulting in ADR-002.

## 5. Original Acceptance Criteria

- Given a skeleton tool with --json, when it runs, then it prints an envelope with `contract: 1.x` that validates against its schema.
- Given a breaking output change, when it is released, then the contract major version is bumped.
- Given the skeleton CI, when it runs, then schema tests for every envelope are green and a tagged release exists.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- **Conflict on tool list**: the Story names next, backlog, check, plan, journal, story chain; ADR-002's surface is next_step, gen_backlog, check_workflow, context, repo_map, gates list/approve, wf.py version. plan, journal and story chain have no ADR entry; context, repo_map, gates list and version have no Story mention. Which list is authoritative?
- "Every envelope" in AC 3: is the set closed to the initial list?

### Functional gaps

- Gate writes (`gates.py approve|request-changes`) are excluded as "write commands", but `gates list --json` is read-only: in or out?
- No AC on error envelopes (tool failure, repo not a workflow repo, empty states).
- "Mismatch message" behaviour (FR-27) depends on the portal reading `wf.py version`; not covered here.

### Technical gaps

- Schema validation without third-party libraries (stdlib has none) in skeleton CI and in the portal contract tests (NFR-13).
- Where schemas are published and how the portal gets them (shipped in the skeleton, per ADR) and how portal pins them.
- Minimum compatible-minor policy: how is "built for" recorded in the portal?
- Skeleton Python baseline vs. portal's ≥ 3.14.
- Size L with ≥ 8 tools may warrant splitting.

### Dependencies or ownership points to clarify

- Delivery in a separate repository: who implements, reviews and tags there; what gets tracked in this backlog.
- Blocks AP0101 (versions in health), AP0106 pinning, and every screen reading state.
- Portal-side contract tests consuming released schemas are not in any listed story.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions: an answer from the PO / stakeholder is mandatory.

- [High impact] Which tools are in contract 1.0? — the Story lists next, backlog, check, plan, journal, story chain; ADR-002 lists next_step, gen_backlog, check_workflow, context, repo_map, gates list, wf.py version. Scope decides which portal screens R1 can show.
- [High impact] Split this L story (envelope + `wf.py version` first, then one story per tool)? — unblocks AP0101 health and AP0106 early; changes the backlog.
- [High impact] Who implements, reviews and tags in agentic-skeleton, and how is that work tracked in this backlog? — ownership across repositories (NFR-14).

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Schema validation without runtime deps — **Proposal**: schemas (JSON Schema 2020-12) shipped in the skeleton under `schemas/`; `jsonschema` used only as a CI/test dependency on both sides; at runtime the portal checks only the `contract` version · **Why**: NFR-08 binds the portal backend runtime, not tests; avoids writing a validator · **Alternatives**: minimal stdlib validator for the subset used · **Confidence**: medium
- [High impact] Portal-side contract tests (NFR-13) — **Proposal**: new portal story: CI checks out the pinned skeleton tag, runs each tool with `--json` on a fixture repo and validates against its schemas · **Why**: ADR-002 follow-up "contract tests on both sides" has no story yet · **Alternatives**: recorded fixtures only (drift risk) · **Confidence**: high
- [Medium impact] Error envelope — **Proposal**: `{"contract","tool","error":{"code","message"}}`, no `data`, non-zero exit; empty states are valid `data` with empty lists · **Why**: lets the portal show clear messages without parsing stderr · **Confidence**: medium
- [Medium impact] "Built for" version — **Proposal**: a portal constant `CONTRACT_BUILT_FOR`, compared with `wf.py version --json` and exposed in /api/health · **Why**: ADR-002 rule (same major, minor ≥ built-for) · **Confidence**: high
- [Medium impact] Python baseline of skeleton tools — **Proposal**: keep the skeleton's current baseline; only the portal requires ≥ 3.14 · **Why**: avoids breaking existing workflow repos · **Confidence**: low (skeleton baseline not read)
- [Low impact] mtime caching — **Proposal**: portal side, in a later story; not part of AP0103 · **Confidence**: high

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-19)

See the Refined Story. Changes to §7 proposals: Skeleton tools use Python 3.14; `wf.py version --json` added to the 1.0 tool list; split into two stories judged feasible.
