---
artifact_type: refined
us_id: STORY_AP0105
title: Upstream gates.py
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0105_upstream_gates_tool.md
  - analysis/20-analysis/ANALYSIS_AP0105_upstream_gates_tool.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md
related_references:
  - reference/architecture/ADR-002-skeleton-contract.md
  - reference/architecture/ADR-006-local-security.md
  - reference/product/functional-requirements.md#FR-13
  - reference/product/functional-requirements.md#FR-14
  - reference/product/non-functional-requirements.md#NFR-14
last_updated: 2026-10-20
---

# Refined Story AP0105 - Upstream gates.py

## 1. References

- ID: AP0105
- Title: Upstream gates.py
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, ADRs listed above
- Missing sources: skeleton step files defining each gate field and the template status values (to read in the Brief)
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md

## 2. Refined User Story

### Refined story text

As a portal (consumer of agentic-skeleton), I want a gates.py tool that lists pending human gates and records approve or request-changes exactly as a human edit, attributed to the project.toml owner with date, so that the portal never edits workflow files directly.

### Refined description

Delivered in agentic-skeleton as a contract minor; AI implements and tags, human + AI review.

## 3. Scope

### In scope

- `gates.py list --json`: `{id, type, artifact, field, current, proposed, story_id?, since, age_days}`, types `inception`, `workshop`, `spec`, `run-strategy`, `tuning`; id `<type>:<artifact path>`; one detection shared with `next_step.py` (`human_gates` keeps its shape).
- `approve` / `request-changes <gate-id> [--comment] [--expect <value>]`: approver is the `project.toml` owner (`--by` optional, accepted only if equal); date today (ISO).
- Edits touch only the gate field plus one line in a `## Gates` section of the artifact: `YYYY-MM-DD — approved|changes requested by <owner>: <comment>`; the skeleton templates get the section.
- Refuse stale actions, unknown ids, invalid transitions, missing owner, missing comment on request-changes; atomic write, line endings preserved, only files from `list`.
- New tool `gates` with schemas and a contract minor; `WF_AGENT=1` makes the tool refuse to run.
- Tests on Python 3.11 and 3.14, CRLF, no-git directory.

### Out of scope

- Portal UI, agent-caller checks and confirm nonce (EP-04).
- Journal entries or sidecar files.

## 4. Confirmed Information

### Facts

- AGENTS.md §3: agents never pass human gates; FR-14: write exactly as a human edit, attributed to the owner.
- ADR-002 lists `gates` as a later minor; tag numbering follows AP0109.

### Decisions confirmed during refinement

- All Analyst proposals approved (ids, shared detection, owner attribution, edit only the gate field, refuse stale actions).
- What approve and request-changes change per gate: AI decides, Analyst proposals stand (approve sets the template's approved value; request-changes sets the draft value and never an approval value; both return `data.diff`).
- Comment and attribution live in a dedicated `## Gates` section (owner delegated: name and line format as above).
- An agent running `gates.py approve` before caller checks exist is acceptable (residual risk accepted).
- Standing (proposal accepted by default): age from the last commit touching the gate field, fallback mtime; error codes `unknown_gate`, `stale_gate`, `invalid_transition`, `no_owner`, `comment_required`; the `WF_AGENT` guard (low confidence, may be dropped in the Spec).

### Residual assumptions

- The workshop gate is listed with the minutes file as evidence and approving it only records a `## Gates` line (no field change); the Spec confirms.

## 5. Confirmed Acceptance Criteria

- Given a repository with pending gates, when I run `gates.py list --json`, then each gate has artifact, type, field, current, proposed and age in the envelope and validates against its schema.
- Given a pending gate, when I run `gates.py approve`, then only the gate field changes and one `## Gates` line with owner and date is added.
- Given a pending gate, when I run `gates.py request-changes` with a comment, then the comment is recorded in `## Gates`, the field returns to its draft value and no approval is written.
- Given an unknown, stale or already resolved gate, a missing owner or a missing comment, when an action runs, then the matching error envelope is returned, non-zero exit and nothing is written.
- Given CRLF files, when an action runs, then line endings and all other bytes are preserved.

## 6. Remaining Open Points

### Functional

- None blocking.

### Technical

- Per-gate field and value table to be taken from the skeleton step files and templates in the Brief.
- Adding `## Gates` to the templates may need a `check_workflow` allowance.

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Gate catalog and shared detection; edit mechanics; templates update; schemas and contract minor; error codes; tests; README entry.

### Boundaries to respect

- Only in agentic-skeleton (NFR-14); Python ≥ 3.11 stdlib; `next_step.py --json` output unchanged.

## 8. Refinement Outcome

- Story ready with residual open points to track
