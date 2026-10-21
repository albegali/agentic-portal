# RUN-AP0107

## References
- Story ID: AP0107
- Spec: SPEC-AP0107
- Started at (datetime): 2026-10-21T16:01
- Completed at (datetime): 2026-10-21T17:49
- Branch: ap0107-bundle-launcher
- PR: https://github.com/albegali/agentic-portal/pull/9

---

## Status
Closed

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
- Step 1 (TSK-01): `build_bundle.py` writes manifest format 1, root layout `portal_server/`, `web/dist/`, `VERSION`, `check_entry_name` on every entry, partial zip removed on failure; `test_bundle.py` updated (manifest, layout, unsafe names, abort without zip, extraction cwd = zip root, `--repo` fixture).
- Step 2 (TSK-02): `parse_args` (`--repo` default cwd, must contain `project.toml`, `--help` lists it), `PortalHTTPServer.server_bind` without `getfqdn()`; tests added; `find_static` needed no change (tests cover both layouts); two existing `main()` tests now pass `--repo`.
- Step 3 (TSK-03): `scripts/release_checks.py` (`tag`, `ancestor`, `prerelease`, `verify`) with `test_release_checks.py`; `verify` also run on the real built bundle.
- Step 4 (TSK-04): `scripts/tests/launcher_smoke.py` (real launcher, PATH without node, compatible and other-major fixtures) run locally with this repository's `tools/`; CI job `launcher` (3 OS, skeleton checkout at the pin) added.
- Step 5 (TSK-05): `release.yml` hardened (tag = VERSION, ancestor of origin/main, existing release refused, verify before publish, `--prerelease` for 0.x); job `release-dry-run` on pull requests touching the release machinery.
- Step 6 (TSK-06): `docs/RELEASE.md`, pointer in `server/AGENTS.md`.

### Changes (high-level)
- Code: `scripts/build_bundle.py`, `scripts/release_checks.py` (new), `server/portal_server/app.py`.
- Interfaces: bundle manifest format 1 and zip layout; `portal_server --repo` validated; workflows `ci.yml` (jobs `launcher`, `release-dry-run`), `release.yml`.
- Domain: none.
- Tests: ${PY:-python3} -m unittest discover -s server/tests -q && ${PY:-python3} scripts/check_deps.py server && ${PY:-python3} -m unittest discover -s scripts/tests -q && npm --prefix web test -- --run → pass
- Specs: none.

---

# 4. Verification

- Build: OK (`make lint`; bundle built from `web/dist`)
- Tests: OK (`make test` with Python 3.14: server 83 run / 2 skipped, scripts 17)
- Interfaces / target platforms: OK on macOS (local launcher smoke against `tools/portal.py` of this repository, compatible and incompatible fixtures); Linux and Windows run in CI only after push, workflows only syntax-checked locally
- Manual (if any): not run (first release, browser matrix are owner actions)

Notes:
- AC4 wording "health and the version gate report `incompatible`": the gate state is `incompatible` on `GET /api/contract`; `/api/health` carries no state and shows the skeleton contract (`unknown` for a 2.x envelope, which fails the 1.x schemas). The smoke asserts exactly that.
- `launcher_smoke.py` takes `--skeleton`; CI passes the checkout at the pin, local runs default to this repository's vendored `tools/`.

If FAIL → move to Tuning.

---

# 5. Tuning Log (If needed)

> Only within scope. The acceptance is the human's: fill it when they run `/persist` (or say the result is accepted).

Tuning accepted by: Alberto Galimberti
Date: 2026-10-21

### Entry #1
- Issue: CI job `launcher` failed on all three OSes: the launcher resolves a relative `PORTAL_BUNDLE` against the fixture repo's working directory ("does not exist").
- Fix: `launcher_smoke.py` resolves `--bundle` to an absolute path before starting the launcher.
- Impact: test script only; no product code or Spec change.
- Verified: Yes (local run with a relative `--bundle` from the repository root); CI result in §8.

