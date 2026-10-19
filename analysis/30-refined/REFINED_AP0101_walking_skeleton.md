---
artifact_type: refined
us_id: STORY_AP0101
title: Walking skeleton
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0101_walking_skeleton.md
  - analysis/20-analysis/ANALYSIS_AP0101_walking_skeleton.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md
related_references:
  - reference/product/non-functional-requirements.md#NFR-01
  - reference/product/non-functional-requirements.md#NFR-08
  - reference/product/non-functional-requirements.md#NFR-09
  - reference/architecture/ADR-003-distribution.md
last_updated: 2026-10-19
---

# Refined Story AP0101 - Walking skeleton

## 1. References

- ID: AP0101
- Title: Walking skeleton
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, NFR-01/08/09
- Missing sources: architecture.md §2 and §6 (layout, health shape) never read by the analyst; the health shape below supersedes §6 and the Brief must align them
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md

## 2. Refined User Story

### Refined story text

As a development team, I want a Python stdlib server on 127.0.0.1 serving a Vite/React page and GET /api/health, with build, tests and CI (GitHub Actions) that produce a release bundle zip with a manifest, so that every later story has its place ready and a runnable artifact exists from day one.

### Refined description

The first bundle may ship with skeleton and contract versions reported as "unknown"; AP0103 completes them. The first page is a placeholder showing the portal version from /api/health; the shell belongs to AP0108.

## 3. Scope

### In scope

- Server on loopback only, static page, /api/health; build, lint, tests; dependency check; CI producing zip + manifest; Python < 3.14 exits with a clear message.
- CI: full pipeline on Linux; server tests and bundle start smoke test on macOS and Windows.
- Publishing the release (tag, GitHub Release, manifest) from GitHub Actions; the owner owns the pipeline.

### Out of scope

- Domain features, authentication, app shell (AP0108), launcher (AP0106), AWS infrastructure.

## 4. Confirmed Information

### Facts

- Loopback only (NFR-01), stdlib-only runtime (NFR-08), runs without Node (NFR-09).
- Release pipeline owner: the project owner, on GitHub Actions.

### Decisions confirmed during refinement

- Health returns datetime and status, optionally error code and message, plus portal, contract and skeleton versions; skeleton/contract are "unknown" until AP0103 (owner override of the Analysis shape).
- Shipping health with "unknown" versions before AP0103 is accepted, provided AP0103 completes them.
- Not overridden, therefore standing: release assets `agentic-portal-<version>.zip` (`server/`, `web/dist/`, `VERSION`) plus `manifest.json` `{version, contract_built_for, python_min, assets:[{name, sha256}]}`; dependency check by an stdlib `ast` script allowing only `sys.stdlib_module_names` and local packages (test/lint tools are dev-only).

### Residual assumptions

- Exact JSON field names and the datetime format of the health response are left to the Spec.
- "Unknown" is represented as null or a literal string: Spec decision.

## 5. Confirmed Acceptance Criteria

- Given the cloned repository, when I run `make setup && make test`, then server and web tests pass.
- Given a merge on main, when the pipeline runs, then build, lint, tests are green and a bundle zip with SHA-256 and the manifest are produced.
- Given the server started from the bundle, when I open its URL without Node installed, then the page loads and /api/health returns datetime, status, and portal, contract and skeleton versions ("unknown" until AP0103).
- Given the dependency check in CI, when server/ imports a third-party package, then the pipeline fails.
- Given the server started, when its sockets are inspected, then it listens only on 127.0.0.1 and refuses a non-loopback host option (NFR-01).
- Given Python older than 3.14, when the server starts, then it exits with a message stating the requirement.

## 6. Remaining Open Points

### Functional

- None blocking.

### Technical

- Whether publishing to GitHub Releases is part of this story's tasks or a separate pipeline story; the Story AC only requires the zip. Not blocking: decide in the Brief.
- AWS infrastructure "to be decided later" vs ADR-003 (GitHub Releases): ADR-003 may need revision; not blocking while GitHub Releases is used (see AP0106).
- Align health shape with architecture.md §6 (update the document; owner approval for architecture changes).

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Server + loopback test; /api/health; placeholder page; web scaffold and tests.
- Dependency-check script; CI workflow (OS matrix, bundle, manifest, release publication).

### Boundaries to respect

- No shell or screens; no new runtime dependencies; skeleton files are not modified locally (NFR-14).
- Bundle and manifest format is shared with AP0106: do not change without it.

## 8. Refinement Outcome

- Story ready with residual open points to track
