# RUN-AP0106

## References
- Story ID: AP0106
- Spec: SPEC-AP0106
- Started at (datetime): 2026-10-20T12:00
  - Fill only when execution starts after human approval, immediately before the first code or test change.
- Completed at (datetime): 2026-10-20T16:00
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
  - none apply: the work is in `../agentic-skeleton` (root `AGENTS.md`; no `tools/AGENTS.md`). `server/AGENTS.md` and `web/AGENTS.md` are not touched.
- [x] `delivery/templates/RUN-template.md`

### Findings from the skeleton (TSK-AP0106-01, read-only, `../agentic-skeleton`, branch `main`, clean)
- `tools/launch.py` (`make run`) already does start + wait-for-URL + `webbrowser` + Ctrl+C; style reference (argparse, stdlib, `tomllib`). `tools/VERSION` = 1.0.0; `wf.py` has `skeleton_version()` and `dump_envelope`.
- Makefile: `PY ?= python3`, targets documented with `##`; `test-tools` = `unittest discover -s tools/tests`. CI matrix Python 3.11 and 3.14 (single workflow, ubuntu only today).
- `tomllib` needs 3.11, so the launcher's own baseline is 3.11 (matches the AP0103 decision); a < 3.11 interpreter cannot read TOML, so the version guard goes first and the module avoids 3.11+-only syntax at import time.
- `.gitignore` of the skeleton has no `.portal/`; no `[portal]` section in `project.toml` yet.
- Portal `server/portal_server/app.py` today: `--host`, `--port` (default 8765), `GET /api/health` → `{"status": "ok", ...}`; no `--repo` yet.

