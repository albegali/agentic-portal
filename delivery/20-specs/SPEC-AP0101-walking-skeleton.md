# SPEC-AP0101 - Walking skeleton

## References
- Story ID: AP0101
- Brief: BRIEF-AP0101
- RUN: RUN-AP0101

---

## Status
Done

---

# 1. Goal

A Python >= 3.14 stdlib server bound to 127.0.0.1 serves a prebuilt Vite/React placeholder page and `GET /api/health`; build, lint, tests, dependency check and GitHub Actions CI produce and publish a release bundle zip with manifest.

---

# 2. User / Business Value

As a development team
I want a tested, loopback-only server with a prebuilt page and a release pipeline
So that every later story has its place ready and a runnable artifact exists from day one.

---

# 3. Scope

Included:
- `server/portal_server/` package with entry point; static file serving of `web/dist/`; `GET /api/health`; `--host` option that refuses any non-loopback address (NFR-01); Python < 3.14 check with clear exit message.
- `web/` Vite/React/TypeScript scaffold with a placeholder page showing the portal version fetched from `/api/health`; Vitest tests, lint, typecheck.
- `tools/check_deps.py`-style dependency check (stdlib `ast`; allows only `sys.stdlib_module_names` and local packages). Placed outside skeleton files (e.g. `scripts/`), see Notes.
- `VERSION` file; bundle build script producing `agentic-portal-<version>.zip` (`server/`, `web/dist/`, `VERSION`) and `manifest.json`.
- GitHub Actions: CI (Linux full pipeline; macOS and Windows server tests + bundle start smoke test); release workflow on version tag publishing zip and manifest to GitHub Releases.
- `server/AGENTS.md` and `web/AGENTS.md` (package rules) if absent.

Out of scope:
- Domain features, authentication, app shell (AP0108), launcher `tools/portal.py` (AP0106), contract/skeleton version detection (AP0103), AWS infrastructure.
- Any change to skeleton files (NFR-14).

---

# 4. Acceptance Criteria

- [x] AC1: Given the cloned repository, when I run `make setup && make test`, then server and web tests pass.
- [ ] AC2 (pending first CI run on GitHub): Given a merge on main, when the pipeline runs, then build, lint and tests are green and a bundle zip with SHA-256 and `manifest.json` are produced.
- [x] AC3: Given the server started from the bundle on a machine without Node, when I open its URL, then the page loads and `/api/health` returns datetime, status and portal, contract and skeleton versions ("unknown" until AP0103).
- [x] AC4: Given a third-party import in `server/`, when the dependency check runs in CI, then the pipeline fails.
- [x] AC5: Given the server started, when its sockets are inspected, then it listens only on 127.0.0.1, and a non-loopback `--host` is refused with an error.
- [x] AC6: Given Python older than 3.14, when the server starts, then it exits non-zero with a message stating the requirement.
- [ ] AC7 (pending owner tag `v0.1.0`): Given a version tag, when the release workflow runs, then a GitHub Release holds the zip and manifest whose SHA-256 values match.

---

# 5. Tasks

- `TSK-AP0101-01` Server package: entry point, loopback-only binding and host refusal, Python version check, static serving, unit tests.
- `TSK-AP0101-02` `GET /api/health` with the shape in Notes, plus tests.
- `TSK-AP0101-03` Web scaffold (Vite/React/TS), placeholder page showing the portal version, Vitest, lint, typecheck.
- `TSK-AP0101-04` Dependency-check script and its tests (fails on third-party import, passes on stdlib/local).
- `TSK-AP0101-05` `make setup/test/lint` wiring and bundle build script producing zip + `manifest.json`; test of manifest checksums and of starting the server from the bundle.
- `TSK-AP0101-06` GitHub Actions: CI matrix (Linux full; macOS/Windows server tests + bundle smoke test) and tag-triggered release workflow.
- `TSK-AP0101-07` Package rules `server/AGENTS.md`, `web/AGENTS.md`; docs touched by persistence.

---

# 6. Execution Boundaries

The agent is allowed to:
- Create `server/`, `web/`, `scripts/`, `.github/workflows/`, `VERSION`, and Makefile targets needed by the tasks.
- Add dev-only dependencies to `web/` and test/lint tools for development.

The agent is not allowed to:
- Add any third-party runtime dependency to `server/` (NFR-08).
- Modify skeleton files (`tools/`, `workflow/`, templates) (NFR-14).
- Change the bundle/manifest format without AP0106.
- Bind to non-loopback addresses, or add auth, domain features or shell screens.
- Push tags or publish a release itself: the owner triggers it.

---

# 7. Quality Gates

- [x] Tests added/updated
- [x] Build passes
- [x] Public interfaces updated if impacted (health JSON, bundle layout, manifest)
- [x] Domain invariants respected (loopback only, stdlib only, no Node at runtime)
- [x] No breaking changes unless explicitly approved
- [x] Dependency check green; CI matrix green (matrix pending first run)

---

# 8. Stop Conditions

Stop and ask for supervision if:
- acceptance criteria are ambiguous
- a breaking change is required
- security or permission rules are unclear
- architectural alternatives are non-trivial (e.g. conflict with ADR-003)
- work appears out of scope, or a skeleton file needs changing
- Python 3.14 is unavailable on a CI runner

---

# 9. Impacted Areas

- Code: `server/`, `web/`, `scripts/`, `.github/workflows/`
- Interfaces: `GET /api/health`; bundle zip layout; `manifest.json`
- Domain: none
- UX: placeholder page only
- Platforms / distribution: Linux, macOS, Windows; GitHub Releases
- Tests: `server/tests`, `web` Vitest, dependency-check tests, bundle smoke test
- Docs: architecture.md §6/§7 only if the implementation deviates

---

# 10. Notes / Clarifications

- Health response (Spec decision): `{"status": "ok", "datetime": "<UTC ISO-8601, e.g. 2026-10-19T12:00:00Z>", "portal_version": "<VERSION>", "contract_version": "unknown", "skeleton_version": "unknown"}`; on failure `status: "error"` plus `error: {"code", "message"}`. "Unknown" is the literal string `"unknown"`.
- Manifest `contract_built_for` is `"unknown"` in the first bundle; `python_min` is `"3.14"`.
- The dependency check lives in `scripts/` rather than `tools/` to respect NFR-14.
- The published release requires the owner's repository permissions; the agent prepares the workflow only.

---

# 11. Final Reconciliation

To be completed before marking Done.

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- TSK-01..07 done. Verified locally: server 10, scripts 6, web 2 tests; lint, typecheck, build, dependency check; server started from the extracted bundle without Node; owner checked the running app. Deferred: AC2 and AC7 need GitHub (push, tag `v0.1.0`). Only deviation: `project.toml [stack]` wiring (RUN §6).
