# RUN-AP0110

## References
- Story ID: AP0110
- Spec: SPEC-AP0110
- Started at (datetime): 2026-10-20T16:00
- Completed at (datetime): 2026-10-20T17:00

---

## Status
Closed

---

# 1. Execution Strategy (Agent)

### Required Reads
- [x] Target Spec
- [x] Scoped package `AGENTS.md` files, if applicable:
  - `server/AGENTS.md`, `web/AGENTS.md`: listed by `tools/context.py`; **not read**, no file of this repository's packages is touched (all code lands in agentic-skeleton)
  - agentic-skeleton `AGENTS.md` (root): to read at execution start (TSK-AP0110-01)
- [x] `delivery/templates/RUN-template.md`

### Plan
All code in `../agentic-skeleton` (NFR-14), on a new branch `ap0110-launcher-token` created before the first change. Current `tools/portal.py` (v1.1.1, 377 lines): `serve()` starts the server with `os.environ` + `PYTHONPATH`, writes `run.json`, opens the plain URL; `main()` reuses a running instance via `running_instance()` and opens the plain URL.
- Step 1 (TSK-01): create the skeleton branch; read its `AGENTS.md`, `Makefile`, CI, `tools/tests/test_portal.py` helpers (fake bundle/server, `PortalCase`); log findings.
- Step 2 (TSK-02): add `token_file(root)`, `new_token()` (`secrets.token_urlsafe(32)`), `write_token(root, token)` (create `.portal/` if needed; `os.open(tmp, O_WRONLY|O_CREAT|O_EXCL, 0o600)` then `os.replace`; on Windows `icacls <file> /inheritance:r /grant:r <user>:F`, failure → warning on stderr, launch continues), `read_token(root)` (returns None if missing, empty, or on POSIX mode has group/other bits), `remove_token(root)`.
- Step 3 (TSK-03): `serve()` generates the token, writes the file **before** starting the server, passes `PORTAL_TOKEN` in the child `env` only (overriding any inherited value), prints and opens `<url>/#token=<token>`; the file is removed in `finally` next to `run.json`. `main()` reuse path: `read_token` → open `<url>/#token=…`, else plain URL + restart hint, exit 0. Printed "already running" line stays token-free; the one-time printed URL carries the token (AC6).
- Step 4 (TSK-04): tests for AC1–AC6 in `tools/tests/test_portal.py`, reusing the fake server (extended to record `PORTAL_TOKEN` and `argv`); Windows branch via mocked `os.name`/`subprocess.run`; run the full suite and the skeleton CI command locally.
- Step 5 (TSK-05): document `PORTAL_TOKEN`/`.portal/token`/URL fragment next to the existing `[portal]` docs; commit on the skeleton branch; **tag only after human approval**.

### Assumptions
- The fake server used by AP0106 tests can be extended without changing its contract; `PORTAL_TOKEN` is the only server-side contract (AP0102 AC8).
- Token file name `.portal/token` (Spec §10); one token per fresh start, replaced if stale.
- On reuse the token is not verifiable (health unauthenticated); accepted in the Spec.
- Windows is covered by mocked tests only (NFR-10 manual matrix, as AP0106).

### Risks / Open Questions
- Passing `PORTAL_TOKEN` via `env=` does not hide it from same-user processes that read the child's environment; accepted by ADR-006 option A.
- `icacls` user resolution (`USERDOMAIN\USERNAME` vs `%USERNAME%`): use `os.environ["USERNAME"]` with domain when present; failure only warns.
- Terminal prints the tokenised URL (required: lets the user open a browser manually); scrollback exposure accepted by the ADR.
- Sequencing vs AP0102 (Spec §10): the portal server does not read `PORTAL_TOKEN` until AP0102 ships; this RUN's tests use the fake server, so no dependency.
- Open: PLAN.md placement of AP0110 (owner to confirm).