### Plan
- Step 1 (TSK-02): branch `ap0106-portal-launcher` in the skeleton. `tools/portal.py`: first lines check `sys.version_info >= (3, 11)` (message + exit 1), then imports; repo-root resolution (walk up to `project.toml`; error exit 1 if none); `[portal]` parse (`version`, `source` default from the skeleton's configured portal repo); exit codes 0/1/2 via a small `LauncherError(code, message)`. Verify: unit tests for each error path.
- Step 2 (TSK-03): manifest fetch + parse (format of Spec §10), asset download to a temp file with size and SHA-256 check (streamed, `hashlib`); `PORTAL_BUNDLE` (zip or directory; verify when `manifest.json` is present, else warn "unverified"). All network via `urllib` with a base-URL seam (`PORTAL_RELEASE_BASE`, test/mirror use only, undocumented as a user setting) so tests use a local `http.server`. Verify: tamper, size mismatch, 404, offline cases.
- Step 3 (TSK-04): extraction with `zipfile` into `.portal/<version>.tmp`: reject absolute, drive-letter, `..` and symlink entries (checked per member before writing), then atomic `os.replace` to `.portal/<version>/`; remove `.tmp` on any failure; cache hit = directory with `manifest.json`, no network. Verify: zip-slip archive, interrupted extract leaves no cache.
- Step 4 (TSK-05): interpreter choice from manifest `requires_python` (current → `python3.<minor>` → `py -3.<minor>` on Windows → exit 1 with the requirement); port 8765 else next free; start the bundled `portal_server` (`python -m portal_server --host 127.0.0.1 --port N`, cwd = bundle dir) with `--repo <root>` when the bundle supports it (probe `--help`, logged; fallback documented); wait for `/api/health` (timeout 15 s); write `.portal/run.json` atomically; open browser (`--no-browser` flag like `launch.py`); Ctrl+C → terminate child, remove `run.json`. Detection at start: read `run.json`, probe `<url>/api/health` (0.5 s); alive → open + exit 0; stale → delete and continue. Verify: fake server tests (alive, stale, port taken).
- Step 5 (TSK-06): Makefile target `portal` (`@$(PY) tools/portal.py`); `tools/README.md` section: `[portal] version|source`, `PORTAL_BUNDLE`, exit codes, Windows `python tools/portal.py`, manifest format. Commented `[portal]` block in `project.toml`.
- Step 6 (TSK-07): `tools/tests/test_portal.py` (stdlib `unittest`, fake release served locally, fake bundle with a tiny `portal_server` that serves `/api/health`), covering AC1-AC9; green on 3.11 and 3.14 locally if both are installed, otherwise CI; CI already runs `make test-tools`. Add a macOS/Windows job only if cheap (decision logged; otherwise NFR-10 per-OS check stays manual).
- Step 7 (TSK-08): update `tools/README.md`; commit on the branch; **no tag, no push** without human approval. In this repo only RUN/Spec/README reconciliation (via `/persist`).

### Assumptions
- `[portal] source` holds `<owner>/<repo>`; default owner/repo is the portal repository, set when the first release exists (placeholder constant until then, logged).
- Bundle layout: zip root contains `portal_server/` (package) and `web/dist/` plus `manifest.json` copy optional; confirmed against AP0101 at the first real release, tests use the layout above.
- Browser opening via `webbrowser.open`; failure to open prints the URL and is not an error.
- The server binds `127.0.0.1` only.

### Risks / Open Questions
- Server `--repo` not available yet (portal-side, outside this Spec): handled with a capability probe + cwd fallback; the first release must add it, otherwise the portal would not see the repo. Flag to the owner as a follow-up for AP0101/AP0108 sequencing.
- `.portal/` is not ignored in adopted repos (follow-up in ADR-003): the launcher prints a one-line warning if `.portal/` is not in `.gitignore`; skeleton's own `.gitignore` is not changed unless approved (small, proposed as a deviation).
- Windows process termination and `py` launcher behaviour tested only via CI/manual; no Windows runner here (NFR-10 manual matrix).
- Chicken-and-egg first release (skeleton launcher ↔ portal bundle): end-to-end check deferred until the AP0101 pipeline publishes a release.

### Scoped Agent Rules Check
- Applies: No
- Files read:
  - root `AGENTS.md`, `delivery/guide/run.md`
- Notes:
  - Code changes land in `../agentic-skeleton` only (NFR-14 is respected from this repository's side: no skeleton file modified here).

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
- Steps 1-5 (TSK-AP0106-02..06): `../agentic-skeleton` branch `ap0106-portal-launcher`: `tools/portal.py` (guard, root/config, manifest, download, SHA-256/size, `PORTAL_BUNDLE`, safe atomic extract, interpreter/port choice, `--repo` capability probe, `run.json` + health probe, browser, Ctrl+C/SIGTERM cleanup), Makefile `portal`.
- Step 6 (TSK-07): `tools/tests/test_portal.py`, 22 tests (fake release over local HTTP, fake bundle server).
- Step 7 (TSK-08): `tools/README.md` "Portal launcher" section (settings, flow, manifest, exit codes), commented `[portal]` block in `project.toml`. One commit on the branch; no tag, no push.
- Found while testing: a SIGTERM to the launcher skipped cleanup (orphaned server, stale `run.json`); fixed in the launcher (SIGTERM/SIGBREAK handled like Ctrl+C). Test-only: `127.0.0.1:8765` is taken on the developer machine, so port tests use their own base port.

### Changes (high-level)
- Code: skeleton `tools/portal.py`, `Makefile`.
- Interfaces: `make portal`, `python tools/portal.py [--no-browser]`, `PORTAL_BUNDLE`, `[portal] version|source`, `manifest.json` format 1, exit codes 0/1/2, `.portal/run.json`. (`PORTAL_RELEASE_BASE` is an undocumented test/mirror seam.)
- Domain: n/a
- Tests: `tools/tests/test_portal.py` (AC1-AC9).
- Specs: none changed yet (reconciliation in persistence).

---

# 4. Verification

- Build: OK (`make check`)
- Tests: OK (`make test-tools`: 51 tests incl. 22 new, Python 3.12; portal tests also OK on 3.13 and 3.14)
- Interfaces / target platforms: macOS only locally; Windows (AC3) and Linux rely on skeleton CI / manual matrix: NOT verified here. CI matrix is ubuntu 3.11 + 3.14.
- Manual (if any): not done. AC4 (Python < 3.11) is covered by a source-order test only (no older interpreter here). End-to-end against a real release pending the AP0101 pipeline.

Notes:
- `--repo` is exercised against the fake bundle only; the real server does not accept it yet (portal-side follow-up).

---

# 5. Tuning Log (If needed)

> Only within scope.

None: result accepted by the owner on 2026-10-20 without tuning.

---

# 6. Deviations

- What changed: skeleton version bumped to 1.1.0 (`tools/VERSION`) and tagged `v1.1.0` on merge to `main` (TSK-AP0106-08); SIGTERM handled like Ctrl+C.
- Why: a release tag needs a version; cleanup on termination was missing (found in tests).
- Scope impact: None (tag and push approved by the owner 2026-10-20).

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- SPEC-AP0106 §4, §7, §11 → Done. ADR-003 Revisions (manifest format, detection, Python baseline, v1.1.0); architecture §7 (release manifest, launcher behaviour, Python prerequisites).

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied (AC3 Windows and AC4 < 3.11 by test design, manual check pending)
- [x] Tests passing (`make test-tools` 51/51 on skeleton main, 1.1.0)
- [x] No scope creep
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0106-01 … TSK-AP0106-08

Tasks deferred:
- none (end-to-end against a real release waits for the AP0101 release pipeline)

Goal achieved:
- [x] Yes
- [ ] Partial
- [ ] No

Summary:
- agentic-skeleton `main` merged and pushed, tag `v1.1.0`: `make portal` / `python tools/portal.py` download, verify, cache, start and reopen the portal.

---

# 10. Next Steps

- Follow-ups: portal server `--repo` flag (portal side, before the first release); release pipeline emitting `manifest.json` format 1; `.portal/` in `.gitignore` via `make adopt` (ADR-003); merge skeleton v1.1.0 into this repository.
- Risks: Windows behaviour untested (NFR-10 manual matrix); chicken-and-egg order of the first portal and skeleton releases.
- Improvements: macOS/Windows jobs in the skeleton CI.

---

# 11. Addendum (Post-Closure Only)

### 2026-10-20
- Note: follow-ups done on owner request: agentic-skeleton v1.1.1 (`.portal/` in the skeleton `.gitignore` and added by `make adopt`; CI job `portal-launcher` on macOS and Windows, Python 3.11, green: covers AC3 and NFR-10 for the launcher; health probe bypasses proxies; startup wait 60 s). macOS CI showed `HTTPServer` stalling at bind on reverse DNS (`getfqdn`): fixed in the fake test server, recorded for the real server in AP0107 together with `--repo` and the manifest format. Skeleton 1.1.1 merged into this repository.
- Impact: none on the accepted scope; AP0107 backlog entry extended (AC `--repo`, notes).
