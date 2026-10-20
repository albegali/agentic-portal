---
artifact_type: analysis
us_id: STORY_AP0102
title: Local security baseline
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0102_local_security_baseline.md
  - reference/project-summary.md
related_references:
  - reference/product/non-functional-requirements.md#NFR-01
  - reference/product/non-functional-requirements.md#NFR-02
  - reference/product/non-functional-requirements.md#NFR-03
  - reference/architecture/ADR-006-local-security.md
  - reference/architecture/ADR-003-distribution.md
last_updated: 2026-10-20
---

# Analysis AP0102 - Local security baseline

## 1. References

- ID: AP0102
- Source story: analysis/10-stories/STORY_AP0102_local_security_baseline.md
- Roadmap phase: R1 (sprint S1 in PLAN.md)
- Sources used: Story, project summary, NFR-01/02/03, ADR-006, ADR-003 (revisions), Analysis/Refined AP0101, `server/portal_server/app.py`, `tools/portal.py` (launcher released in skeleton 1.1.x)
- Missing sources: architecture.md §6 (API/SSE conventions) and ADR-004/005 not read; web client code not read beyond the existence of `web/src`

## 2. Original User Story

### Story text

As a owner at the machine, I want loopback-only binding, a per-session token, Host/Origin checks and CSRF protection on every API route, so that no other process or web page can read or change my repository through the portal.

### Description

- Epic: EP-01 — Technical foundations
- Priority (MoSCoW): Must · Release: R1 · Size: M · Type: technical
- Requirements: NFR-01, NFR-02, NFR-03
- Depends on: AP0101
- Notes: ADR-006. Token travels URL fragment → sessionStorage → bearer header; gate nonce is handled in EP-04.
- Out of scope: Gate confirm nonce, agent allow-list.

## 3. Intent Understanding

### Functional goal

- Make the local server safe against other web pages (CSRF, DNS rebinding) and unauthenticated local callers, and guarantee that nothing is written outside the repository.

### Actors involved

- Owner using the browser; the launcher (`make portal`); other browser tabs/pages; other local processes.

### Expected outcome

- Every `/api` route requires the session token; state-changing requests also pass Host/Origin checks; write paths are confined to the repository root; loopback-only binding is verified.

## 4. Information Classification

### Facts

- ADR-006 (accepted): bind 127.0.0.1; 256-bit token generated at start, printed once in the launch URL fragment, never in logs or files; kept in `sessionStorage`; `Authorization: Bearer`; Host must be `127.0.0.1:<port>`/`localhost:<port>`; Origin must match on state-changing requests; writes only through skeleton commands with path checks.
- NFR-02: 100% of API routes reject missing/invalid token (automated tests); NFR-01 verified by test + port scan; NFR-03 by path-traversal tests.
- AP0101 (done) already refuses non-loopback `--host`; `/api/health` is served without any token; the request log is suppressed (`log_message` is a no-op).
- Launcher `tools/portal.py` (skeleton 1.1.x, released): chooses the port (8765, else next free) and passes `--port`; probes `/api/health` without credentials, both to wait for startup and to detect a running instance; stores `url`, `pid`, `port` in `.portal/run.json`; opens `http://127.0.0.1:<port>` **without a token fragment**; reuses a running portal by opening the stored URL.
- Out of scope per Story: gate confirm nonce (EP-04), agent allow-list (ADR-004).

### Clarifications received

- None specific to this story. Owner decisions of 2026-10-19 confirm NFR-01..03 as Must.

## 5. Original Acceptance Criteria

- Given the server running, when I scan listeners, then only 127.0.0.1 is bound.
- Given a request without or with a wrong token, when it reaches any /api route, then it is rejected and logged to stderr without the token.
- Given a state-changing request with a foreign Origin or Host, when it reaches the server, then it is rejected.
- Given a write path outside the repo root, including traversal, when a write is attempted, then it is refused and nothing is written.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- **Token never reaches the browser today.** ADR-006 has the server print the URL with `#token=…`, but the released launcher (AP0106) is the process the user runs, opens the browser itself and never sees the token. Interpretation: the launcher must obtain or generate the token and open `…/#token=…`; this is an upstream change not in any story.
- **Reopening / reusing a running portal.** The owner decided (workshop 2026-10-19, AP0106) that a running portal is reused. ADR-006 states the consequence "reopening the browser needs the URL from the terminal" and forbids the token in files, while the launcher reuses an instance through `.portal/run.json`. These cannot both hold.
- **`/api/health` and "every route".** The launcher needs an unauthenticated liveness probe; NFR-02 says 100% of routes reject a missing token. Is health an exception?
- "Rejected" is not specified (status codes, body, whether the page shows "session expired / open from the terminal URL").

### Functional gaps

- AC 3 covers only state-changing requests; a foreign Host on a **GET** (DNS rebinding reads data) is not covered.
- No AC for token handling in the browser (fragment removed from the address bar, new tab without the token, token lost on restart of the portal).
- No AC for the case where NFR-03 applies today: the server has no write route yet, so "when a write is attempted" has nothing to exercise.
- Which paths count as "workflow artifacts and settings" (NFR-03) versus portal private state in `.portal/` (run.json, caches, run logs) is not stated.

### Technical gaps

- Token transport for SSE: `EventSource` cannot send `Authorization`; ADR-006 does not say how streams authenticate (affects the Runs/log stream stories).
- Token comparison, generation (`secrets`), storage in memory only, and redaction in logs are implied but not specified.
- Symlinks, Windows drive letters/case-insensitivity and `..` in path checks (NFR-10).
- Static files (`/`, assets) are not under `/api`; confirm they stay public (the page must load to read the fragment).
- CORS: no `Access-Control-*` headers must ever be emitted; not stated.

