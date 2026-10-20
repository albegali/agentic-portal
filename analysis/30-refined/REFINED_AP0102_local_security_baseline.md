---
artifact_type: refined
us_id: STORY_AP0102
title: Local security baseline
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0102_local_security_baseline.md
  - analysis/20-analysis/ANALYSIS_AP0102_local_security_baseline.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md
related_references:
  - reference/architecture/ADR-006-local-security.md
  - reference/product/non-functional-requirements.md#NFR-01
  - reference/product/non-functional-requirements.md#NFR-02
  - reference/product/non-functional-requirements.md#NFR-03
last_updated: 2026-10-20
---

# Refined Story AP0102 - Local security baseline

## 1. References

- ID: AP0102
- Title: Local security baseline
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, ADRs listed above
- Missing sources: architecture.md §6, ADR-004/005, web client code
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md

## 2. Refined User Story

### Refined story text

As an owner at the machine, I want loopback-only binding, a per-session token, Host/Origin checks and CSRF protection on every API route, so that no other process or web page can read or change my repository through the portal.

### Refined description

Server and web-client side of the security model. The token is generated and delivered by the upstream launcher (AP0110) and kept in a user-only file in `.portal/`.

## 3. Scope

### In scope

- Loopback-only bind (verified by test on port 0).
- Token required on every `/api` route except `/api/health`; constant-time compare; 401/403 JSON error; stderr log line with method, path, reason, never headers or token.
- Host check on all methods; Origin and JSON content type on state-changing methods; no CORS headers.
- `safe_path` / `write_guard` helper with traversal, absolute, symlink and Windows case tests; `.portal/` allowed as portal-owned state.
- Web `api` module: reads `#token`, stores in `sessionStorage`, clears the fragment, sends the bearer header, plain "open the portal with `make portal`" message on 401.
- Server reads `PORTAL_TOKEN`; if unset it generates a token and prints the URL once.

### Out of scope

- Launcher token delivery and token file writing (AP0110, upstream).
- Gate confirm nonce, agent allow-list.
- Visual treatment of the 401 message (AP0108 shell).

## 4. Confirmed Information

### Facts

- ADR-006 (revised 2026-10-20), NFR-01..03; AP0101 refuses non-loopback `--host` and suppresses request logs.
- Released launcher (skeleton 1.1.x) does not deliver the token today.
- NFR-08: stdlib only, so no keyring or crypto library.

### Decisions confirmed during refinement

- Token may be stored in a file if protected from other users and applications; chosen: gitignored `.portal/` file, 0600 on POSIX, `icacls` restricted to the current user on Windows (best effort, warning on failure). Encrypting with a co-located key adds nothing. Spec decides details; deviation needs owner approval.
- Launcher generates the token, passes `PORTAL_TOKEN`, opens `/#token=…`; reuse of a running portal reads the token from the file. Owner: fix upstream now (AP0110).
- `/api/health` unauthenticated, documented exception to NFR-02; a route-enumeration test covers every other `/api` route.
- Not overridden, therefore standing (proposal accepted by default): middleware order Host → token → Origin/content type; write scope helper; `.portal/` private state; SSE via `fetch` with bearer header (no `EventSource`); web client token module; `unittest` bind test with `getsockname()`.

### Residual assumptions

- A second hand-opened tab has no token (sessionStorage) and shows the 401 message; accepted limitation.

## 5. Confirmed Acceptance Criteria

- Given the server running, when I inspect the bound address, then only 127.0.0.1 is bound.
- Given a request without or with a wrong token to any `/api` route other than health, when it arrives, then it is rejected (401) and logged to stderr without the token.
- Given any request with a foreign Host (including GET), when it arrives, then it is rejected.
- Given a state-changing request with a foreign Origin, when it arrives, then it is rejected.
- Given a write path outside the repo root (traversal, absolute, symlink escape), when checked by the write guard, then it is refused and nothing is written.
- Given the router, when the route-enumeration test runs, then every `/api` route except health is covered by the missing/invalid token test.
- Given a browser opening `/#token=…`, when the page loads, then the token is kept in `sessionStorage`, removed from the address bar and sent as a bearer header; with no token a plain message explains how to open the portal.

## 6. Remaining Open Points

### Functional

- None blocking.

### Technical

- End-to-end (real launcher → browser) depends on AP0110, which is not in the plan yet: placement in S1/S2 is a PO decision (PLAN.md).
- Windows `icacls` behaviour is verified in CI on Windows.

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Auth/Host/Origin middleware and error shape; `safe_path`/`write_guard`; `PORTAL_TOKEN` handling; token-file read for reuse (consumed with AP0110); web `api` token module; tests (route enumeration, bind, traversal).

### Boundaries to respect

- Stdlib only; no write route exists yet; no skeleton file edited here (launcher change is AP0110).
- ADR-006 revision is already recorded; do not re-ask for it.

## 8. Refinement Outcome

- Story ready with residual open points to track
