# server/ — package rules

Python ≥ 3.14, **standard library only** at runtime (NFR-08). See `reference/architecture/architecture.md` §2 and ADR-002, ADR-004..ADR-008.

## Layout
- `server/portal_server/` — package: `http/` (routing, auth, SSE), `contract/`, `runs/` (`adapters/` per CLI), `gates/`, `insights/` (`adapters/` per analyzer), `diagrams/`, `settings/`, `store/` (`.portal/`).
- `server/tests/` — `unittest`; fixtures in `server/tests/fixtures/` (sample repository, recorded tool envelopes, recorded analyzer outputs, fake agent CLI script).

## Rules
- Read and write project state only through the skeleton tools (`contract`); never parse or edit workflow Markdown/TOML here.
- Every API route goes through the auth + Host/Origin middleware; add a test per new route (NFR-02).
- Subprocesses: argument lists (never `shell=True`), allow-listed commands only, own process group, timeouts.
- Paths from requests are resolved and checked to stay under the repository root.
- Redact run output before writing to `.portal/` or streaming.
- Cross-platform: `pathlib`, no POSIX-only calls without a Windows branch.

## Commands
- Test: `python3 -m unittest discover -s server/tests -q`
- Lint: `python3 -m compileall -q server`
