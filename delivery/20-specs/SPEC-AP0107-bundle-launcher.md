# SPEC-AP0107 - Release bundle for make portal

## References
- Story ID: AP0107 (statement: `analysis/10-stories/STORY_AP0107_bundle_launcher.md`, not copied here)
- Brief: BRIEF-AP0107
- RUN: RUN-AP0107
- Requirements: FR-23, NFR-09, NFR-10

---

## Status
Done

---

# 1. Goal

The release pipeline publishes `agentic-portal-<version>.zip` and `manifest.json` (format 1) that the skeleton launcher downloads, verifies and starts for a repository with no Node on the machine, on Linux, macOS and Windows. CI proves the real chain on all three before any release is published.

---

# 2. User / Business Value

Makes `make portal` usable: the first release (with AP0102 and AP0104) can be pinned by any project with zero setup.

---

# 3. Scope

Included:
- **Manifest format 1** (`scripts/build_bundle.py`): `manifest: 1`, `version`, `asset`, `size`, `sha256`, `requires_python` (`">=3.14"`), plus `contract_built_for` (ignored by the launcher). Old keys `file`, `python_min` removed.
- **Zip layout and hygiene**: root = `portal_server/`, `web/dist/`, `VERSION` (no `server/` prefix); no tests, caches or `.pyc`; fixed timestamps, explicit modes (files 0644); every entry name checked against the launcher's safe-extraction rules (no absolute path, `..`, drive letter, backslash, symlink); a failing name aborts the build.
- **Server**: `find_static` works for the bundle layout (static at `<root>/web/dist`) and the dev layout; `--repo <path>` (default cwd) must contain `project.toml`, otherwise exit non-zero with a clear message; `--help` lists `--repo`; `server_bind` overridden so startup never calls `getfqdn()`.
- **CI job `launcher`** (`.github/workflows/ci.yml`) on ubuntu, macos, windows (`fail-fast: false`): build web, zip and manifest; checkout agentic-skeleton at `SKELETON_PIN` (as job `contract`) for `tools/portal.py`; fixture repo (temp dir) with `project.toml [portal] version = <VERSION>` and `.portal` untouched; `PORTAL_BUNDLE=<zip>` + `--no-browser`; poll `/api/health` until it answers and assert it reports that repository and version; fail if `node` is on PATH for the step (removed from PATH); stop the portal at the end. A second fixture with a skeleton whose contract major differs asserts `/api/health` and `GET /api/contract` report `incompatible`.
- **Release workflow hardening** (`.github/workflows/release.yml`): tag must equal `v$(cat VERSION)`; tag commit must be an ancestor of `origin/main`; after building, verify the zip against `manifest.json` (size, sha256, layout) before publishing; `0.*` published with `--prerelease`; refuse to run if a release for the tag already exists (never overwrite); release dry run (same steps up to, not including, `gh release create`) on pull requests touching `scripts/build_bundle.py` or `release.yml`.
- **Docs**: short release procedure (tag, what the pipeline checks, pre-release rule, how to verify a published release) in `docs/` and a pointer in `server/AGENTS.md` if it lists distribution.

Out of scope:
- Launcher code (skeleton), token delivery (AP0110), auto-update, bundle signing.
- UI message for contract mismatch (AP0104/AP0108).
- Browser matrix of NFR-10 (owner verifies manually per release; CI covers start on three OSes).
- Cutting the first release itself (owner action after merge).

---

# 4. Acceptance Criteria

- [x] AC1: Given a tag on `main` whose commit is reachable from `origin/main`, when the release pipeline runs, then a GitHub Release with `agentic-portal-<version>.zip` and `manifest.json` (format 1) is published; a tag off `main`, a tag ≠ `v$(cat VERSION)` or an existing release stops the pipeline before publishing, and `0.*` is marked pre-release. → test: `scripts/tests/test_release_checks.py::test_*` for the check script used by `release.yml`; workflow dry run in CI (PR); first real release: manual — owner checks the published assets.
- [x] AC2: Given the built bundle pinned in a fixture repository, when the real launcher runs on Linux, macOS and Windows without Node, then `/api/health` answers for that repository. → test: CI job `launcher` (3 OS) via `scripts/tests/launcher_smoke.py`.
- [x] AC3: Given the launcher starts the bundle with `--repo <root>`, when the server starts, then it serves that repository, `--help` lists `--repo`, a directory without `project.toml` is refused, and startup does not stall on reverse DNS. → test: `server/tests/test_server.py::test_repo_option`, `::test_help_lists_repo`, `::test_bind_does_not_resolve_fqdn`.
- [x] AC4: Given a fixture skeleton with another contract major, when the bundle runs, then `/api/health` and `GET /api/contract` report `incompatible`, and the manifest carries `contract_built_for`. → test: `scripts/tests/launcher_smoke.py` (incompatible fixture, CI) and `scripts/tests/test_bundle.py::test_manifest_format_1`.
- [x] AC5: Given a zip entry that fails the safe-name rules, when the bundle is built, then the build fails. → test: `scripts/tests/test_bundle.py::test_unsafe_entry_name_fails_build`.
- [x] AC6: Given the built zip, then its root holds only `portal_server/`, `web/dist/` and `VERSION`, with fixed timestamps and no tests or caches, and the manifest size and sha256 match it. → test: `scripts/tests/test_bundle.py::test_layout_and_manifest_match_zip`.

