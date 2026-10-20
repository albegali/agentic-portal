# SPEC-AP0102 - Local security baseline

## References
- Story ID: AP0102
- Brief: BRIEF-AP0102
- RUN: RUN-AP0102

---

## Status
Done

---

# 1. Goal

Every `/api` request is accepted only from the loopback interface with a valid session token and a valid Host (and Origin for state-changing calls), and any server write path is confined to the repository root; the web client obtains, stores and sends the token without leaking it.

---

# 2. User / Business Value

As an owner at the machine
I want loopback-only binding, a per-session token, Host/Origin checks and CSRF protection on every API route
So that no other process or web page can read or change my repository through the portal.

---

# 3. Scope

Included:
- Loopback-only bind, verified by a test on port 0 with `getsockname()` (NFR-01).
- Request pipeline order Host → token → Origin/content type, on every `/api` route except `GET /api/health`.
- Token: `Authorization: Bearer`, constant-time compare (`hmac.compare_digest`), JSON error body (401 missing/invalid token, 403 Host/Origin/content type), one stderr line with method, path and reason, never headers or token.
- Host allowed: `127.0.0.1:<port>` and `localhost:<port>`, all methods. State-changing methods (POST, PUT, PATCH, DELETE): Origin must match the allowed hosts and content type must be `application/json`. No CORS headers.
- Token source: `PORTAL_TOKEN` env; if unset the server generates a 256-bit token (`secrets`) and prints the launch URL (`#token=…`) once to stdout. Read of the token file `.portal/` (user-only) for a reused running portal, as a helper consumed by AP0110.
- `safe_path` / `write_guard` helper in `server/portal_server/store/`: resolves against the repo root, refuses traversal, absolute paths, symlink escapes and Windows case-variant escapes; `.portal/` is allowed as portal-owned state (NFR-03).
- Web `api` module: reads `#token` before the router mounts, stores it in `sessionStorage`, clears the fragment (`history.replaceState`), exposes a `fetch` wrapper adding the bearer header (usable for SSE through `fetch`), plain message "open the portal with `make portal`" on 401 or missing token.
- Tests: bind, route enumeration, token/Host/Origin/content-type matrix, log redaction, `safe_path` (traversal, absolute, symlink, case), web token module.
- Docs: document the health exception to NFR-02 in `reference/architecture/architecture.md` if not already stated; update `server/AGENTS.md`/`web/AGENTS.md` only if a rule changes.

Out of scope:
- Launcher token generation, token file writing and opening `/#token=…` (AP0110, upstream).
- Gate confirm nonce, agent allow-list, run-log redaction (EP-04, ADR-004).
- Visual treatment of the 401 message (AP0108 shell).
- Any write route; any skeleton file edit.

---

# 4. Acceptance Criteria

- [x] AC1: Given the server running, when the bound address is inspected (port 0, `getsockname()`), then only 127.0.0.1 is bound.
- [x] AC2: Given a request without or with a wrong token to any `/api` route other than health, when it arrives, then it gets 401 with a JSON error and one stderr line (method, path, reason) that contains no token or header.
- [x] AC3: Given any request (including GET) with a foreign Host, when it arrives, then it is rejected (403) before the token is checked.
- [x] AC4: Given a state-changing request with a foreign Origin or a non-JSON content type, when it arrives with a valid token, then it is rejected (403).
- [x] AC5: Given a write path outside the repo root (traversal, absolute, symlink escape, Windows case variant), when checked by `write_guard`, then it is refused and nothing is written; `.portal/` paths are accepted.
- [x] AC6: Given the router, when the route-enumeration test runs, then every `/api` route except health is covered by the missing/invalid token test (a new route without coverage fails the test).
- [x] AC7: Given a browser opening `/#token=…`, when the page loads, then the token is in `sessionStorage`, removed from the address bar and sent as bearer; with no token a plain message explains how to open the portal.
- [x] AC8: Given `PORTAL_TOKEN` unset, when the server starts, then it generates a token and prints the URL once; given it set, then that value is used and nothing prints it.
- [x] AC9: Given `GET /api/health` with a valid Host and no token, when it arrives, then it succeeds with no repository data; with a foreign Host it is rejected.

---

# 5. Tasks

