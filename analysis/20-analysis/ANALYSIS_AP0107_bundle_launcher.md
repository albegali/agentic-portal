---
artifact_type: analysis
us_id: STORY_AP0107
title: Release bundle for make portal
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0107_bundle_launcher.md
  - reference/project-summary.md
related_references:
  - reference/product/functional-requirements.md#FR-23
  - reference/product/non-functional-requirements.md#NFR-09
  - reference/product/non-functional-requirements.md#NFR-10
  - reference/architecture/ADR-003-distribution.md
last_updated: 2026-10-20
---

# Analysis AP0107 - Release bundle for make portal

## 1. References

- ID: AP0107
- Source story: analysis/10-stories/STORY_AP0107_bundle_launcher.md
- Roadmap phase: R1 (sprint S2 in PLAN.md)
- Sources used: Story, project summary, FR-23, NFR-09, NFR-10, ADR-003 (incl. 2026-10-20 revision), Analysis/Refined AP0101, Analysis AP0106 §6+, `tools/README.md` (Portal launcher), `scripts/build_bundle.py`, `.github/workflows/release.yml`, `server/portal_server/app.py`, `tools/portal.py`
- Missing sources: `ci.yml` and `workflow-check.yml` not read; architecture.md §2/§6; the AP0106 Spec/RUN (what the launcher tests cover)

## 2. Original User Story

### Story text

As a developer using the workflow, I want the portal release pipeline to publish a versioned bundle zip with SHA-256 manifest that the skeleton launcher starts, so that I get the portal with zero setup and no Node.

### Description

- Epic: EP-01 — Technical foundations
- Priority (MoSCoW): Must · Release: R1 · Size: M · Type: technical
- Requirements: FR-23, NFR-09, NFR-10
- Depends on: AP0101, AP0106
- Notes: ADR-003. Launcher is AP0106 (skeleton v1.1.0): the release publishes `manifest.json` format 1 (`manifest`, `version`, `asset`, `size`, `sha256`, `requires_python`) next to the zip, `portal_server/` at the zip root (tools/README.md, Portal launcher). The server must not stall at bind: `HTTPServer.server_bind` calls `getfqdn()` (reverse DNS, seconds on macOS); override it as the launcher tests do.
- Out of scope: Launcher code, auto-update.

## 3. Intent Understanding

### Functional goal

- Make a tagged portal release installable by a project that only pins `[portal] version` and runs `make portal`, without Node, on macOS, Windows and Linux.

### Actors involved

- Developer/owner running `make portal`; release maintainer (the owner, on GitHub Actions); the skeleton launcher (consumer of the bundle).

### Expected outcome

- A release pipeline that produces and publishes assets in exactly the shape the released launcher accepts, and a server that starts cleanly from the extracted bundle with the launcher's arguments.

## 4. Information Classification

### Facts

- Launcher contract (released, skeleton 1.1.x): downloads `manifest.json` then the zip it names from `https://github.com/<source>/releases/download/v<version>/`; manifest format 1 keys `manifest`, `version`, `asset`, `size`, `sha256`, `requires_python`; exit 2 on a different manifest major or checksum/size mismatch; extracts safely into `.portal/<version>/`; runs `python -m portal_server --host 127.0.0.1 --port <p> [--repo <root>]` with `PYTHONPATH=<bundle>` and cwd = repository root; `--repo` is used only if `--help` lists it; waits for unauthenticated `GET /api/health`; writes `.portal/run.json`; opens the browser.
- **Current portal state** (code read): `scripts/build_bundle.py` writes a manifest with keys `version`, `file`, `sha256`, `python_min`, `contract_built_for` (no `manifest`, `asset`, `size`, `requires_python`) and puts server files under `server/portal_server/…` and web under `web/dist/…`; `app.py` locates `web/dist` via `ROOT`/`ROOT.parent`; `portal_server` has no `--repo` option; `ThreadingHTTPServer` is used without a `server_bind` override; `release.yml` triggers on `v*` tags, checks tag = `VERSION`, runs lint/build/test, builds the bundle on Linux only and publishes with `gh release create`.
- NFR-09: works without Node; NFR-10: macOS, Windows, Linux and the two latest versions of the major browsers; AP0101 refined: CI smoke test of the bundle start on macOS and Windows.
- Release pipeline is owned by the project owner on GitHub Actions; the repository is public; checksum without signing is accepted (AP0106 workshop).
- Requires Python ≥ 3.14 for the server (`requires_python`), launcher ≥ 3.11 picks `python3.<minor>` / `py -3.<minor>`.

