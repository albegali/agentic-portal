# SPEC-AP0106 - Upstream: portal.py launcher and make portal

## References
- Story ID: AP0106
- Brief: BRIEF-AP0106
- RUN: RUN-AP0106

---

## Status
Done

---

# 1. Goal

In the agentic-skeleton repository: `tools/portal.py` (stdlib) and a `make portal` target that download the pinned portal bundle, verify its SHA-256, cache it in `.portal/<version>/`, start it for the current repo, and open the browser.

---

# 2. User / Business Value

As a portal (consumer of agentic-skeleton)
I want a launcher in the skeleton that fetches, verifies and starts the pinned bundle
So that every workflow repository, greenfield or adopted, starts the portal with one command and no Node.

---

# 3. Scope

Included:
- Config: read `[portal] version` (and optional `[portal] source` = `<owner>/<repo>`, default this repository) from the nearest `project.toml`; that directory is the repo root.
- Download `https://github.com/<owner>/<repo>/releases/download/v<version>/manifest.json`, then the asset it names, to a temp file; verify size and SHA-256 against the manifest (checksum only, no signing). Manifest format in §10.
- Safe atomic cache: extract to `.portal/<version>.tmp` rejecting absolute and `..` paths, then rename to `.portal/<version>/`; an existing cache is reused with no network.
- Interpreter for the bundle: the current one if it satisfies the manifest `requires_python`, else `python3.<minor>` on PATH (Windows: `py -3.<minor>`), else exit 1 stating the requirement.
- Start the bundled server with `--repo <root> --port <port>`, print the URL, open the browser automatically, stop on Ctrl+C.
- Port: 8765 (architecture default), else first free port above it.
- Running-instance detection (§10): launcher-owned `.portal/run.json`, verified by a probe of `/api/health`; if alive, open it instead of starting another; if stale, remove it and start.
- `PORTAL_BUNDLE=<path>`: no download; verify the checksum if a manifest is present.
- Failure paths with exit codes 0 ok, 1 user/config error, 2 integrity error.
- Python requirement check: the launcher runs on the skeleton baseline (>= 3.11, AP0103) with syntax compatible with older Python so the requirement message is reachable.
- `make portal` target; `python tools/portal.py` equivalent on Windows without make.
- Tests (stdlib `unittest`) for each AC with a local fake bundle/server; run in skeleton CI on the OS matrix available there.

Out of scope:
- Bundle build and release pipeline (AP0101); signed releases; contract-mismatch check at launch; automatic cleanup of old caches.
- `.portal/` in `.gitignore` via `make adopt` (follow-up in ADR-003, not this story unless trivial and approved).
- Portal-side changes in this repository other than delivery artifacts and reconciliation in persistence.

---

# 4. Acceptance Criteria

- [x] AC1: Given `[portal] version` set, when I run `make portal`, then the bundle is downloaded, SHA-256 verified, cached in `.portal/<version>/`, started with `--repo <root>`, and the browser opens.
- [x] AC2: Given a tampered download, when the checksum is compared, then launch aborts with a message, exit code 2, and no cache is left behind.
- [x] AC3: Given Windows without make, when I run `python tools/portal.py`, then the same happens. *(Same code path, no make involved; not run on Windows: manual NFR-10 matrix, owner accepted 2026-10-20.)*
- [x] AC4: Given Python older than 3.11, when the launcher runs, then it stops and states the requirement; given no interpreter satisfying the manifest `requires_python`, then it states that requirement and exits 1. *(< 3.11 covered by a guard-order test; no older interpreter available.)*
- [x] AC5: Given no network and no cache, when I run the launcher, then it prints a message and exits 1; with a cache it starts from the cache.
- [x] AC6: Given a missing `[portal] version` or a version not found, when I run the launcher, then it prints how to fix it and exits 1.
- [x] AC7: Given `PORTAL_BUNDLE=<path>`, when I run the launcher, then nothing is downloaded and the checksum is verified if a manifest is present.
- [x] AC8: Given a portal already running for the repo, when I run `make portal`, then the running one is opened and no second one starts; given a stale `.portal/run.json`, then it is removed and a new portal starts.
- [x] AC9: Given an archive with absolute or `..` paths, when extracted, then launch aborts (exit 2) and nothing is written outside `.portal/`.

---

# 5. Tasks

- `TSK-AP0106-01` Inspect agentic-skeleton (tools, Makefile, tests, CI, Python baseline, `project.toml` parsing); log findings in the RUN.
- `TSK-AP0106-02` Launcher core: Python check, config and repo-root resolution, exit-code scheme.
- `TSK-AP0106-03` Manifest parsing, download, size and SHA-256 verification, `PORTAL_BUNDLE` override.
- `TSK-AP0106-04` Safe atomic extraction and cache reuse.
- `TSK-AP0106-05` Interpreter selection, port selection, server start, `run.json` + health-probe detection, browser opening, Ctrl+C cleanup.
- `TSK-AP0106-06` `make portal` target and Windows invocation docs.
- `TSK-AP0106-07` Tests for AC1-AC9 and CI wiring.
- `TSK-AP0106-08` Skeleton docs for the `[portal]` settings and the manifest format; release tagging only after human review.