- `TSK-AP0102-01` Auth/Host/Origin/content-type middleware and JSON error shape in `server/portal_server/http/`, wired into `app.py`, stderr log without secrets.
- `TSK-AP0102-02` Token handling: `PORTAL_TOKEN`, generation and one-time URL print, token-file reader (user-only file check) for reuse.
- `TSK-AP0102-03` `safe_path` / `write_guard` helper with tests (traversal, absolute, symlink, Windows case).
- `TSK-AP0102-04` Server tests: bind on port 0, route enumeration, token/Host/Origin matrix, health exception, log redaction.
- `TSK-AP0102-05` Web `api` token module (fragment read/strip before router mount, `sessionStorage`, bearer fetch wrapper, 401 message) wired in `main.tsx`, with unit tests.
- `TSK-AP0102-06` Docs: health exception noted in architecture; Spec reconciliation inputs for persist.

---

# 6. Execution Boundaries

The agent is allowed to:
- Edit `server/portal_server/`, `server/tests/`, `web/src/api/`, `web/src/main.tsx` and web tests, and the reference docs named in §9.
- Create `.portal/` handling code (reader and `write_guard`) without creating the token file writer.

The agent is not allowed to:
- Edit skeleton or launcher files (`scripts/portal.py`, `wf.py`, …): that is AP0110.
- Add third-party runtime dependencies (NFR-08; web dependency only with reason in the RUN).
- Add routes beyond the existing health route (a test-only route is allowed for enumeration tests).
- Store or log the token anywhere except the user-only `.portal/` file read path, `sessionStorage` and the one-time launch URL.

---

# 7. Quality Gates

- [x] Tests added/updated (`make test`)
- [x] Build passes (`make lint`, web build)
- [x] Public interfaces updated if impacted (API error shape, `PORTAL_TOKEN`, health exception in architecture §)
- [x] Domain invariants respected (ADR-006; NFR-01..03, NFR-08)
- [x] No breaking changes unless explicitly approved
- [x] Windows `icacls`/case behaviour left to CI on Windows (noted, not blocking locally)

---

# 8. Stop Conditions

Stop and ask for supervision if:
- acceptance criteria are ambiguous
- a breaking change is required (e.g. AP0101 health contract or CLI flags)
- security or permission rules are unclear (token file permissions, any deviation from ADR-006)
- a skeleton/launcher change seems necessary (belongs to AP0110)
- work appears out of scope

---

# 9. Impacted Areas

- Code: `server/portal_server/` (`http/`, `store/`, `app.py`), `web/src/api/`, `web/src/main.tsx`
- Interfaces (API, CLI, file formats, protocols, library API): API auth and error shape; env `PORTAL_TOKEN`; launch URL fragment; `.portal/` token file (read only)
- Domain: n/a
- UX: plain 401 / no-token message
- Platforms / distribution: Windows `icacls` and case-insensitive paths
- Tests: `server/tests/`, web unit tests
- Docs: `reference/architecture/architecture.md` (health exception), `server/AGENTS.md` / `web/AGENTS.md` if needed

---

# 10. Notes / Clarifications

- Source of decisions: `analysis/30-refined/REFINED_AP0102_local_security_baseline.md` and workshop 2026-10-20; ADR-006 revision is already recorded.
- Second hand-opened tab has no token and shows the 401 message: accepted.
- End-to-end real launcher → browser depends on AP0110.

---

# 11. Final Reconciliation

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- TSK-01..06 done. Final state: `server/portal_server/http/auth.py` (Host → token → Origin/content type; `PUBLIC_ROUTES` = GET/HEAD `/api/health`), `http/token.py` (`PORTAL_TOKEN` or generated token, URL printed once, `.portal/token` reader that refuses group/other-readable files on POSIX), `store/paths.py` (`safe_path`/`write_guard`), `app.py` (guard on every verb, `API_ROUTES` table used by the route-enumeration test); web `src/api/token.ts` (fragment captured and stripped before the router mounts, `sessionStorage`, `apiFetch` bearer, 401 message in `ServerStatus`).
- Behaviour beyond the Spec wording: a missing `Origin` on a state-changing request is rejected; unknown `/api/*` paths return 401 without a token (404 with one). No deviations.
- Open: end-to-end launcher → browser needs AP0110; Windows `icacls` and case checks run only in Windows CI (`test_windows_case_variant_inside_root_allowed` is skipped on POSIX).
