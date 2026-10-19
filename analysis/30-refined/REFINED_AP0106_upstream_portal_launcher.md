---
artifact_type: refined
us_id: STORY_AP0106
title: Upstream portal.py launcher and make portal
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0106_upstream_portal_launcher.md
  - analysis/20-analysis/ANALYSIS_AP0106_upstream_portal_launcher.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md
related_references:
  - reference/architecture/ADR-003-distribution.md
  - reference/product/functional-requirements.md#FR-23
  - reference/product/non-functional-requirements.md#NFR-09
  - reference/product/non-functional-requirements.md#NFR-10
  - reference/product/non-functional-requirements.md#NFR-14
last_updated: 2026-10-19
---

# Refined Story AP0106 - Upstream portal.py launcher and make portal

## 1. References

- ID: AP0106
- Title: Upstream portal.py launcher and make portal
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, ADR-003
- Missing sources: FR-24 text, skeleton `project.toml`/Makefile, final manifest format (defined in AP0101)
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md

## 2. Refined User Story

### Refined story text

As a portal (consumer of agentic-skeleton), I want tools/portal.py and the `make portal` target in the skeleton to download the pinned bundle, verify SHA-256, cache it in .portal/<version>/, start it and open the browser, so that every workflow repository can start the portal with one command.

### Refined description

Delivered in the agentic-skeleton repository. Python 3.14 runs the launcher like the portal and the skeleton tools.

## 3. Scope

### In scope

- Download from GitHub Releases, SHA-256 check against the manifest (checksum is enough, no signing), safe and atomic cache, start, automatic browser opening, Ctrl+C stop.
- If a portal is already running for the repo, open the running one.
- Failure paths and `PORTAL_BUNDLE=<path>` override (see AC).
- Repo root = nearest directory with `project.toml`; server started with `--repo <root>`; URL printed.

### Out of scope

- Bundle build and release pipeline (AP0101); signed releases; contract-mismatch check at launch (shown in Settings); automatic cleanup of old caches.

## 4. Confirmed Information

### Facts

- agentic-portal is a public repository: no token needed.
- Release pipeline: owned by the owner, GitHub Actions.
- ADR-003 behaviour: `[portal] version`, gitignored `.portal/<version>/`, stdlib launcher runnable as `python tools/portal.py`.

### Decisions confirmed during refinement

- `make portal` opens the browser automatically; an already running portal for the repo is opened instead of starting another.
- SHA-256 from the same release is sufficient.
- Not overridden, therefore standing: URL `https://github.com/<owner>/agentic-portal/releases/download/v<version>/<asset>` with `<owner>/<repo>` overridable via `[portal] source`; temp download then extract to `.portal/<version>.tmp` rejecting absolute/`..` paths, then rename; launcher syntax compatible with old Python so the requirement message is reachable; exit codes 0 ok, 1 user/config error, 2 integrity error.

### Residual assumptions

- `[portal] version` is the portal bundle version.
- Port: default from architecture, else first free from 8765. How a running portal is detected is a Spec decision.

## 5. Confirmed Acceptance Criteria

- Given project.toml [portal] version set, when I run `make portal`, then the bundle is downloaded, verified, cached, started and the browser opens.
- Given a tampered download, when the checksum is compared, then launch aborts with a message and exit code 2.
- Given Windows without make, when I run `python tools/portal.py`, then the same happens.
- Given Python older than 3.14, when the launcher runs, then it stops and states the requirement.
- Given no network and no cache, when I run the launcher, then it prints a message and exits 1; with a cache it starts from the cache.
- Given a missing `[portal] version` or a version not found, when I run the launcher, then it prints how to fix it and exits 1.
- Given `PORTAL_BUNDLE=<path>`, when I run the launcher, then nothing is downloaded and the checksum is verified if a manifest is present.
- Given a portal already running for the repo, when I run `make portal`, then the running one is opened.

## 6. Remaining Open Points

### Functional

- None blocking.

### Technical

- "AWS infrastructure to be decided later" vs ADR-003 (GitHub Releases, owner-confirmed): ADR-003 may need revision. The launcher hides the source (reversibility), so AP0106 can proceed on GitHub Releases. Not blocking.
- End-to-end verification needs a published release from the AP0101 pipeline.
- Chicken-and-egg: the portal pins a skeleton release that contains the launcher fetching the portal; sequence of first releases to define in the plan.

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Launcher (config, download, verify, atomic extract, start, browser, running-instance detection); Makefile target; tests per OS; ACs for failure paths.

### Boundaries to respect

- Only in agentic-skeleton; stdlib only; no local modification of skeleton files in the portal repo (NFR-14).
- Manifest format comes from AP0101.

## 8. Refinement Outcome

- Story ready with residual open points to track
