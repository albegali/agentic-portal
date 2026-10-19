---
artifact_type: analysis
us_id: STORY_AP0106
title: Upstream portal.py launcher and make portal
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0106_upstream_portal_launcher.md
  - reference/project-summary.md
related_references:
  - reference/product/functional-requirements.md#FR-23
  - reference/product/non-functional-requirements.md#NFR-09
  - reference/product/non-functional-requirements.md#NFR-10
  - reference/product/non-functional-requirements.md#NFR-14
  - reference/architecture/ADR-003-distribution.md
last_updated: 2026-10-19
---

# Analysis AP0106 - Upstream portal.py launcher and make portal

## 1. References

- ID: AP0106
- Source story: analysis/10-stories/STORY_AP0106_upstream_portal_launcher.md
- Roadmap phase: R1
- Sources used: project summary, Story, FR-23, NFR-09, NFR-10, NFR-14, ADR-003
- Missing sources: release manifest format; skeleton `project.toml` schema/Makefile; FR-24 text (cited by ADR-003, not provided); analysis of AP0101/AP0103

## 2. Original User Story

### Story text

As a portal (consumer of agentic-skeleton), I want tools/portal.py and the `make portal` target in the skeleton to download the pinned bundle, verify SHA-256, cache it in .portal/<version>/ and start it, so that every workflow repository can start the portal.

### Description

Epic EP-01 · Must · R1 · M · technical · FR-23, NFR-09, NFR-10, NFR-14 · Depends on: — · Delivered in the agentic-skeleton repository; portal pins the released skeleton version · Out of scope: bundle build (portal release pipeline).

## 3. Intent Understanding

### Functional goal

- One command starts the portal for the current repository, on any supported OS, using a pinned and verified release bundle.

### Actors involved

- Any developer/PO/analyst in a workflow repository; skeleton maintainers; the portal release pipeline (producer of bundle and manifest).

### Expected outcome

- First run downloads, verifies, caches and starts; later runs start from cache.

## 4. Information Classification

### Facts

- ADR-003 (accepted, owner-confirmed): `project.toml [portal] version`; zip from this repository's GitHub Releases into gitignored `.portal/<version>/`; SHA-256 against the release manifest; stdlib launcher runnable as `python tools/portal.py` without make; `PORTAL_BUNDLE=<path>` overrides download.
- Must run on macOS, Windows, Linux (NFR-10) and work without Node (NFR-09); no skeleton file modified locally (NFR-14).
- Release pipeline must exist before first use (ADR-003 consequences); here it is out of scope, and AP0101 only produces a zip in CI.
- `.portal/` in `.gitignore` via `make adopt` is a follow-up in ADR-003.

### Clarifications received

- Distribution decision confirmed by owner 2026-10-19.

## 5. Original Acceptance Criteria

- Given project.toml [portal] version set, when I run `make portal`, then the bundle is downloaded, verified, cached and started.
- Given a tampered download, when the checksum is compared, then launch aborts with a message.
- Given Windows without make, when I run `python tools/portal.py`, then the same happens.
- Given Python older than 3.14, when the launcher runs, then it stops and states the requirement.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- "Started": which port, is the URL printed, does the browser open, how does Ctrl+C stop it, what if one is already running for the repo?
- FR-23 acceptance hint "serves the UI for the current repo": how the launcher passes the repo root to the server.
- Interpretation: `[portal] version` is the portal bundle version, not the skeleton version; to confirm.

### Functional gaps

- No AC for: missing/invalid `[portal]` section, offline first run, cached run, unavailable release/version, `PORTAL_BUNDLE` override (in ADR, not in AC).
- Messages and exit codes are not specified.
- NFR-10 has no per-OS acceptance beyond the Windows AC.

### Technical gaps

- Release manifest shape and download URL convention (needs agreement with AP0101 producer).
- Trust model: checksum from the same origin protects against corruption, not a compromised release; accepted?
- Private repository or rate-limit authentication for GitHub Releases.
- Zip extraction safety (path traversal) and atomic cache population on interrupted download.
- Python ≥ 3.14 check must run on syntax-compatible code of the launcher itself.
- Compatibility between pinned portal version and installed skeleton contract (FR-27) at launch.

### Dependencies or ownership points to clarify

- Cannot be verified end-to-end until a published release exists (AP0101 / release pipeline, unowned).
- Skeleton repo delivery and tagging shared with AP0103.
- Chicken-and-egg: the portal pins a skeleton release containing the launcher that fetches the portal.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions: an answer from the PO / stakeholder is mandatory.

- [High impact] Who owns the release pipeline, and does it ship before this story? — same question as AP0101; AP0106 cannot be verified end to end without a published release.
- [High impact] What does the user see at launch: browser opened automatically or URL printed only; if a portal already runs for the repo, reuse it or fail? — user-visible behaviour.
- [Medium impact] Is a SHA-256 published in the same release enough, or are signed releases required? — risk acceptance: it detects corruption, not a compromised release.
- [Medium impact] Is the agentic-portal GitHub repository public? — a private repository forces tokens on every user.

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Download URL and manifest — **Proposal**: `https://github.com/<owner>/agentic-portal/releases/download/v<version>/<asset>`, manifest as proposed in AP0101; `<owner>/<repo>` overridable via `[portal] source` · **Why**: ADR-003 source; one manifest shared with AP0101 · **Confidence**: medium
- [High impact] Failure-path ACs — **Proposal**: add ACs: offline with no cache → message and exit 1; offline with cache → start from cache; missing `[portal] version` → message with how to set it; version not found → message; `PORTAL_BUNDLE=<path>` → no download, checksum verified if a manifest is present · **Why**: ADR-003 behaviours not covered by the ACs · **Confidence**: high
- [Medium impact] Start mechanics — **Proposal**: repo root = nearest directory with `project.toml`; launcher starts the cached server with `--repo <root>` and a port (default from architecture, else first free from 8765), prints the URL, stops on Ctrl+C · **Why**: FR-23 "serves the UI for the current repo" · **Confidence**: medium
- [Medium impact] Safe and atomic cache — **Proposal**: download to a temp file in `.portal/`, verify, extract to `.portal/<version>.tmp` rejecting absolute/`..` paths, then rename · **Why**: interrupted runs never leave a half cache · **Confidence**: high
- [Medium impact] Contract mismatch at launch — **Proposal**: the launcher does not check it; the portal shows it in Settings · **Why**: ADR-002 decision · **Confidence**: high
- [Low impact] Python check — **Proposal**: launcher syntax kept compatible with old Python so the "≥ 3.14 required" message is always reachable · **Confidence**: high
- [Low impact] Messages, exit codes, old caches — **Proposal**: exit 0 ok, 1 user/config error, 2 integrity error; no automatic cleanup in v1 · **Confidence**: medium

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-19)

See the Refined Story. Changes to §7 proposals: Browser opens automatically; a running portal is reused; checksum is enough; repository is public.
