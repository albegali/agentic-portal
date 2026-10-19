---
artifact_type: adr
id: ADR-008
status: accepted
date: 2026-10-19
drivers: [FR-25, FR-10, NFR-05, NFR-12]
---

# ADR-008 — Portal state: repository files + a gitignored `.portal/` directory, no database

## Context
Project state lives in repository files (FR-25). The portal also has data of its own: run history and logs (FR-10, NFR-12), findings cache, the downloaded bundle. Deleting it must not lose project state.

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. JSON/JSONL files in gitignored `.portal/` (`runs/<id>.json` + `runs/<id>.log`, `findings.json`) | stdlib only, inspectable, disposable | No queries; files grow (rotation needed) | Good |
| B. SQLite (stdlib `sqlite3`) | Queries, atomic writes | Opaque file; schema migrations | Unnecessary for the volumes |

## Decision
Option A. Run logs are redacted before writing (NFR-05); old runs rotated after a configurable count (default 200).

## Consequences
- Positive: nothing to migrate; deleting `.portal/` resets the portal only.
- Negative / trade-offs: concurrent writes guarded by the run manager (single process).
- Follow-up stories: run store with rotation.

## Reversibility
Low: storage is behind a small repository interface.