### Clarifications received

- ADR-003 revision 2026-10-20 (owner, AP0106 Spec review): GitHub Releases stay; manifest format 1; running-instance detection through `.portal/run.json` + `/api/health`.

## 5. Original Acceptance Criteria

- Given a tag on main, when the release pipeline runs, then a GitHub Release with the bundle zip and SHA-256 manifest is published.
- Given the published version pinned in a fixture repository, when I run `make portal`, then the portal starts for that repo without Node.
- Given a bundle built for one contract major, when the skeleton reports another, then the portal shows an incompatibility message.
- Given the launcher starts the bundle with `--repo <root>`, when the server starts, then it serves that repository and `--help` lists `--repo`.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- AC 1 "a tag on main": the workflow triggers on any `v*` tag, not only commits on main; should tags not reachable from main be refused?
- AC 3 depends on AP0104 (version gate) and on AP0102's token flow, neither listed as dependencies: is it verified here end to end or only that the bundle carries `contract_built_for`? Also "the portal shows" conflicts with FR-27's Settings-only wording (see AP0104).
- "Starts for that repo": AP0101's page and health work without a repo; what the user sees for the repo (name, path) before the shell stories is undefined.

### Functional gaps

- No AC for the **first-run experience over the real chain**: pin → download → verify → start → browser opens the authenticated URL (the token is not delivered by the released launcher — see AP0102).
- No AC for prerelease/yanked versions, republishing the same tag, tag/VERSION mismatch (exists in the workflow), or what a project sees for a version that has no release.
- NFR-10: browsers (latest 2 versions of Chrome, Edge, Safari, Firefox, Chromium) are verified manually; no AC says when/who.
- Windows support: Windows-specific acceptance only through CI smoke; port, signal handling and `py` launcher paths are exercised by the skeleton tests, not by the bundle.

### Technical gaps

- **Manifest mismatch**: the AP0101 manifest (`file`, `python_min`) differs from format 1 (`manifest`, `asset`, `size`, `requires_python`); `contract_built_for` is "unknown" and is not part of format 1 (unknown keys are ignored, so it may stay).
- **Layout mismatch**: the launcher expects `portal_server/` at the zip root (bundle dir on `PYTHONPATH`); the AP0101 zip nests it under `server/` and keeps `web/dist/`; static lookup in `app.py` must follow the new layout (`web/dist` at root).
- Server lacks `--repo` (AC 4) and uses the working directory; how it reaches the repo root for skeleton calls is undefined.
- `server_bind` override to avoid `getfqdn()` stalls (Notes) is not implemented; bind address is a literal `127.0.0.1`.
- Release job runs only on Linux; a bundle zip is platform independent but the start smoke test on macOS/Windows must run against the **published** zip and manifest (or at least the built one) with the real launcher.
- Zip reproducibility, permissions and entry names must pass the launcher's safe-extraction rules (no absolute, `..`, drive letters, symlinks).
- Pinning: which skeleton launcher version the pipeline tests against (the chicken-and-egg noted in AP0106) and how the portal repository consumes `tools/portal.py` in its own CI.
- Release notes/versioning: `VERSION` ↔ tag ↔ manifest `version` consistency; pre-release handling.

### Dependencies or ownership points to clarify

- Depends on AP0106 (done, skeleton v1.1.x) and AP0101 (done); soft dependencies on AP0102 (token delivery) and AP0104 (contract gate) for AC 3 and for a usable first run.
- The first public release (`v0.1.0`?) and who triggers it (owner) is a human step outside the code.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions only: an answer from the PO / stakeholder is mandatory.

