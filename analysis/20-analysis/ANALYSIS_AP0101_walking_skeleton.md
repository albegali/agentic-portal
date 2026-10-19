---
artifact_type: analysis
us_id: STORY_AP0101
title: Walking skeleton
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0101_walking_skeleton.md
  - reference/project-summary.md
related_references:
  - reference/product/non-functional-requirements.md#NFR-01
  - reference/product/non-functional-requirements.md#NFR-08
  - reference/product/non-functional-requirements.md#NFR-09
last_updated: 2026-10-19
---

# Analysis AP0101 - Walking skeleton

## 1. References

- ID: AP0101
- Source story: analysis/10-stories/STORY_AP0101_walking_skeleton.md
- Roadmap phase: R1
- Sources used: project summary, Story, NFR-01, NFR-08, NFR-09
- Missing sources: architecture.md §2 (layout) and §6 (health shape) cited by the Story but not provided in this context; no PLAN.md sprint view; no analysis of AP0103/AP0106 (dependencies unknown)

## 2. Original User Story

### Story text

As a development team, I want a Python stdlib server on 127.0.0.1 serving a Vite/React page and GET /api/health, with build, tests and CI that produce a release bundle zip, so that every later story has its place ready and a runnable artifact exists from day one.

### Description

Epic EP-01 · Must · R1 · M · technical · Requirements NFR-01, NFR-08, NFR-09 · Depends on: — · Out of scope: domain features, authentication.

## 3. Intent Understanding

### Functional goal

- Provide the runnable foundation: server, static page, health endpoint, build/test/CI, and a downloadable release bundle.

### Actors involved

- Development team (primary); indirectly every later story and the launcher (AP0106) that consumes the bundle.

### Expected outcome

- A zip with SHA-256 that runs without Node and shows the page and a health response with portal, contract and skeleton versions.

## 4. Information Classification

### Facts

- Server binds only to loopback (NFR-01, test + port scan); backend stdlib only, 0 runtime deps, checked in CI (NFR-08); prebuilt static bundle, `make portal` works without Node (NFR-09).
- Stack: Python ≥ 3.14 stdlib + React/Vite/TS (project summary).
- Health must return portal, contract and skeleton versions (AC 3).
- Authentication and domain features are out of scope.

### Clarifications received

- None specific to this story.

## 5. Original Acceptance Criteria

- Given the cloned repository, when I run `make setup && make test`, then server and web tests pass.
- Given a merge on main, when the pipeline runs, then build, lint, tests are green and a bundle zip with SHA-256 is produced.
- Given the server started from the bundle, when I open its URL without Node installed, then the page loads and /api/health returns portal, contract and skeleton versions.
- Given the dependency check in CI, when server/ imports a third-party package, then the pipeline fails.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- "Skeleton version" and "contract" in /api/health: from where does the server obtain them at this stage (no skeleton tool exists yet; `wf.py version` is in AP0103's upstream scope, not a dependency of this story)? Interpretation: placeholder/"unknown" until AP0103 lands.
- "Page loads": what content is expected (blank placeholder vs. shell)? Overlap with AP0108 to be delimited.

### Functional gaps

- NFR-01 (loopback only, port scan) has no acceptance criterion although it is a cited requirement.
- Port selection, port-in-use behaviour and who opens the browser are unspecified.
- Windows/macOS/Linux build or test coverage (NFR-10) not mentioned in CI.

### Technical gaps

- Bundle composition and release manifest format (SHA-256 file name/shape) are not defined, yet AP0106 must consume them.
- AC 2 says the pipeline *produces* a zip; publication to GitHub Releases (ADR-003) is neither in this story nor in AP0106 (out of scope there) — the release pipeline looks unowned.
- Dependency check: how are "third-party imports" detected with stdlib only (AST/import allowlist)? Dev-only tools (pytest, linters) vs. runtime scope of NFR-08.
- Python ≥ 3.14 in CI and for contributors; what happens on older Python at runtime.

### Dependencies or ownership points to clarify

- Health endpoint versions depend on AP0103 (skeleton version) though "Depends on: —"; confirm ordering or placeholder.
- AP0106 and AP0108 depend on the bundle/layout produced here.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions: an answer from the PO / stakeholder is mandatory.

- [High impact] Who owns publishing releases (tag, GitHub Release, manifest)? — AP0101 only builds a zip, AP0106 excludes the pipeline; no project can start the portal until someone owns it. Shared with AP0106.
- [High impact] May the first bundle ship with health reporting skeleton/contract as "unknown" until AP0103 is released, or must AP0101 wait for AP0103? — decides sprint ordering across two repositories.

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Bundle and manifest format — **Proposal**: release assets `agentic-portal-<version>.zip` (`server/`, `web/dist/`, `VERSION`) plus `manifest.json` `{version, contract_built_for, python_min, assets:[{name, sha256}]}`; CI attaches both to the release · **Why**: ADR-003 requires SHA-256 against a release manifest; one file serves AP0106 and future integrity checks · **Alternatives**: plain `.sha256` sidecar (simpler, no metadata) · **Confidence**: medium
- [High impact] Health shape before the contract exists — **Proposal**: `{"status":"ok","portal":"x.y.z","contract":{"built_for":"1.0","skeleton":null},"skeleton":null}`, nulls filled from `wf.py version --json` once AP0103 ships · **Why**: AC 3 stays testable now; ADR-002 names `wf.py version` as the source · **Alternatives**: block on AP0103 · **Confidence**: medium (architecture.md §6 not read; align if it differs)
- [Medium impact] NFR-01 has no AC — **Proposal**: add "Given the server started, when its sockets are inspected, then it listens only on 127.0.0.1 and refuses a non-loopback host option" · **Why**: NFR-01 is Must with test verification · **Alternatives**: rely on review · **Confidence**: high
- [Medium impact] Dependency check — **Proposal**: stdlib script parsing `server/` with `ast`, allowing only `sys.stdlib_module_names` and local packages; test/lint tools live in dev requirements never imported by `server/` · **Why**: NFR-08 targets runtime deps · **Alternatives**: pip-based scan (needs install) · **Confidence**: high
- [Medium impact] CI OS matrix (NFR-10) — **Proposal**: full pipeline on Linux; server tests + bundle start smoke test on macOS and Windows · **Why**: catches path/encoding issues early at low cost · **Alternatives**: defer to AP0106 · **Confidence**: medium
- [Low impact] Python version at start — **Proposal**: server exits with a clear message if `sys.version_info < (3, 14)` · **Why**: same rule as the launcher · **Confidence**: high
- [Low impact] First page content — **Proposal**: static placeholder showing the portal version read from /api/health; the shell is AP0108 · **Why**: avoids overlap · **Confidence**: high

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-19)

See the Refined Story. Changes to §7 proposals: Health returns datetime and status, optionally error code and message, plus portal, contract and skeleton versions; release pipeline owned by the owner on GitHub Actions.
