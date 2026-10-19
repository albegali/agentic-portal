# RUN-AP0101

## References
- Story ID: AP0101
- Spec: SPEC-AP0101
- Started at (datetime): 2026-10-19T19:40:07Z
  - Fill only when execution starts after human approval, immediately before the first code or test change.
- Completed at (datetime): 2026-10-19T20:04:16Z
  - Fill only when the RUN is ready to close after verification, tuning and persistence.
  - If tuning or follow-up changes happen before closure, update this to the latest completion datetime.

---

## Status
Closed

> A RUN MUST NOT be Closed before Persisted.

---

# 1. Execution Strategy (Agent)

> MUST be written before any code.

### Required Reads
- [x] Target Spec
- [x] Scoped package `AGENTS.md` files, if applicable:
  - server/AGENTS.md
  - web/AGENTS.md
- [x] `delivery/templates/RUN-template.md`

### Plan
- Step 1 (TSK-01, 02): `server/portal_server/` (`__main__`, `app`, `health`, static serving of `web/dist/`), `ThreadingHTTPServer` bound to 127.0.0.1; `--host` accepts only loopback (127.0.0.0/8, ::1, `localhost`), else exit non-zero; Python < 3.14 check at the very top of the entry point (before other imports) with a clear message; `GET /api/health` per Spec Notes; static path traversal guard. `unittest` tests incl. socket-binding, host refusal, version-check (via injectable version tuple). Verify: `python3.14 -m unittest discover -s server/tests -q`.
- Step 2 (TSK-04): `scripts/check_deps.py` (stdlib `ast`; allows `sys.stdlib_module_names` + local packages, handles relative imports) plus tests with a third-party-import fixture. Verify: fails on fixture, passes on `server/`.
- Step 3 (TSK-03): `web/` Vite/React/TS scaffold, placeholder page fetching `/api/health` and showing the portal version; Vitest + Testing Library, ESLint, `tsc --noEmit`; dev proxy to the server. Verify: `npm --prefix web ci && test --run && lint && typecheck && build`.
- Step 4 (TSK-05): `VERSION`; `scripts/build_bundle.py` producing `dist-release/agentic-portal-<version>.zip` (`server/` without tests, `web/dist/`, `VERSION`) and `manifest.json` (version, sha256, `python_min` "3.14", `contract_built_for` "unknown"); tests on checksums and on starting the server from the extracted zip (no Node needed). Wire `make setup/test/lint` through `project.toml [stack]` (already defined) adding the dep check, bundle test and `PY` override; no change to skeleton Makefile logic beyond a possible `bundle` target.
- Step 5 (TSK-06): `.github/workflows/ci.yml` (Linux: setup, lint, dep check, tests, build, bundle + sha256 artifact; macOS/Windows: server tests + bundle smoke, `actions/setup-python` 3.14) and `release.yml` on `v*` tag publishing zip + manifest via `gh release`. Not pushed or triggered; YAML validated locally.
- Step 6 (TSK-07): confirm `server/AGENTS.md`/`web/AGENTS.md` still match (they exist); note deviations in RUN §6; leave docs to `/persist`.

### Assumptions
- Local `python3` is 3.12; `python3.14` exists at /opt/homebrew/bin, so server tests/lint run with `PY=python3.14` (project.toml `python3` commands left as is; CI uses 3.14).
- Node 24 / npm 11 locally; `package-lock.json` is committed for `npm ci`.
- Web dev dependencies (vite, react, vitest, eslint, typescript, testing-library) are allowed as dev-only; `react`/`react-dom` are build-time only because the bundle ships static assets.
- `web/dist/` is gitignored, so the server tolerates its absence (returns a clear 404 / hint) and tests build a temp dist.
- Health `datetime` is UTC ISO-8601 with `Z`; versions read from `VERSION` (bundle: next to `server/`; repo: root).

### Risks / Open Questions
- Python 3.14 on GitHub runners (3.14 must be available in `setup-python`): Spec Stop Condition if not.
- Windows: bundle smoke test and path handling (`pathlib`, zip separators) may need branches; process start/stop in the smoke test is cross-platform via `subprocess` + port 0 and terminate.
- Binding `localhost` may resolve to non-loopback in odd setups: resolve and check the address, else refuse.
- Release workflow cannot be verified end to end (AC7) without a tag; verified by review and a dry local run of the build script only.
- Top-level `Makefile` is skeleton (NFR-14): additions limited to what Spec allows; if a skeleton edit is needed beyond that, stop.

### Scoped Agent Rules Check
- Applies: Yes
- Files read:
  - server/AGENTS.md
  - web/AGENTS.md
- Notes:
  - Server stdlib only, `unittest`, `pathlib`, resolved-path checks. Auth/SSE/contract rules belong to later stories (out of scope here); web rules (tokens, a11y, e2e) apply only minimally to the placeholder. New web runtime deps are justified here: React, ReactDOM only.

