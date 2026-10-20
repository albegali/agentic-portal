# BRIEF-AP0106 - Upstream: portal.py launcher and make portal

## References
- Story ID: AP0106
- Source: `analysis/30-refined/REFINED_AP0106_upstream_portal_launcher.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-20T11:00
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-20T16:00

---

## Status
Closed

---

## Type
Feature

---

## Urgency (Optional)
Medium

---

# 1. Original Customer Intent

As a portal (consumer of agentic-skeleton), I want tools/portal.py and the `make portal` target in the skeleton to download the pinned bundle, verify SHA-256, cache it in .portal/<version>/, start it and open the browser, so that every workflow repository can start the portal with one command.

---

# 2. Initial Goal

A stdlib launcher in the agentic-skeleton repository, plus the `make portal` target, that fetches the pinned portal release bundle, verifies it, caches it and starts it for the current repo.

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Delivered in the agentic-skeleton repository (NFR-14); the portal pins the released skeleton version.
- ADR-003: `[portal] version` in `project.toml`, gitignored `.portal/<version>/`, stdlib launcher runnable as `python tools/portal.py`, `PORTAL_BUNDLE=<path>` override.
- Requirements: FR-23, FR-24, NFR-09, NFR-10, NFR-14.
- Workshop 2026-10-19 decisions: browser opens automatically; an already running portal for the repo is opened; SHA-256 from the same release is enough.
- Standing defaults (Refined Story §4): URL `https://github.com/<owner>/agentic-portal/releases/download/v<version>/<asset>`, `<owner>/<repo>` overridable via `[portal] source`; download to temp, extract to `.portal/<version>.tmp` rejecting absolute/`..` paths, then rename; launcher syntax compatible with old Python; exit codes 0 ok, 1 user/config error, 2 integrity error.

---

# 5. Known Constraints

- Only in agentic-skeleton; stdlib only; no local modification of skeleton files in this repository.
- Repo root = nearest directory with `project.toml`; server started with `--repo <root>`; URL printed.
- Manifest format comes from AP0101 (release pipeline, out of scope here).
- Out of scope: bundle build and release pipeline, signed releases, contract-mismatch check at launch, automatic cache cleanup.

---

# 6. Expected Fix (Optional)

`tools/portal.py` (config, download, verify, atomic extract, start, browser, running-instance detection) and a `portal` Makefile target; tests per OS.

---

# 7. Open Questions

- How a running portal is detected (Spec decision).
- Default port: from architecture, else first free from 8765.
- ADR-003 may need revision ("AWS infrastructure later" vs GitHub Releases); not blocking, the launcher hides the source.
- End-to-end verification needs a published release from the AP0101 pipeline; sequence of first releases to define in the plan.

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.  
> Add clarifications here.

### Addendum - 2026-10-20

- Source: owner, chat (Spec review)
- Clarification: running-portal detection and manifest format left to the developer; launcher Python baseline stays >= 3.11 (AP0103); distribution stays on GitHub Releases.
- Impact: SPEC-AP0106 §3, AC4, AC8, §8, §10 updated; ADR-003 unchanged.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0106 (Done)
- RUN: RUN-AP0106 (Closed)
- Code: agentic-skeleton `tools/portal.py`, `tools/tests/test_portal.py`, tag `v1.1.0`
