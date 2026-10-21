# RUN-AP0107

## References
- Story ID: AP0107
- Spec: SPEC-AP0107
- Started at (datetime):
- Completed at (datetime):
- Branch: ap0107-bundle-launcher
- PR:

---

## Status
Approved

---

# 1. Execution Strategy (Agent)

### Required Reads
- [x] Target Spec
- [x] Scoped package `AGENTS.md` files, if applicable:
  - `server/AGENTS.md`
- [x] `delivery/templates/RUN-template.md`

### Plan
Order keeps the build green at every step (the bundle test and the CI job move with the layout).
- TSK-AP0107-01: rewrite `build_bundle.py` in one change: manifest format 1 (`manifest`, `version`, `asset`, `size`, `sha256`, `requires_python`, `contract_built_for`), archive names `portal_server/…`, `web/dist/…`, `VERSION` (source stays `server/portal_server`), a `check_entry_name` helper applied to every entry (build raises on failure), 0644 modes and fixed timestamps kept. Update `scripts/tests/test_bundle.py` in the same step (manifest, layout, extraction `cwd` becomes the zip root, unsafe name test, layout/manifest-match test).
- TSK-AP0107-02: tests first for `find_static` on both layouts, `--repo` without `project.toml`, `--help` listing `--repo`, `server_bind` not calling `getfqdn`; then minimal code in `app.py`: validate `--repo` (exit 2 with message), subclass `ThreadingHTTPServer.server_bind` as `socketserver.TCPServer.server_bind` + set `server_name`/`server_port` directly. Change `find_static` only if its test fails.
- TSK-AP0107-03: new `scripts/release_checks.py` (stdlib, CLI used by `release.yml`): `tag` (= `v$(cat VERSION)`), `ancestor` (git merge-base against `origin/main`), `prerelease` (prints `--prerelease` for `0.*`), `verify` (zip vs `manifest.json`: size, sha256, root entries, format 1, safe names). The "release does not exist yet" check stays a `gh release view` step in the workflow. Unit tests with temp git repos and zips in `scripts/tests/test_release_checks.py`.
- TSK-AP0107-04: `scripts/tests/launcher_smoke.py` (not discovered by `unittest discover`; run by CI): builds the fixture repo in a temp dir (`project.toml [portal] version`, a copy of the skeleton `tools/` and `schemas/` from the checkout), runs `python skeleton/tools/portal.py --no-browser` with `PORTAL_BUNDLE`, `PATH` stripped of `node`, polls `.portal/run.json` + `/api/health`, asserts the repo and version, terminates the process tree; second pass with the fixture `tools/wf.py` patched to report another contract major and asserts `incompatible` on health and `/api/contract`. CI job `launcher` (matrix ubuntu/macos/windows, `fail-fast: false`, `needs: full`): checkout + skeleton checkout at `SKELETON_PIN`, Node only to build web, build bundle, run the smoke script.
- TSK-AP0107-05: `release.yml`: checkout with `fetch-depth: 0`, steps `release_checks.py tag|ancestor`, `gh release view` must fail, `verify` after the build, `gh release create` with the `prerelease` flag; dry-run job in `ci.yml` on pull requests touching `scripts/build_bundle.py`, `scripts/release_checks.py` or `release.yml`, running the same steps up to `verify`.
- TSK-AP0107-06: `docs/RELEASE.md` (procedure, checks, pre-release rule, verifying a release, first-release owner action) and pointer in `server/AGENTS.md`; collect reconciliation inputs.

### Assumptions
- The pinned skeleton tag (`v1.3.0`) contains `tools/portal.py` with `PORTAL_BUNDLE` and `--no-browser` (launcher released in 1.1.0); no launcher change is needed.
- The launcher runs the server as `python3.<minor> -m portal_server --repo <root>` with the bundle root as cwd, so `ROOT` (parent of `portal_server/`) is the zip root and `find_static` already finds `<root>/web/dist`.
- The incompatible fixture is obtained by editing the copied `tools/wf.py` version output in the temp repo (not a skeleton file in this repository).
- Python 3.14 is available on the three hosted runners through `setup-python`; Node is removed from `PATH` only for the launcher step, after the web build.