---

# 2. Human Approval

- [x] Strategy reviewed
- [x] Scope correctly understood
- [x] No out-of-scope work detected

Decision:
- [x] Approved
- [ ] Revisions requested
- [ ] Stopped

Notes:
- …

Reviewer: Alberto Galimberti
Date: 2026-10-19

---

# 3. Execution Log (Agent)

### Steps
- Step 1: `server/portal_server/` (`__main__`, `app`, `health`), loopback-only `ThreadingHTTPServer`, `--host` refusal (exit 2), Python < 3.14 check (exit 1), static serving with traversal guard, `/api/health`; 10 unittest tests.
- Step 2: `scripts/check_deps.py` (ast; stdlib + local names; relative imports ok) + tests (fails on third-party, passes on stdlib, `server/` clean).
- Step 3: `web/` Vite/React/TS scaffold, placeholder page showing portal version, Vitest (2 tests), eslint, tsc; `package-lock.json`.
- Step 4: `VERSION` 0.1.0; `scripts/build_bundle.py` (reproducible zip, manifest.json); tests for checksum, layout, server start from extracted bundle. `project.toml [stack]` test/lint extended with dep check, scripts tests, `${PY:-python3}`; `release/` gitignored.
- Step 5: `.github/workflows/ci.yml` (Linux full; macOS/Windows server tests + bundle smoke) and `release.yml` (tag `v*` must equal VERSION; publishes zip + manifest). YAML parses; not run on GitHub.
- Step 6: `server/AGENTS.md`, `web/AGENTS.md` already present and consistent; unchanged.

### Changes (high-level)
- Code: `server/portal_server/`, `web/`, `scripts/`, `VERSION`, `.github/workflows/{ci,release}.yml`, `.gitignore` (+`release/`).
- Interfaces: `GET /api/health`; bundle layout (`VERSION`, `server/`, `web/dist/`); `manifest.json` (version, file, sha256, python_min, contract_built_for).
- Domain: none.
- Tests: `server/tests`, `scripts/tests`, `web/src/App.test.tsx`.
- Specs: none.

---

# 4. Verification

- Build: OK (`npm --prefix web run build`, `scripts/build_bundle.py`)
- Tests: OK (server 10, scripts 6, web 2) with `PY=python3.14 make test`; lint/typecheck OK; dep check OK
- Interfaces / target platforms: OK on macOS (Python 3.14.5, Node 24); Linux/Windows CI and AC7 release not run (need GitHub)
- Manual (if any): OK, bundle server started from extracted zip without Node (covered by test)

Notes:
- AC1, AC3, AC4, AC5, AC6 verified locally; AC2 and AC7 only by workflow review until the first push and tag (the owner triggers the tag).
- `make test` needs `web/dist` built first, otherwise the bundle tests skip.

---

# 5. Tuning Log (If needed)

> Only within scope.

### Entry #1
- Issue:
- Fix:
- Impact:
- Verified: Yes / No

### Entry #2
- …

---

# 6. Deviations

- What changed: `project.toml [stack]` test/lint commands extended (dep check, scripts tests, `PY` override); `.gitignore` +`release/`.
- Why: wire the dependency check and bundle tests into `make test/lint`; allow Python 3.14 selection locally.
- Scope impact: Minor (Spec allows Makefile/stack wiring; no skeleton tool or template touched)

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- Spec §11 completed; AC1, AC3-AC6 checked, AC2 and AC7 marked pending first CI run / tag. `architecture.md` §6/§7 already match the implementation (health shape, bundle layout), no change. `make run` launcher came from the skeleton (merged `a80d295`), not part of this Spec.

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied (AC2, AC7 pending GitHub, see §9)
- [x] Tests passing
- [x] No scope creep
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0101-01 to TSK-AP0101-07

Tasks deferred:
- Verification of AC2 (CI on main) and AC7 (GitHub Release): need a push and the owner's `v0.1.0` tag.

Goal achieved:
- [x] Yes
- [ ] Partial
- [ ] No

Summary:
- Loopback-only stdlib server, placeholder web page, dependency check, bundle + manifest and CI/release workflows delivered; verified locally on macOS (owner checked the running app).

---

# 10. Next Steps

- Follow-ups: push, confirm CI green on Linux/macOS/Windows incl. Python 3.14 on runners; tag `v0.1.0` to verify AC7 (SHA-256 vs manifest).
- Risks: Windows/macOS jobs untested; `make test` skips bundle tests if `web/dist` is not built.
- Improvements: AP0106 launcher consumes the manifest; AP0103 replaces `unknown` versions.

---

# 11. Addendum (Post-Closure Only)

### <Date>
- Note:
- Impact:
