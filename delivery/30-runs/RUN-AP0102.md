# RUN-AP0102

## References
- Story ID: AP0102
- Spec: SPEC-AP0102
- Started at (datetime): 2026-10-20T18:30
  - Fill only when execution starts after human approval, immediately before the first code or test change.
- Completed at (datetime): 2026-10-20T19:10
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
  - `server/AGENTS.md`
  - `web/AGENTS.md`
- [x] `delivery/templates/RUN-template.md`

### Plan
- Step 0: create branch `ap0102-local-security-baseline` from `main` before the first change; fill `Started at`.
- Step 1 (TSK-02): `server/portal_server/http/token.py` — `resolve_token(env)` (`PORTAL_TOKEN` else `secrets.token_urlsafe(32)`, flag `generated`), `read_token_file(root)` (`.portal/` file, refuses group/other-readable on POSIX), one-time launch URL print in `app.main` only when generated. Tests first.
- Step 2 (TSK-01): `server/portal_server/http/auth.py` — pure `check_request(method, path, headers, port, token)` returning `None` or `(status, code, reason)`, order Host → token → Origin/content type; health exempt from the token only; `hmac.compare_digest`; JSON error body `{"error":{"code","message"}}`; no CORS headers. Wire into `Handler` in `app.py` for every method (add `do_POST/PUT/PATCH/DELETE` so state-changing verbs hit the middleware, 403/401 before 404/405); stderr line `method path reason` only. `create_server` gets a `token` parameter (existing tests keep working by passing one).
- Step 3 (TSK-03): `server/portal_server/store/paths.py` — `safe_path(root, rel)` / `write_guard`: resolve (follows symlinks), `is_relative_to(root.resolve())`, reject absolute and NUL, case-insensitive compare via `os.path.normcase` on Windows; `.portal/` allowed. Tests: traversal, absolute, symlink escape, case variant (skipped off Windows where not applicable).
- Step 4 (TSK-04): extend `server/tests/`: bind on port 0 with `getsockname()` (AC1); route-enumeration test that lists declared routes from a router table in `app.py` (small `ROUTES` registry added for this purpose, health the only exempt entry) and asserts missing/invalid token → 401 for the rest, so a new route without coverage fails; Host/Origin/content-type matrix; health exception; log never contains the token.
- Step 5 (TSK-05): `web/src/api/token.ts` — `captureToken()` reads `#token=…`, stores in `sessionStorage`, `history.replaceState` to strip it, tolerant of storage errors; `apiFetch(path, init)` adds `Authorization: Bearer`, throws/returns a `NoTokenError`/401 state; call `captureToken()` in `main.tsx` before the router mounts; the existing health call uses `apiFetch`; a plain "open the portal with `make portal`" message component text for 401/no token (styling stays AP0108). Vitest for capture/strip/bearer/401 and no token logging.
- Step 6 (TSK-06): note the health exception in `reference/architecture/architecture.md`; touch `server/AGENTS.md` / `web/AGENTS.md` only if a rule changes. Leave Spec §11 and RUN §7–10 to `/persist`.
- After each step run the unit tests of that side; before finishing: `make test`, `make lint`, web build.

### Assumptions
- Spec status is Ready (set by the owner); ADR-006 revision and workshop 2026-10-20 decisions apply and are not re-asked.
- `server/portal_server/http/` and `store/` packages do not exist yet and are created here per `server/AGENTS.md` layout; `health.py` stays where it is.
- The token-file reader only reads; writing it is AP0110. Permission check on Windows is best effort (warning), verified in Windows CI.
- No route exists besides `/api/health`; unknown `/api/*` paths still require the token (401 before 404), so that route existence is not leaked.
- Non-`/api` static paths need no token (the SPA must load before it can send one); Host check still applies to them (DNS rebinding).
- The `ROUTES` registry is an internal helper for enumeration, not a new API surface.

### Risks / Open Questions
- Host check on static assets may break `localhost`/IP access variants: allowed set is `127.0.0.1:<port>` and `localhost:<port>` only, per ADR-006.
- Adding verbs to `BaseHTTPRequestHandler` changes the 501 default for unknown methods to JSON 401/403; judged in scope (NFR-02), no API consumer exists yet.
- Existing AP0101 tests may assume no Host check or no token; they are updated, not weakened, and the change is logged.
- Real launcher → browser flow is untestable until AP0110 (stop condition if a skeleton edit looks necessary).
- Windows `icacls`/case behaviour verified only in CI.

