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

Contract surface (v1.0, upstreamed to agentic-skeleton; revised after the 2026-10-19 workshop):
| Tool | Output | Story |
|---|---|---|
| envelope | `{"contract","tool","data"}`; on failure `{"contract","tool","error":{"code","message"}}`, no `data`, non-zero exit; empty states are valid `data` with empty lists | AP0103 |
| `wf.py version --json` | skeleton and contract version | AP0103 |
| `next_step.py --json` | phase, next step, mode, tier, IDs, why (exists; wrap in envelope) | AP0103 |
| `gen_backlog.py --json` (read-only view) | epics, stories, status, owner, sprint, deps | AP0109 |
| `check_workflow.py --json` | errors, warnings, counts | AP0109 |
| plan `--json` | releases, sprints, stories per sprint (PLAN.md) | AP0109 |
| journal `--json` | context, decisions, learnings, weekly and monthly entries | AP0109 |
| story chain `--json` | artifacts of one ID (Story → RUN, tasks) with status and paths | AP0109 |

Schemas (JSON Schema 2020-12) for every v1.0 tool ship in the skeleton under `schemas/` with AP0103; `jsonschema` is a CI/test dependency only; at runtime the portal checks only the `contract` version against its `CONTRACT_BUILT_FOR` constant. Skeleton tools require Python 3.14 (owner, 2026-10-19). Exact tool names for plan, journal and story chain are fixed in the AP0103 Spec.

Later minor versions (not in v1.0):
| Tool | Output | Story |
|---|---|---|
| `gates.py list --json` | pending human gates: artifact, field, current value, proposed value | AP0105 |
| `gates.py approve|request-changes <gate-id> --by <owner> [--comment]` | applies the change, returns the diff | AP0105 |
| `context.py <step> <IDs> --json` | file list and token estimate (used for run scope) | to be created |
| `repo_map.py --json` | packages, files, sizes (Insights, diagrams) | to be created |

## Consequences
- Positive: portal and skeleton evolve separately; mismatch is a clear message (Settings); gates are applied by the same code humans and agents use.
- Negative / trade-offs: upstream work in agentic-skeleton before the portal can show some screens; contract tests needed on both sides.
- Follow-up stories: AP0103 (envelope, version, next, all v1.0 schemas); AP0109 (remaining v1.0 tools); AP0105 (`gates.py`); AP0104 (portal contract client and tests, NFR-13); context and repo_map stories still to be created.
- Revision 2026-10-19, owner decisions in `analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md`: v1.0 surface follows the Story list (plan, journal, story chain added; context, repo_map, gates moved to later minors); error envelope and Python 3.14 added.

## Reversibility
High: every screen depends on the contract. Additions are cheap (minor versions); a new major needs a coordinated release.