### Entry #2 (review #1)
- Issue: review #1 findings: AC4 wording deviation undocumented; smoke manifest check silently skipped and inline `__import__("signal")`; cancelled `other-os` jobs on the last commit.
- Fix: Deviation #1 in §6 and Spec AC4/§11/Revisions aligned; `launcher_smoke.py` drops the conditional manifest check (covered by `test_manifest_format_1`) and imports `signal` at the top; CI re-run on the new push (§8 updated by `/persist`).
- Impact: test script and artifacts only; no product code.
- Verified: Yes locally (`PY=python3.14 make test` pass, `launcher_smoke.py` OK on macOS, `make check` OK); CI after push in §8.

---

# 6. Deviations

> One entry per deviation or stop condition. `Requires approval` sets the RUN to Blocked until a human approves it.

### Deviation #1
- What changed: AC4 wording. Health does not carry the gate state; `incompatible` is reported by `GET /api/contract` (health shows the skeleton contract, `unknown`/non-1.0 for a 2.x envelope). The smoke asserts exactly that.
- Why: AP0104 health/contract fields are out of scope (Spec §6); the Spec wording assumed health carried the state. Found by review #1.
- Plan impact: none; Spec AC4 and §11 aligned, Revisions line added.
- Scope impact: Minor
- Approved by:
- Date:

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Reference docs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- Spec §11 written, ACs ticked, status Done. Docs touched: `docs/RELEASE.md` (new), `server/AGENTS.md` (Distribution). No `reference/` change needed: ADR-003 and its revisions already describe format 1 and the layout.

---

# 8. Quality Gates Check

Facts, not ticks (`make check` reads them):

