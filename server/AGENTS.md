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

## Skeleton call API (`portal_server/contract/`)
- One entry point: `gate_for(root).call(tool, *args)` → `Ok(envelope)` (`.data`) or `ContractError(kind, message)`; kinds `incompatible`, `missing-tool`, `timeout`, `bad-output`, `tool-error`. Never run a skeleton script elsewhere; there is no cache yet (hook point = `Gate.call`).
- Tools are a fixed table in `runner.TOOLS` (`version`, `next`, `next-story`, `backlog`, `check`, `plan`, `journal`, `story`), run as `sys.executable tools/<script> --json` with cwd = repository root, 30 s, 5 MB cap, process group killed on timeout. A non-zero exit with a data envelope is `Ok` (`check` reports problems that way).
- Every envelope is validated against `schemas/envelope.schema.json` and its tool schema by the stdlib subset validator; a keyword outside the subset raises `UnsupportedSchemaKeyword` (skeleton change or Spec update, do not widen silently).
- API routes return `(status, body)` or a body; `/api/contract*` and health are exempt from the 409 guard, never from auth. Contract tests: `jsonschema` is allowed only under `server/tests/` (`scripts/check_deps.py`).
- Recorded envelopes in `server/tests/fixtures/envelopes/` come from real emitter output (re-record when the pin moves); `SKELETON_PIN` is in `project.toml [portal] skeleton_pin` and CI.

## Commands
- Test: `python3 -m unittest discover -s server/tests -q`
- Lint: `python3 -m compileall -q server`