### Risks / Open Questions
- Windows: process-tree termination, `PATH` stripping and `py -3.14` lookup in the launcher may differ; stop condition in the Spec applies if a runner cannot do it.
- `.portal/run.json` format belongs to the launcher; the smoke script reads it only for the port and falls back to scanning the launcher output.
- First real release is an owner action (tag), listed under Pending owner actions at persist; the release workflow itself is exercised only by the dry run until then.

### Scoped Agent Rules Check
- Applies: Yes (`server/AGENTS.md`; `scripts/` has no package rules)
- Files read:
  - `server/AGENTS.md`
- Notes:
  - Stdlib only at runtime; test/CI helpers under `scripts/` stay stdlib; `check_deps.py` keeps passing.
  - Any new route needs a test: none added (only startup options).
  - Cross-platform: `pathlib`, Windows branch for process termination in the smoke script.

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
- Approved via `/run AP0107 approve`.

Reviewer: Alberto Galimberti
Date: 2026-10-21

---

# 3. Execution Log (Agent)

### Steps
- Step 1: …
- Step 2: …

### Changes (high-level)
- Code:
- Interfaces:
- Domain:
- Tests:
- Specs:

---

# 4. Verification

- Build: OK / FAIL
- Tests: OK / FAIL
- Interfaces / target platforms: OK / FAIL
- Manual (if any): OK / FAIL

Notes:
- …

If FAIL → move to Tuning.

---

# 5. Tuning Log (If needed)

> Only within scope. The acceptance is the human's: fill it when they run `/persist` (or say the result is accepted).

Tuning accepted by:
Date:

### Entry #1
- Issue:
- Fix:
- Impact:
- Verified: Yes / No

### Entry #2
- …

---

# 6. Deviations

> One entry per deviation or stop condition. `Requires approval` sets the RUN to Blocked until a human approves it.

### Deviation #1
- What changed:
- Why:
- Plan impact:
- Scope impact: None / Minor / Requires approval
- Approved by:
- Date:

---

# 7. Persistence / Reconciliation

- [ ] Spec updated (if needed)
- [ ] Reference docs updated (if needed)
- [ ] Acceptance Criteria aligned

Summary:
- …

---

# 8. Quality Gates Check

Facts, not ticks (`make check` reads them):

- AC: n/n met (Spec §4; the tests named there)
- Tests: <command> → pass / fail (counts)
- Out-of-scope changes: none / <files and why>
- CI: green / red / none (no remote) — <PR URL>

### Security review
> Only for security-sensitive stories, written by `/security-review` (`workflow/steps/security.md`); delete otherwise.
- Date:
- Reviewer:
- Outcome: `ok` / `changes-requested`
- Findings:

---

# 9. Outcome

Tasks completed:
- TSK-...

Tasks deferred:
- …

Goal achieved:
- [ ] Yes
- [ ] Partial
- [ ] No

Summary:
- …

---

# 10. Next Steps

- Follow-ups:
- Risks:
- Improvements:

---

# 11. Review

> Written by `/review-story` (review mode), one entry per review, newest last. `ok-to-close` → RUN `Reviewed`;
> `changes-requested` → RUN `Tuning`, findings applied with `/run <ID> tuning: …`, then `/persist` and a new review.

### Review #1
- Date:
- Reviewer:
- Outcome: `ok-to-close` / `changes-requested`
- Findings:
  - …

---

## Pending owner actions

> Actions only a person can do that the story still waits for (a tag, a release, a setting, a sign-off), one per line.
> `make next` lists the open ones of every RUN; a RUN cannot close with Goal achieved `Yes` while one is open.
- [ ] <action> — owner: <name> — since: <YYYY-MM-DD>

---

## Revisions

> Post-closure only: factual corrections (links, typos, recorded results), one line each with date and source.
> A change in behaviour is a new story with `supersedes = "<ID>"` in `backlog/stories.toml`, never a revision.

