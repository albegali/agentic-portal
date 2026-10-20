---
artifact_type: refined
us_id: STORY_AP0107
title: Release bundle for make portal
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0107_bundle_launcher.md
  - analysis/20-analysis/ANALYSIS_AP0107_bundle_launcher.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md
related_references:
  - reference/architecture/ADR-003-distribution.md
  - reference/product/functional-requirements.md#FR-23
  - reference/product/non-functional-requirements.md#NFR-09
  - reference/product/non-functional-requirements.md#NFR-10
last_updated: 2026-10-20
---

# Refined Story AP0107 - Release bundle for make portal

## 1. References

- ID: AP0107
- Title: Release bundle for make portal
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, ADRs listed above
- Missing sources: ci.yml, workflow-check.yml, architecture.md §2/§6, AP0106 Spec/RUN
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md

## 2. Refined User Story

### Refined story text

As a developer using the workflow, I want the portal release pipeline to publish a versioned bundle zip with SHA-256 manifest that the skeleton launcher starts, so that I get the portal with zero setup and no Node.

### Refined description

Aligns the artifact and the server with the released launcher (skeleton 1.1.x) and proves the real chain in CI on three operating systems.

## 3. Scope

### In scope

- Manifest format 1 now: `manifest`, `version`, `asset`, `size`, `sha256`, `requires_python` (+ `contract_built_for`, ignored extra).
- Zip root: `portal_server/`, `web/dist/`, `VERSION` (no `server/` prefix); entry names pass the launcher's safe-extraction rules; fixed timestamps, explicit modes.
- Server `--repo <path>` (default cwd, must contain `project.toml`), listed by `--help`; `server_bind` override without `getfqdn()`.
- CI job on Linux, macOS, Windows: build zip + manifest, fixture repo pinning the version, skeleton `tools/portal.py` with `PORTAL_BUNDLE`, `--no-browser`, poll `/api/health`, assert the repo is served, no Node on PATH; plus a release dry run before `gh release create`.
- Release hardening: tag = `v$(cat VERSION)`, tag commit ancestor of `origin/main`, verify zip against its manifest before publishing, `0.*` marked pre-release, no overwrite of an existing release.
- Short release-procedure section in the docs.

### Out of scope

- Launcher code (skeleton), token delivery (AP0110), auto-update.
- UI message for contract mismatch (AP0104/AP0108).

## 4. Confirmed Information

### Facts

- Launcher contract per `tools/README.md` (Portal launcher); current portal manifest and layout differ from format 1 and from the launcher's expectations.
- Release pipeline owned by the owner on GitHub Actions; public repository; checksum without signing is accepted.

### Decisions confirmed during refinement

- Manifest switches to format 1 now; drop the `server/` prefix; add `--repo`; `server_bind` override; CI job on Linux/macOS/Windows running the real launcher.
- The first release must be usable (including AP0102 and AP0104); every iteration keeps the build green.
- Implementation only through the AP0107 RUN, after the strategy is approved.
- Standing (proposal accepted by default): launcher obtained by checking out agentic-skeleton at the pinned tag (same pin as AP0104); AC 3 verified at server level (health and version gate report `incompatible` for a fixture with another major, manifest carries `contract_built_for`); zip hygiene; release procedure doc.

### Residual assumptions

- Release scheme `0.x` pre-releases until R1 closes, `1.0.0` at R1 (not answered in the minutes; low impact).
- NFR-10 browsers verified manually per release by the owner; CI covers start on the three OSes.

## 5. Confirmed Acceptance Criteria

- Given a tag on main whose commit is reachable from `origin/main`, when the release pipeline runs, then a GitHub Release with `agentic-portal-<version>.zip` and `manifest.json` (format 1) is published.
- Given the built bundle pinned in a fixture repository, when the real launcher runs on Linux, macOS and Windows without Node, then `/api/health` answers for that repository.
- Given the launcher starts the bundle with `--repo <root>`, when the server starts, then it serves that repository, `--help` lists `--repo`, and startup does not stall on reverse DNS.
- Given a fixture skeleton with another contract major, when the bundle runs, then health and the version gate report `incompatible`.
- Given a zip entry that fails the safe-name rules, when the bundle is built, then the build fails.

## 6. Remaining Open Points

### Functional

- None blocking.

### Technical

- End-to-end first run with token needs AP0110; until it is released, the CI job runs with `--no-browser` and health only.
- Release scheme and republish policy: assumptions above, confirm at the first release.

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Manifest and layout change in `build_bundle.py`; `find_static` follows the new layout; `--repo` and `server_bind`; CI cross-OS job; release workflow hardening; contract constant in the manifest; docs.

### Boundaries to respect

- No Node at runtime; no skeleton file edited (NFR-14); no code before an approved RUN strategy.

## 8. Refinement Outcome

- Story ready with residual open points to track
