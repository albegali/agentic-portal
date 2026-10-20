---
artifact_type: analysis
us_id: STORY_AP0105
title: Upstream gates.py
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0105_upstream_gates_tool.md
  - reference/project-summary.md
related_references:
  - reference/product/functional-requirements.md#FR-13
  - reference/product/functional-requirements.md#FR-14
  - reference/product/non-functional-requirements.md#NFR-03
  - reference/product/non-functional-requirements.md#NFR-14
  - reference/architecture/ADR-002-skeleton-contract.md
  - reference/architecture/ADR-006-local-security.md
last_updated: 2026-10-20
---

# Analysis AP0105 - Upstream gates.py

## 1. References

- ID: AP0105
- Source story: analysis/10-stories/STORY_AP0105_upstream_gates_tool.md
- Roadmap phase: R1 (sprint S2 in PLAN.md)
- Sources used: Story, project summary, FR-13, FR-14, NFR-03, NFR-14, ADR-002, ADR-006, Analysis AP0103 §6+, `AGENTS.md` §3, `tools/next_step.py` (human gates), `project.toml` (`owner`)
- Missing sources: the skeleton's step files that define each gate field (`workflow/steps/*.md`), templates' status values, workshop minutes format; the gates-related parts of `/spec`, `/run` and `/refine` were not read

## 2. Original User Story

### Story text

As a portal (consumer of agentic-skeleton), I want a gates.py tool that lists pending human gates and records approve or request-changes exactly as a human edit, attributed to the project.toml owner with date, so that the portal never edits workflow files directly.

### Description

- Epic: EP-01 — Technical foundations
- Priority (MoSCoW): Must · Release: R1 · Size: M · Type: technical
- Requirements: FR-13, FR-14, NFR-03, NFR-14
- Depends on: AP0103
- Notes: ADR-002, ADR-006. Delivered in the agentic-skeleton repository (NFR-14); the portal pins the released skeleton version.
- Out of scope: Portal UI, agent-caller checks.

## 3. Intent Understanding

### Functional goal

- Provide, upstream, the single command that lists pending human gates and applies an approval or a change request, so humans, agents' tooling and the portal produce the same file edit.

### Actors involved

- Owner (approver, from `project.toml`); portal server (caller); agents (must never pass gates, AGENTS.md §3); skeleton maintainers.

### Expected outcome

- `gates.py list --json`, `approve`, `request-changes` released in the skeleton as a contract minor, ready for the portal's Approvals screens (EP-04) and for AP0104 to consume.

## 4. Information Classification

### Facts

- AGENTS.md §3: agents never pass human gates; gates are inception approvals, workshop, Spec `Ready`, RUN strategy approval, tuning acceptance. Pending gates are phrased as `file → field → value`.
- Existing gate information: `next_step.py --json` exposes `human_gates` as `{id, stage, detail}` per story; no tool lists inception approvals as artifact/field/value.
- FR-14: write exactly as a human edit (e.g. `status: approved`), attributed to the owner in `project.toml` (`owner = "Alberto Galimberti"`) with date; the action modifies only the gate field; request-changes records a comment. FR-13: each gate shows artifact, what is being approved and age.
- ADR-002 (later minor, not in 1.0): `gates.py list --json` returns artifact, field, current value, proposed value; `approve|request-changes <gate-id> --by <owner> [--comment]` applies the change and returns the diff. ADR-002 revision: the tool is released as a later minor than 1.0; the `v1.0.0` tag follows AP0109.
- ADR-006: agent-caller checks and the confirm nonce belong to the portal (EP-04); agent processes get an environment without the token.
- Skeleton tools keep Python ≥ 3.11 (ADR-002); the envelope and schemas live in the skeleton (AP0103).

### Clarifications received

- Owner decision 2026-10-19: approvals are attributed to the owner defined in `project.toml`.

## 5. Original Acceptance Criteria

- Given a repository with pending gates, when I run `gates.py list --json`, then each gate is listed with artifact, gate type and age in the envelope.
- Given a pending gate, when I run `gates.py approve`, then only the gate field changes and owner and date are recorded.
- Given a pending gate, when I run `gates.py request-changes` with a comment, then the comment is recorded and no approval is written.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- **Which gates exist as files.** Inception artifacts have a `status` field; Spec `Ready`, RUN strategy and tuning acceptance live in delivery artifacts; the **workshop** gate is a human event whose evidence is the minutes file. What does "approve the workshop" write?
- **What `request-changes` does to the artifact**: reset status to `draft`/`proposed`, keep it and add a comment, or both? "No approval written" is the only stated effect.
- **Where the comment and the attribution are recorded** (a revision line inside the artifact, a journal entry, or a sidecar).
- **"Age"**: since when is a gate pending, and from which source (file mtime, git commit date, a date in the artifact)?
- Story AC lists "artifact, gate type and age"; ADR-002 lists "artifact, field, current value, proposed value" (and FR-14 acceptance wants the field). Which fields does the envelope carry?
- Attribution: the Story reads `project.toml` owner; ADR-002 passes `--by <owner>` from the caller. Who is authoritative?

### Functional gaps

- No AC for: unknown or already-resolved gate id, a gate that changed since it was listed (stale approval), empty list, invalid status transition, missing `owner` in `project.toml`, request-changes without a comment.
- No AC for the diff returned (ADR-002) and for the error envelope.
- No statement on whether `gates.py` may be run by agents from the command line: it is a repository tool, so any agent could approve its own work (agents never pass gates); "agent-caller checks" are out of scope.