- [High impact] Must the first published release already give a **usable** portal (authenticated page, health with real versions — i.e. AP0102 and AP0104 included), or may AP0107 publish an early `0.x` bundle that starts but cannot yet read the repository? — decides the sprint order within S2 and what AC 2 promises to early users.
- [Medium impact] Which version scheme do releases follow (e.g. `0.1.0` pre-releases until R1 closes, `1.0.0` at R1) and may releases be marked pre-release on GitHub? — user-visible pin values in every project's `project.toml`.
- [Medium impact] Who runs the cross-OS/browser verification of NFR-10 before tagging (owner manual matrix, or only CI smoke on macOS/Windows/Linux plus a manual browser check per release)? — release confidence versus effort.
- [Low impact] Are republished or withdrawn releases allowed (same tag replaced)? — affects trust in the pinned checksum.

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Align the artifact with the launcher — **Proposal**: `scripts/build_bundle.py` writes manifest format 1 `{"manifest":1,"version","asset","size","sha256","requires_python":">=3.14"}` (plus `contract_built_for` as an ignored extra), zip root holds the `portal_server/` package, `web/dist/` and `VERSION`; `find_static` already finds `web/dist` next to the package · **Why**: the released launcher is the consumer and cannot change in this story; the only change to the current zip is dropping the `server/` prefix · **Alternatives**: static assets inside the package (self-contained, needs a `find_static` change) · **Confidence**: high
- [High impact] `--repo` and bind — **Proposal**: add `--repo <path>` (default: current directory) resolved to an absolute directory that must contain `project.toml`, passed to the contract client and health; `--help` lists it; override `server_bind` in a `ThreadingHTTPServer` subclass to skip `socket.getfqdn()` (set `server_name` to the host, `server_port` to the bound port) · **Why**: AC 4 and the macOS stall in the Notes · **Alternatives**: wrap launcher timeout (hides the stall) · **Confidence**: high
- [High impact] End-to-end test of the real chain — **Proposal**: CI job after the bundle build on Linux, macOS and Windows: build the zip + manifest, create a fixture repository whose `project.toml` pins the version, run the skeleton `tools/portal.py` with `PORTAL_BUNDLE=<zip>` and `--no-browser` against a local file server serving the manifest, poll `/api/health`, assert it serves that repo, stop it; plus a release-workflow dry run that stops before `gh release create` · **Why**: AC 2 without publishing; covers NFR-10 start on all OSes, no Node (`PATH` without node) · **Alternatives**: test only the zip layout (misses launcher contract) · **Confidence**: medium
- [Medium impact] Release workflow hardening — **Proposal**: tag must equal `v$(cat VERSION)` (exists), the tag commit must be an ancestor of `origin/main`, publish after building and verifying the zip against its own manifest, attach `agentic-portal-<version>.zip` and `manifest.json`, mark `0.*` as pre-release, never overwrite an existing release · **Why**: AC 1 wording "tag on main"; integrity · **Alternatives**: rely on convention · **Confidence**: medium
- [Medium impact] Launcher source of truth in CI — **Proposal**: the portal's CI vendors nothing; it checks out `agentic-skeleton` at the pinned tag (same pin as the contract tests of AP0104) to obtain `tools/portal.py` · **Why**: NFR-14 (no skeleton files modified locally), one pin for both uses · **Alternatives**: copy of the launcher in `scripts/` (violates NFR-14) · **Confidence**: medium
- [Medium impact] Contract mismatch (AC 3) — **Proposal**: verify at server level that `/api/health` and the version gate (AP0104) report `incompatible` for a fixture skeleton with another major, and that the manifest carries `contract_built_for`; the UI message itself is covered in AP0104/AP0108 · **Why**: avoids duplicating the logic · **Alternatives**: UI test here · **Confidence**: medium
- [Low impact] Zip hygiene — **Proposal**: keep the fixed timestamps, exclude tests/caches (exists), set explicit file modes, fail the build on entries failing the launcher's safe-name rules · **Confidence**: high
- [Low impact] Documentation — **Proposal**: a short "release procedure" section in `README`/`docs` (bump `VERSION`, tag, check release, update pins) · **Confidence**: high

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-20)

See `analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md` and the Refined Story. Owner decisions recorded there change §7 proposals; the rest stands.
