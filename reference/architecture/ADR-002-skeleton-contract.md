---
artifact_type: adr
id: ADR-002
status: accepted
date: 2026-10-19
drivers: [FR-25, FR-27, FR-14, FR-24, NFR-13, NFR-14]
---

# ADR-002 — Skeleton contract: tool CLIs with a versioned JSON envelope

## Context
The repository files are the source of truth and the portal reads them through the skeleton's tools (FR-25). The portal must work in any workflow repository, at whatever skeleton version it has (FR-24), and detect incompatible versions (FR-27, mismatch shown only in Settings). Gate writes must be the same change a human or agent would make (FR-14). The owner delegated the contract design to this step. Today only `next_step.py` has `--json`.

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. Subprocess calls to `tools/*.py --json`; every output is an envelope `{"contract": "1.2", "tool": "...", "data": {...}}` validated against JSON Schemas shipped with the skeleton; writes through new skeleton commands | Process boundary independent of internals; version check on every call; the same commands are usable by humans and agents | Process start per call (mitigated by caching on file mtimes); skeleton needs new `--json` outputs and a write command | Strong: FR-24, FR-25, FR-27, NFR-13 |
| B. Import the tools as Python modules | Fast, no schemas | Couples the portal to internal signatures; weak version detection | Weak: FR-27, NFR-13 |

## Decision
Option A (owner-confirmed 2026-10-19). Direction: tools → portal for reads; portal → tools for writes. Versioning: semver on `contract`; the portal accepts the same major and any minor ≥ the one it was built for; minor versions only add fields.

Contract surface (v1, upstreamed to agentic-skeleton):
| Tool | Output |
|---|---|
| `next_step.py --json` | phase, next step, mode, tier, IDs, why (exists; wrap in envelope) |
| `gen_backlog.py --json` (read-only view) | epics, stories, status, owner, sprint, deps |
| `check_workflow.py --json` | errors, warnings, counts |
| `context.py <step> <IDs> --json` | file list and token estimate (used for run scope) |
| `repo_map.py --json` | packages, files, sizes (Insights, diagrams) |
| `gates.py list --json` | pending human gates: artifact, field, current value, proposed value |
| `gates.py approve|request-changes <gate-id> --by <owner> [--comment]` | applies the change, returns the diff |
| `wf.py version --json` | skeleton and contract version |

## Consequences
- Positive: portal and skeleton evolve separately; mismatch is a clear message (Settings); gates are applied by the same code humans and agents use.
- Negative / trade-offs: upstream work in agentic-skeleton before the portal can show some screens; contract tests needed on both sides.
- Follow-up stories: envelope + `wf.py version`; `--json` for each tool; `gates.py`; contract tests (NFR-13).

## Reversibility
High: every screen depends on the contract. Additions are cheap (minor versions); a new major needs a coordinated release.