- AC: 6/6 met (Spec §4; AC1 and AC2 rest on the CI jobs `launcher` and `release-dry-run`, the real release is the owner's tag)
- Tests: `PY=python3.14 make test` → pass (server 83 run, 2 skipped; scripts 17); `python3.14 scripts/tests/launcher_smoke.py` → pass (macOS)
- Out-of-scope changes: none (existing `main()` tests in `server/tests/test_server.py` and `test_security.py` got `--repo`, a consequence of the new `project.toml` check)
- CI: green — https://github.com/albegali/agentic-portal/pull/9 (head 718908c: portal-ci run 39627502621 and workflow-check run 39627502513 all jobs pass, incl. `launcher` on 3 OSes, `release-dry-run`, `other-os`; no required checks configured)

### Security review
> Only for security-sensitive stories, written by `/security-review` (`workflow/steps/security.md`); delete otherwise.
- Date:
- Reviewer:
- Outcome: `ok` / `changes-requested`
- Findings:

---

### Gates
> Written by `make gates` on 2026-10-21T17:38+02:00; do not edit by hand.
- test: `${PY:-python3} -m unittest discover -s server/tests -q && ${PY:-python3} scripts/check_deps.py server && ${PY:-python3} -m unittest discover -s scripts/tests -q && npm --prefix web test -- --run` → pass (OK)
- lint: `${PY:-python3} -m compileall -q server scripts && npm --prefix web run lint && npm --prefix web run typecheck` → pass (> tsc --noEmit)
- secrets: `/opt/homebrew/opt/python@3.14/bin/python3.14 tools/secret_scan.py --branch` → pass (secret scan: OK)






# 9. Outcome

Tasks completed:
- TSK-AP0107-01, TSK-AP0107-02, TSK-AP0107-03, TSK-AP0107-04, TSK-AP0107-05, TSK-AP0107-06

Tasks deferred:
- none

Goal achieved:
- [x] Yes
- [ ] Partial
- [ ] No

Summary:
- The release pipeline builds and verifies a format-1 bundle that the skeleton launcher starts; CI proves the chain on three OSes and hardens the release.

---

# 10. Next Steps

- Follow-ups: owner cuts the first release (`v0.1.0`) per `docs/RELEASE.md` after merge; confirm the 0.x pre-release scheme there.
- Risks: PATH stripping of Node on hosted runners (`/usr/bin` may hold `node`); the real `release.yml` is exercised only at the first tag.
- Improvements: token round trip in the smoke once the launcher token story (AP0110) is in the pinned tag.

---

# 11. Review

> Written by `/review-story` (review mode), one entry per review, newest last. `ok-to-close` → RUN `Reviewed`;
> `changes-requested` → RUN `Tuning`, findings applied with `/run <ID> tuning: …`, then `/persist` and a new review.

### Review #1
- Date: 2026-10-21
- Reviewer: review agent (Claude Sonnet 5.5)
- Outcome: `changes-requested`
- Findings:
  - delivery/20-specs/SPEC-AP0107-bundle-launcher.md:51 (AC4), RUN §6 → AC4 says `/api/health` and `GET /api/contract` report `incompatible`; the code and `launcher_smoke.py:119-124` prove `/api/contract` `incompatible` and health answering with a non-1.0 skeleton contract (RUN §4 Notes). Spec §11 says "Spec changes since Ready: none", §6 is empty, AC4 is ticked as met → record the deviation (RUN §6 Deviation #1, Scope impact Minor) and a Spec Revisions line aligning the AC4 wording to what is tested; correct Spec §11 accordingly.
  - scripts/tests/launcher_smoke.py:130-132 → the manifest `contract_built_for` check is silently skipped when `manifest.json` is not next to the bundle (`else {}`) → make it unconditional or drop it (already covered by `test_manifest_format_1`). Non-blocking nit; same for the inline `__import__("signal")` (line 84).
  - RUN §8 CI → run 39626297391 (HEAD 9a721fb, docs-only) shows `workflow-check` `other-os` (macos, windows) CANCELLED, not failed; `portal-ci` (incl. `launcher` ×3, `release-dry-run`, `e2e`) green on HEAD; `workflow-check` was fully green on c4c70dc → re-run the cancelled jobs and cite the final run in §8.
  - Checked, no finding: Brief/Spec/RUN scope aligned, no skeleton files touched (NFR-14), stdlib only (NFR-08), no Node at runtime (NFR-09), AC1-AC6 each mapped to a test or CI job, gates pass, `make check` OK, no secrets, `server/AGENTS.md` rules respected, tag/ancestor/existing-release/verify/prerelease checks present in `release.yml`.
  - Open at close (not a finding): Pending owner action, first release `v0.1.0`.

### Review #2
- Date: 2026-10-21
- Reviewer: review agent (Claude Sonnet 5.5)
- Outcome: `ok-to-close`
- Findings:
  - Review #1 findings resolved: AC4 deviation recorded (RUN §6 Deviation #1, Spec AC4/§11/Revisions aligned); `launcher_smoke.py` imports `signal` at the top, no conditional manifest check left; PR #9 checks on HEAD eca98cb all pass (`launcher` ×3, `release-dry-run`, `other-os`, `e2e`, `secrets`).
  - RUN §8 CI cites head 718908c; HEAD eca98cb is docs-only and also green → non-blocking, `/close` may refresh the run ids.
  - RUN §6 Deviation #1 has empty `Approved by`/`Date` (Scope impact Minor, no approval required) → nothing to do.
  - Checked, no finding: Brief/Spec/RUN aligned, AC1-AC6 mapped to tests/CI, no scope creep or skeleton files touched (NFR-14), stdlib only (NFR-08), no Node at runtime (NFR-09), gates pass, `make check` OK, no secrets, `server/AGENTS.md` rules respected.
  - Open at close (not a finding): Pending owner action, first release `v0.1.0` (a RUN cannot close with Goal achieved `Yes` while it is open; settle it per `/close`).

---

## Pending owner actions

> Actions only a person can do that the story still waits for (a tag, a release, a setting, a sign-off), one per line.
> `make next` lists the open ones of every RUN; a RUN cannot close with Goal achieved `Yes` while one is open.
- [ ] Cut the first release (`v0.1.0`, pre-release) per `docs/RELEASE.md` after merge — owner: Alberto Galimberti — since: 2026-10-21

---

## Revisions

> Post-closure only: factual corrections (links, typos, recorded results), one line each with date and source.
> A change in behaviour is a new story with `supersedes = "<ID>"` in `backlog/stories.toml`, never a revision.