---

# 6. Execution Boundaries

The agent is allowed to:
- Change the agentic-skeleton repository (branch, commits) within the scope above.
- Write delivery artifacts here.

The agent is not allowed to:
- Modify skeleton files from this repository, or add a runtime dependency (stdlib only).
- Build the bundle or the release pipeline, add signing, or add launch-time contract checks.
- Push a tag or release without human review and approval.
- Change ADR-003 or the architecture without owner approval.

---

# 7. Quality Gates

- [x] Tests added/updated (every AC covered)
- [x] Build passes (skeleton CI green)
- [x] Public interfaces updated (`make portal`, `tools/portal.py` CLI, env var `PORTAL_BUNDLE`, `[portal]` keys, exit codes)
- [x] Domain invariants respected (no partial cache visible; checksum always verified when a manifest is available)
- [x] No breaking changes to existing skeleton commands

---

# 8. Stop Conditions

Stop and ask for supervision if:
- the manifest format of §10 cannot be produced by the release pipeline as defined
- the detection of §10 proves unreliable on one OS and needs a server-side change
- ADR-003 (GitHub Releases) is revised
- security or permission rules are unclear (extraction, network)
- acceptance criteria are ambiguous or work appears out of scope

---

# 9. Impacted Areas

- Code: agentic-skeleton `tools/portal.py`, `Makefile`
- Interfaces: `make portal`, `python tools/portal.py`, `PORTAL_BUNDLE`, `[portal] version|source`, exit codes
- Domain: n/a
- UX: terminal messages, browser opening
- Platforms / distribution: macOS, Windows, Linux (NFR-10); skeleton release consumed via the portal's pin
- Tests: skeleton launcher tests and CI
- Docs: skeleton docs for `[portal]`; ADR-003 reconciled in persistence if needed

---

# 10. Notes / Clarifications

- Owner decisions 2026-10-20 (chat): detection and manifest format left to the developer (fixed below); launcher Python baseline stays >= 3.11 (AP0103); distribution stays on GitHub Releases (ADR-003 unchanged).
- Manifest: one release asset `manifest.json`, stdlib-parsable, also kept as `.portal/<version>/manifest.json`:
  `{"manifest": 1, "version": "x.y.z", "asset": "agentic-portal-x.y.z.zip", "size": <bytes>, "sha256": "<hex>", "requires_python": ">=3.14"}`.
  Unknown keys are ignored; `manifest` major other than 1 → exit 2. The launcher learns the asset name and Python requirement from it, so neither is hardcoded. `PORTAL_BUNDLE` points to a zip or a directory; a sibling/contained `manifest.json` triggers verification.
- Detection: after the server prints its listening line the launcher writes `.portal/run.json` `{"pid", "port", "url", "version", "started_at"}` (atomic write) and removes it on exit. On launch, if the file exists the launcher GETs `<url>/api/health` (timeout ~0.5 s, `status: ok`): alive → open browser, exit 0; otherwise stale → delete and start. Repo-scoped because `.portal/` lives in the repo root; no PID inspection (portable on all three OS); one local HTTP call, no scan.
- Dependency on this repository: the server today accepts `--host/--port` but not `--repo`. Adding `--repo` (portal side) is outside this Spec; until it lands, the launcher starts the server with the repo root as working directory and passes `--repo` only when the bundle supports it (decided in the RUN, logged).
- End-to-end verification against a real release depends on the AP0101 pipeline; until then tests use a local fake release and `PORTAL_BUNDLE`. First-release sequence (chicken-and-egg) to be set in the plan.
- Tag/release of the skeleton follows the AP0103 pattern: human approval first.

---

# 11. Final Reconciliation

To be completed before marking Done.

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- Released in agentic-skeleton v1.1.0: `tools/portal.py` + `make portal` as in §3 and §10; `[portal] version|source`, `PORTAL_BUNDLE`, `manifest.json` format 1, exit codes 0/1/2, `.portal/run.json` detection. 22 launcher tests (AC1-AC9) with a fake release.
- Launcher also handles SIGTERM like Ctrl+C (cleanup of the server and `run.json`).
- Reconciled: ADR-003 (Revisions), architecture §7.
- Open: real `--repo` support in the portal server; `.portal/` in `.gitignore` via `make adopt`; Windows/Linux manual check; end-to-end on the first real release (AP0101 pipeline).