---

# 5. Tasks

- `TSK-AP0107-01` `build_bundle.py`: manifest format 1, root layout, hygiene, safe-name check, tests (AC5, AC6, part of AC4).
- `TSK-AP0107-02` Server: `find_static` for the bundle layout, `--repo` validation and help, `server_bind` override, tests (AC3).
- `TSK-AP0107-03` Verification script for the bundle against its manifest and the release checks (tag = VERSION, ancestor of `origin/main`, pre-release flag, release not existing) with unit tests (AC1).
- `TSK-AP0107-04` CI job `launcher` on three OSes with the real launcher at `SKELETON_PIN`, fixture repos (compatible and incompatible), no Node on PATH, `scripts/tests/launcher_smoke.py` (AC2, AC4).
- `TSK-AP0107-05` `release.yml` hardening and dry run on pull requests (AC1).
- `TSK-AP0107-06` Release-procedure docs; Spec reconciliation inputs for persist.

---

# 6. Execution Boundaries

The agent is allowed to:
- Edit `scripts/` (build, checks, smoke script, tests), `server/portal_server/app.py` and `server/tests/`, `.github/workflows/ci.yml` and `release.yml`, and the docs named in §9.

The agent is not allowed to:
- Edit skeleton files (`tools/`, `schemas/`, workflow files rendered from the skeleton): changes go upstream (NFR-14).
- Add third-party runtime dependencies (NFR-08) or require Node at runtime (NFR-09).
- Change the AP0102 auth pipeline, the AP0104 contract API or the health fields.
- Create a tag or publish a release, or bump `VERSION`.

---

# 7. Quality Gates

- [x] Tests added/updated (`make test`)
- [x] Build passes (`make lint`, web build, bundle build)
- [x] Public interfaces updated if impacted (manifest format 1, zip layout, `--repo`)
- [x] Domain invariants respected (ADR-003, NFR-08, NFR-09, NFR-14)
- [x] No breaking changes unless explicitly approved
- [x] CI jobs `launcher` (3 OS) and release dry run green on the story PR

---

# 8. Stop Conditions

The standard ones apply (`delivery/AGENT_GUIDE.md` §9). Story-specific ones only:
- The pinned skeleton launcher rejects the format-1 bundle in a way that needs a launcher change (goes upstream, not here).
- A CI runner cannot provide Python 3.14 or removing Node from PATH is not possible on a runner.

---

# 9. Impacted Areas

- Code: `scripts/build_bundle.py`, new release-check and smoke scripts under `scripts/`, `server/portal_server/app.py`
- Interfaces (API, CLI, file formats, protocols, library API): bundle `manifest.json` (format 1), zip layout, `--repo`/`--help` of `portal_server`
- Domain: n/a
- UX: none
- Platforms / distribution: GitHub Releases, `release.yml`, CI on Linux/macOS/Windows
- Tests: `scripts/tests/`, `server/tests/`
- Docs: `docs/` (release procedure), `server/AGENTS.md` if impacted

---

# 10. Notes / Clarifications

- Sources: `analysis/30-refined/REFINED_AP0107_bundle_launcher.md`, workshop 2026-10-20, ADR-003 and its revisions.
- `--repo` (default cwd) already exists since AP0104; this Spec adds the `project.toml` check and the tests. `find_static` may already work for the new layout (root = zip root): TSK-02 confirms by test before changing anything.
- Story AC3 ("incompatibility message") is shown by AP0104/AP0108; here it is proven at server level only (Refined §4).
- The CI job pins the launcher with `SKELETON_PIN` (`v1.3.0`); without AP0110 in that tag the job runs `--no-browser` and checks health only.

---

# 11. Final Reconciliation

Facts written by `/persist` before Done (no checkboxes):

- Reconciled at: 2026-10-21
- AC met: 6/6 (AC1 and AC2 by the CI jobs `release-dry-run` and `launcher`; the first real release is the owner's tag)
- Tasks deferred: none
- Spec changes since Ready: none
- Reference docs updated: none (`docs/RELEASE.md`, `server/AGENTS.md` updated)

---

## Revisions

> One line per change after approval or closure: date, what, source (minutes, owner decision, commit).
