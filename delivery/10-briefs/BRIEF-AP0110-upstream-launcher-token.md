# BRIEF-AP0110 - Upstream: launcher delivers the session token

## References
- Story ID: AP0110
- Source: `analysis/10-stories/STORY_AP0110_upstream_launcher_token.md` (no Refined Story: created by the workshop of 2026-10-20) · external tracker URL: n/a
- Captured at (datetime): 2026-10-20T15:00
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-20T17:00

---

## Status
Closed

---

## Type
Feature

---

## Urgency (Optional)
High

---

# 1. Original Customer Intent

As a portal (consumer of agentic-skeleton), I want tools/portal.py to generate the session token, store it in a user-only file in .portal/, pass it to the server as PORTAL_TOKEN and open the URL with #token=…, so that the browser authenticates on first open and a reused running portal opens the same session.

---

# 2. Initial Goal

Extend the skeleton launcher (AP0106) so the token is created, protected on disk, handed to the server and delivered to the browser through the URL fragment, including when an already running portal is reused.

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Delivered in the agentic-skeleton repository (NFR-14); AI implements and tags, human + AI review.
- ADR-006 revision 2026-10-20: token may live in a gitignored `.portal/` file readable only by the current user (POSIX 0600; Windows `icacls`, best effort with a warning); no encryption, no keyring (NFR-08); logs never contain it.
- Requirements: FR-23, NFR-02, NFR-14. Depends on AP0106 (launcher, `.portal/run.json`).
- Consumed by AP0102 (server reads `PORTAL_TOKEN`, `#token=` handling in the web client) and by the AP0107 CI job.
- Workshop 2026-10-20: owner chose to fix it now as an upstream story.

---

# 5. Known Constraints

- Only in agentic-skeleton; stdlib only; no local modification of skeleton files in this repository.
- Out of scope: server-side token checks (AP0102), bundle build (AP0107).

---

# 6. Expected Fix (Optional)

In `tools/portal.py`: generate a 256-bit token, write it to `.portal/` with restricted permissions, set `PORTAL_TOKEN` in the server environment, open `<url>/#token=<token>`; on reuse read the token from the file.

---

# 7. Open Questions

- Token file name and lifecycle (Spec decision).
- Release plan placement (PLAN.md S1 lists it; owner to confirm).

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.  
> Add clarifications here.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0110 (Done)
- RUN: RUN-AP0110 (Closed)
- Code: agentic-skeleton `tools/portal.py`, `tools/tests/test_portal.py`, `tools/README.md`