### Technical gaps

- Gate catalog and gate-id scheme (stable, derivable from `artifact + field`).
- Edit mechanics: line-oriented front-matter/field edit that preserves the rest of the file byte for byte, on LF and CRLF; atomic write.
- Contract versioning: new tool `gates` means a minor bump and a schema; the portal's `CONTRACT_BUILT_FOR` must move with it (AP0104).
- Python 3.11 compatibility in skeleton CI; fixtures for each gate type.
- Existing `next_step.py` gate detection and `gates.py list` must agree (single implementation).

### Dependencies or ownership points to clarify

- Delivered in the skeleton repository: who implements, reviews, tags (same open point as AP0103); the portal pins the released version.
- Depends on AP0103 only, but the tag/minor numbering depends on AP0109's `v1.0.0`; confirm the release order (1.0.0 → 1.1.0).
- Consumers: AP0104 (client) and the EP-04 Approvals stories; their nonce/agent checks are what actually prevents agents from approving through the portal.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions only: an answer from the PO / stakeholder is mandatory.

- [High impact] For each human gate (inception approval, workshop, Spec `Ready`, RUN strategy, tuning acceptance), what exactly must "approve" change in the files, and what must "request changes" do (back to draft, stay, mark as blocked)? — defines the behaviour the owner will see in every approval and is the heart of the story.
- [High impact] Where must the owner's change comment and the approval attribution (owner, date) be visible: inside the artifact (revision line, as AGENTS.md describes for owner decisions), in the project journal, or both? — traceability expected by the owner and reviewers.
- [High impact] Is it acceptable that, until the portal's agent-caller checks exist, an agent with shell access can run `gates.py approve` itself? — AGENTS.md says agents never pass gates; the story leaves enforcement out of scope, so the residual risk must be accepted or a minimal guard added here.
- [Medium impact] Should the workshop gate be a listed, approvable gate (what evidence: minutes file present?) or only informational? — the workshop is a human event, not a file field.
- [Medium impact] What does the owner expect "age" to mean (time since the artifact entered the pending state, or since last edit)? — FR-13 acceptance depends on it.
- [Low impact] Should a stale approval (artifact changed since the owner looked) be refused with a message to refresh? — user-visible safeguard.

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Gate catalog and ids — **Proposal**: derive gates from the same detection `next_step.py` uses, expose `{id, type, artifact, field, current, proposed, story_id?, since}` with `id = <type>:<artifact path>` (stable, no counters), types `inception`, `workshop`, `spec`, `run-strategy`, `tuning`; `next_step.py --json` `human_gates` keeps its shape and is fed by the same function · **Why**: ADR-002 fields plus the Story's gate type and age; one implementation · **Alternatives**: two detections (drift) · **Confidence**: medium
- [High impact] Attribution — **Proposal**: `approve|request-changes <gate-id> [--comment …]` takes the approver from `project.toml` `owner`; `--by` is optional and accepted only if equal to the owner (ADR-002 text updated by revision), date = today in ISO format from the system clock · **Why**: FR-14 and owner decision; the Story is authoritative · **Alternatives**: required `--by` passed by the portal (trusts the caller) · **Confidence**: medium
- [High impact] Edit semantics — **Proposal**: `approve` changes only the gate field (`status: proposed → approved`, `Ready`, `approved`, `accepted` as each template defines) and appends one revision line `YYYY-MM-DD — approved by <owner> (gates.py)` where the artifact has a revision section; `request-changes` sets the field to its draft value, appends `YYYY-MM-DD — changes requested by <owner>: <comment>` and never writes an approval value; both print a unified diff in `data.diff` · **Why**: AGENTS.md owner-decision rule and FR-14 acceptance hints · **Alternatives**: comment only in the journal · **Confidence**: medium
- [Medium impact] Age — **Proposal**: `since` = date of the last commit that touched the gate field (`git log -1 --format=%cI -- <file>`), falling back to file mtime when git is unavailable; `age_days` computed at call time · **Why**: mtime changes on clone/checkout · **Alternatives**: mtime only (simple, inaccurate) · **Confidence**: medium
- [Medium impact] Safety of writes — **Proposal**: refuse when the current value differs from the listed `current` (optional `--expect <value>`, portal always sends it), write atomically (temp file + replace), keep line endings, touch only files under the repository root, refuse paths from outside `list` output · **Why**: NFR-03, stale approvals · **Alternatives**: no expect check · **Confidence**: high
- [Medium impact] Contract — **Proposal**: new tool name `gates`, schema `gates.schema.json` and `gates-action.schema.json`, released as contract 1.1 and skeleton `tools/VERSION` next minor, error codes `unknown_gate`, `stale_gate`, `invalid_transition`, `no_owner`, `comment_required` · **Why**: ADR-002 later-minor policy · **Alternatives**: extend `next` · **Confidence**: high
- [Medium impact] Minimal agent guard — **Proposal**: out of scope as stated, but the tool refuses to run when the environment variable `WF_AGENT=1` is set (the portal sets it for agent processes in a later story; documented in tools/README.md) · **Why**: cheap defence in depth without touching the portal · **Alternatives**: nothing now · **Confidence**: low
- [Low impact] Tests — **Proposal**: unittest fixture repositories for each gate type on Python 3.11 and 3.14, including CRLF and a no-git directory · **Confidence**: high

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-20)

See `analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md` and the Refined Story. Owner decisions recorded there change §7 proposals; the rest stands.