### Dependencies or ownership points to clarify

- Depends only on AP0101 per Story, but correct behaviour needs the launcher (upstream, AP0106 already released) and AP0107's bundle start to carry the token: ownership of the launcher change is open.
- AP0104 (contract client) and every API story build on the middleware introduced here; the order inside S1/S2 matters for the "add a test per new route" rule.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions only: an answer from the PO / stakeholder is mandatory.

- [High impact] When a portal is already running and the user runs `make portal` again, should the new invocation open the same session without asking anything (needs the token stored in a gitignored, user-only file in `.portal/`), or may the user be asked to use the URL printed by the first terminal (or get a fresh session by restarting)? — decides whether ADR-006's "token never in files" is amended, and the AP0106 decision "a running portal is reused".
- [High impact] Who owns the upstream launcher change that makes the token reach the browser (launcher generates it or reads it from the server), given the launcher is already released in skeleton 1.1.x? — without it the first real screen cannot authenticate; touches NFR-14 (skeleton changes go upstream).
- [Medium impact] Is an unauthenticated `/api/health` returning only status/versions acceptable as a documented exception to NFR-02 "100% of routes"? — the launcher and reuse detection depend on it.
- [Medium impact] What should the user see when the token is missing or wrong (a clear "open the portal from `make portal`" screen, versus a bare error)? — user-visible behaviour of the first run.
- [Low impact] Is the portal expected to keep working in a second browser tab opened by hand (new tab has no sessionStorage token)? — user-visible limitation.

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Token delivery — **Proposal**: the launcher generates the token (`secrets.token_urlsafe(32)`), passes it to the server in the child environment `PORTAL_TOKEN`, and opens `http://127.0.0.1:<port>/#token=<token>`; if `PORTAL_TOKEN` is unset (server run by hand) the server generates one and prints the full URL once on stdout · **Why**: the launcher already owns port selection and browser opening; the token never goes in a log or a repo file · **Alternatives**: server prints, launcher parses stdout (needs piped output, fragile); token in `.portal/run.json` (violates ADR-006 unless amended) · **Confidence**: medium
- [High impact] Reuse of a running instance — **Proposal**: if the answer to the reuse question is "same session", `run.json` stores the token with file mode 0600 (best effort on Windows), `.portal/` is already gitignored, and ADR-006 is amended with a revision line; otherwise the launcher prints the URL it can no longer reconstruct and offers `--restart` · **Why**: keeps the owner decision to reuse; risk is limited to the same OS user, already outside ADR-006's threat model · **Alternatives**: always restart (drops running agent runs) · **Confidence**: medium
- [High impact] Health exception — **Proposal**: `GET /api/health` stays unauthenticated but Host-checked and returns no repository data; every other `/api/*` route requires the token; the test enumerates routes from the router and fails if a new route is not covered · **Why**: launcher probe; NFR-02 verifiable by construction · **Alternatives**: token on health (launcher would need the token to probe) · **Confidence**: medium
- [Medium impact] Middleware order — **Proposal**: one pipeline for all requests: Host check (all methods) → for `/api`: token (constant-time `hmac.compare_digest`) → for POST/PUT/PATCH/DELETE: Origin must equal `http://<allowed host>:<port>` and a JSON content type; failures return 401/403 with `{"error":{"code","message"}}`; a line to stderr with method, path and reason, never headers or the token; no CORS headers · **Why**: covers DNS rebinding on GET, which AC 3 omits · **Alternatives**: Host check only on writes · **Confidence**: high
- [Medium impact] Write scope — **Proposal**: a single `safe_path(root, candidate)` helper (resolve, reject outside root, reject symlink escape, case-fold on Windows) plus a `write_guard` used by the future store and gate code; this story tests it directly with traversal, absolute, symlink and `..` inputs, and adds a test that the server module has no write call outside the helper (grep-style check) · **Why**: AC 4 has no route to exercise today; NFR-03 is Must · **Alternatives**: defer the test to the first write route (leaves AC 4 untestable now) · **Confidence**: medium
- [Medium impact] Portal private state — **Proposal**: `.portal/` (run.json, caches, logs) is explicitly allowed as portal-owned state and excluded from the "workflow artifacts and settings" rule, but still passes `safe_path` · **Why**: NFR-03 wording would otherwise forbid the launcher/run files · **Alternatives**: amend NFR-03 text (owner approval) · **Confidence**: medium
- [Medium impact] SSE authentication — **Proposal**: streams use `fetch` with a streamed body and the bearer header (no `EventSource`), decided here so run-log stories inherit it · **Why**: keeps one auth mechanism and no token in URLs · **Alternatives**: short-lived single-use stream ticket requested with the bearer · **Confidence**: medium
- [Medium impact] Web client — **Proposal**: a small `api` module reads `#token`, stores it in `sessionStorage`, removes the fragment with `history.replaceState`, adds the bearer header, and on 401 shows a plain "open the portal with `make portal`" message; the visual treatment belongs to AP0108's shell · **Why**: Story notes the browser leg of the flow · **Alternatives**: server-only story, client in a later one · **Confidence**: medium
- [Low impact] Test shape — **Proposal**: unittest starts the server on port 0 and asserts the bound address is 127.0.0.1 (`getsockname()`); no port-scan tool dependency · **Why**: NFR-08 stdlib only · **Confidence**: high

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-20)

See `analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md` and the Refined Story. Owner decisions recorded there change §7 proposals; the rest stands.