### Scoped Agent Rules Check
- Applies: No for this repository's packages (`server/`, `web/` untouched); Yes for agentic-skeleton root `AGENTS.md`.
- Files read:
  - `delivery/20-specs/SPEC-AP0110-upstream-launcher-token.md`, `delivery/guide/run.md`, `delivery/templates/RUN-template.md`
  - `agentic-skeleton/tools/portal.py` (`serve`, `main`, run-file helpers) and test names
- Notes:
  - Git: skeleton gets branch `ap0110-launcher-token`; this repository gets `ap0110-upstream-launcher-token` for the delivery artifacts only, created before the first change of the RUN. The working tree here is currently on `ap0102-local-security-baseline` with AP0102 and other uncommitted files: I will not mix them, and will ask before switching branches.

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
- Step 1: skeleton branch `ap0110-launcher-token` created from `main` (v1.1.1); skeleton `AGENTS.md` read; launcher and test helpers inspected.
- Step 2-3: `tools/portal.py`: `token_file/write_token/read_token/remove_token/restrict_windows/launch_url`; `serve()` writes the token file before the server starts, passes `PORTAL_TOKEN` via env, prints and opens `<url>/#token=…`, removes the file in cleanup; reuse path in `main()` reads the token, falls back to the plain URL plus restart hint.
- Step 4: 9 tests in `Token` class (AC1-AC6); fake server health now echoes `PORTAL_TOKEN` and argv.
- Step 5: `tools/README.md` documents the token delivery. Committed on the skeleton branch (not pushed, not tagged).

### Changes (high-level)
- Code: skeleton `tools/portal.py`
- Interfaces: `PORTAL_TOKEN` env, `.portal/token`, launch URL `#token=`, extra `Open <url>` line
- Domain: n/a
- Tests: skeleton `tools/tests/test_portal.py` (+9, 31 total)
- Specs: none

---

# 4. Verification

- Build: OK (`make test-tools`; skeleton CI green: check 3.11/3.14, portal-launcher macOS/Windows)
- Tests: OK, 31 passed (22 existing + 9 new)
- Interfaces / target platforms: OK on macOS; Windows `icacls` path covered by mocked test only (NFR-10 manual matrix)
- Manual (if any): not run

Notes:
- `Started at` was filled after the first code edit instead of before it (recorded here; no scope impact).
- Skeleton branch merged into skeleton `main` and deleted; no tag (owner approval pending).

---

# 5. Tuning Log (If needed)

Owner accepted the implementation (2026-10-20, chat: `/run AP0110 accept`).

### Entry #1
- Issue: skeleton CI `portal-launcher (windows-latest)` hung: two new tests called `communicate()` after `terminate()`, which on Windows is a hard kill, so the orphaned server kept the stdout pipe open.
- Fix: the AC1 test reads stdout up to the `Open` line instead of waiting for EOF; the AC6 test calls `kill_servers()` before `communicate()` (commit `04d384a`). Test code only.
- Impact: none on launcher behaviour.
- Verified: Yes (`make test-tools` 31 OK locally; skeleton CI green on all 4 jobs, run 39456781366).

---

# 6. Deviations

- What changed: launcher prints an extra `Open <url>` line (needed so `--no-browser` users get the tokenised URL).
- Why: ADR-006 requires the URL to be printed once; the existing line stays token-free.
- Scope impact: None

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- Spec §11 and AC ticked; ADR-006 revision line added; Brief closed; Spec index updated. Architecture unchanged.

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied
- [x] Tests passing
- [x] No scope creep
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0110-01 to TSK-AP0110-05 (release tag pending owner approval)

Tasks deferred:
- none

Goal achieved:
- [x] Yes
- [ ] Partial
- [ ] No

Summary:
- Token generation, user-only file, `PORTAL_TOKEN`, `#token=` URL and reuse delivered upstream; 31 launcher tests green.

---

# 10. Next Steps

- Follow-ups: skeleton tag (owner approval); AP0102 consumes `PORTAL_TOKEN`; Windows manual check.
- Risks: reuse cannot verify the token against the server.
- Improvements: none
