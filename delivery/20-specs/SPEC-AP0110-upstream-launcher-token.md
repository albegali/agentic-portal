# SPEC-AP0110 - Upstream: launcher delivers the session token

## References
- Story ID: AP0110
- Brief: BRIEF-AP0110
- RUN: RUN-AP0110

---

## Status
Done

---

# 1. Goal

In the agentic-skeleton repository, `tools/portal.py` generates the per-session token, stores it in a user-only file in `.portal/`, passes it to the server as `PORTAL_TOKEN`, and opens the browser at `<url>/#token=<token>`, also when it reuses a running portal.

---

# 2. User / Business Value

As a portal (consumer of agentic-skeleton)
I want the launcher to own the session token and deliver it to the browser
So that the browser authenticates on first open and a reused running portal opens the same session.

---

# 3. Scope

Included:
- Token: 256 bits from `secrets` (`secrets.token_urlsafe(32)`), generated on each fresh server start.
- Token file `.portal/token` (decision, §10): written atomically with mode 0600 from creation (`os.open` with `0o600`, then rename); removed on exit together with `run.json`; a stale file is overwritten on the next start.
- Windows: restrict the file to the current user with `icacls` (remove inheritance, grant current user only); on failure print a warning and continue (best effort, ADR-006 revision).
- The server is started with `PORTAL_TOKEN=<token>` in its environment only (never as argument, so it is not visible in the process list).
- Browser URL: `<url>/#token=<token>`; the terminal prints the same URL once.
- Reuse (AP0106 detection alive): read the token from `.portal/token`, open `<url>/#token=<token>`; if the file is missing or unreadable, open the plain URL and print how to restart (`stop the running portal and run make portal again`), exit 0.
- Refuse to read a token file that other users can access on POSIX (mode check) and treat it as missing.
- `.portal/run.json` does not contain the token.
- Tests (stdlib `unittest`) for each AC with the local fake bundle/server of AP0106.
- Skeleton docs: token delivery and file in the `[portal]` documentation.

Out of scope:
- Server-side token validation, Host/Origin checks, web client fragment handling (AP0102).
- Bundle build and release pipeline (AP0107); encryption or keyrings (NFR-08); token rotation during a session.
- `.portal/` in `.gitignore` via `make adopt` unless trivial and approved (as AP0106).

---

# 4. Acceptance Criteria

- [x] AC1: Given `make portal` starting a portal, when the browser opens, then the URL carries the token in the fragment and the server receives the same value as `PORTAL_TOKEN` (and not as a command-line argument).
- [x] AC2: Given the token file in `.portal/`, when I inspect its permissions, then only the current user can read it (0600 on POSIX; `icacls` on Windows, a warning if it fails and the launch still proceeds).
- [x] AC3: Given a portal already running for the repo, when I run `make portal` again, then the running one opens with the same token read from the file and no second server starts.
- [x] AC4: Given a running portal whose token file is missing, unreadable or group/world accessible, when I run `make portal`, then the plain URL opens, a message explains how to restart, and the exit code is 0.
- [x] AC5: Given the launcher exits (Ctrl+C or SIGTERM), when it cleans up, then `.portal/token` and `run.json` are removed; given a stale token file at start, then it is replaced by a new token.
- [x] AC6: Given launcher output, logs and `run.json`, when inspected, then the token appears only in the one-time printed URL and the token file.

---

# 5. Tasks

- `TSK-AP0110-01` Inspect the agentic-skeleton launcher and tests after AP0106 (v1.1.0); log findings in the RUN.
- `TSK-AP0110-02` Token generation and secure file writer/reader (POSIX 0600 and mode check, Windows `icacls` best effort, atomic write, cleanup).
- `TSK-AP0110-03` Pass `PORTAL_TOKEN` to the server environment; build the `#token=` URL for fresh start and reuse; fallback path (AC4).
- `TSK-AP0110-04` Tests for AC1-AC6 (Windows branch with `icacls` mocked) and CI wiring.
- `TSK-AP0110-05` Skeleton docs; release tag (minor) only after human review.

---

# 6. Execution Boundaries

The agent is allowed to:
- Change the agentic-skeleton repository (branch, commits) within the scope above.
- Write delivery artifacts here.

The agent is not allowed to:
- Modify skeleton files from this repository, or add a runtime dependency (stdlib only).
- Change server code or the web client in this repository (AP0102).
- Put the token in arguments, logs, `run.json` or any file other than the token file.
- Push a tag or release without human review and approval.
- Change ADR-006 or the architecture without owner approval.

---

# 7. Quality Gates

- [x] Tests added/updated (every AC covered)
- [x] Build passes (skeleton CI green)
- [x] Public interfaces updated (launch URL fragment, `PORTAL_TOKEN`, `.portal/token`)
- [x] Domain invariants respected (token file never readable by other users)
- [x] No breaking changes to AP0106 behaviour (exit codes, `run.json` fields, `PORTAL_BUNDLE`)

---

# 8. Stop Conditions

Stop and ask for supervision if:
- file permissions cannot be restricted reliably on a platform beyond a warning
- ADR-006 or ADR-003 would need changes
- the AP0102 server contract (`PORTAL_TOKEN`, `#token=`) differs from this Spec
- acceptance criteria are ambiguous or work appears out of scope

---

# 9. Impacted Areas

- Code: agentic-skeleton `tools/portal.py`
- Interfaces: `PORTAL_TOKEN` env, launch URL fragment, `.portal/token`
- Domain: n/a
- UX: terminal messages, browser URL
- Platforms / distribution: macOS, Windows, Linux (NFR-10); skeleton release consumed via the portal's pin
- Tests: skeleton launcher tests
- Docs: skeleton `[portal]` docs; ADR-006 reconciled in persistence if needed

---

# 10. Notes / Clarifications

- Decision: token file name `.portal/token` (plain text, token only, no newline requirement on read: stripped). AP0102 consumes only `PORTAL_TOKEN`; the file reader for reuse lives in the launcher, not in the server.
- Reuse path cannot verify the token against the server (health is unauthenticated); a stale file after a crash is replaced at next start, and AC4 covers an unusable file.
- Release placement: S1 in PLAN.md lists AP0110 after AP0102; AP0102 execution needs this launcher for end-to-end, so execute AP0110 first or in parallel (owner to confirm).
- Tag of the skeleton follows the AP0103/AP0106 pattern: human approval first.

---

# 11. Final Reconciliation

To be completed before marking Done.

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- Delivered in agentic-skeleton (branch `ap0110-launcher-token`): `tools/portal.py` generates the token, writes `.portal/token` (0600; `icacls` on Windows), passes `PORTAL_TOKEN` by environment, prints and opens `<url>/#token=…`, reuses the token of a running portal, removes the file on exit. 9 new tests (31 total); docs in `tools/README.md`.
- The launcher also prints an `Open <url>` line (token included) at start and on reuse; plain URL plus restart hint when the file is unusable.
- Windows `icacls` covered by mocked tests only (NFR-10 manual matrix). End-to-end with the real server depends on AP0102 reading `PORTAL_TOKEN`.
- Release tag pending owner approval.