### Scoped Agent Rules Check
- Applies: Yes
- Files read:
  - `server/AGENTS.md`
  - `web/AGENTS.md`
- Notes:
  - Server: stdlib only, every API route through auth + Host/Origin middleware with a test per route, paths resolved under the repo root, never log the token.
  - Web: token read from the launch fragment and stripped before the router mounts, `sessionStorage` only, never logged; no new runtime dependency planned.

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
Date: 2026-10-20

---

# 3. Execution Log (Agent)

### Steps
- Step 0: branch `ap0102-local-security-baseline` created from `main`; `Started at` filled.
- Step 1 (TSK-02): `http/token.py` — `resolve_token`, `read_token_file` (refuses group/other-readable on POSIX), `launch_url`, constant-time compare; `app.main` prints the launch URL once only when the token was generated.
- Step 2 (TSK-01): `http/auth.py` — `check_request` (Host → token → Origin/content type), `PUBLIC_ROUTES` = GET/HEAD health; `app.py` guard on every verb (`do_POST/PUT/PATCH/DELETE/OPTIONS`), `API_ROUTES` table, JSON error body, stderr line `method path reason`, no CORS headers.
- Step 3 (TSK-03): `store/paths.py` — `safe_path` / `write_guard` (traversal, absolute incl. drive letters, NUL/empty, symlink, `normcase` compare, sibling-prefix).
- Step 4 (TSK-04): `server/tests/test_security.py` (bind, token matrix, route enumeration, Host/Origin/content type, health exception, log redaction, token source, token file, safe_path); `test_server.py` updated to pass a token (unknown `/api` path now 401 without token, 404 with).
- Step 5 (TSK-05): `web/src/api/token.ts` (capture/strip fragment, `sessionStorage`, `apiFetch` bearer, `UnauthorizedError`), called in `main.tsx` before the router mounts; `ServerStatus` uses `apiFetch` and shows the plain "open with `make portal`" alert when no token; unit tests added.
- Step 6 (TSK-06): `architecture.md` §5 notes pipeline order and the health exception; package `AGENTS.md` files unchanged (no rule changed).

### Changes (high-level)
- Code: `server/portal_server/{app.py,http/,store/}`, `web/src/{main.tsx,api/,components/Shell/ServerStatus.tsx}`
- Interfaces: API auth and error shape (`{"error":{"code","message"}}`, 401/403); `PORTAL_TOKEN`; launch URL printed once when generated
- Domain: n/a
- Tests: `server/tests/test_security.py` (new), `test_server.py` (token), `web/src/api/token.test.ts`, `ServerStatus.test.tsx`
- Specs: none

---

# 4. Verification

- Build: OK (`vite build`, `make lint`)
- Tests: OK (`PY=python3.14 make test`: 34 server tests, 1 skipped on POSIX — Windows case; 77 web tests; `npm run e2e` 111 passed)
- Interfaces / target platforms: OK on macOS; Windows `icacls` and case-variant paths left to Windows CI
- Manual (if any): not run (end-to-end launcher → browser depends on AP0110)

Notes:
- Default `python3` here is 3.12; the project needs 3.14, so `PY=python3.14` was used.
- Origin is required (not just matched) on state-changing requests: a missing Origin is rejected.

If FAIL → move to Tuning.

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

- What changed:
- Why:
- Scope impact: None / Minor / Requires approval

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- SPEC-AP0102 §11 and status Done; Brief closed; index updated. Reference docs touched by the story: `reference/architecture/architecture.md` §5 (pipeline order, health exception). No ADR change (ADR-006 revision was already recorded). Package `AGENTS.md` files unchanged.

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied (AC1-AC9)
- [x] Tests passing
- [x] No scope creep
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0102-01 … TSK-AP0102-06

Tasks deferred:
- None

Goal achieved:
- [x] Yes
- [ ] Partial
- [ ] No

Summary:
- Every `/api` route requires the session token and a valid Host (plus Origin and JSON content type when state-changing), health being the one documented exception; write paths are confined to the repo root; the web client captures, stores and sends the token without leaking it.

---

# 10. Next Steps

- Follow-ups: AP0110 (launcher delivers the token and writes `.portal/token`, placement in the plan is a PO decision); first Windows CI run for the `icacls`/case checks; later route stories must add their routes to `API_ROUTES`.
- Risks: reopening a second tab by hand shows the no-token message (accepted).
- Improvements: none.

---

# 11. Addendum (Post-Closure Only)

### <Date>
- Note:
- Impact:
