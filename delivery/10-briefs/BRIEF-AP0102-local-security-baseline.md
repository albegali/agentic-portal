# BRIEF-AP0102 - Local security baseline

## References
- Story ID: AP0102
- Source: `analysis/30-refined/REFINED_AP0102_local_security_baseline.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-20T18:00
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-20T19:10

---

## Status
Closed

---

## Type
NFR

---

## Urgency (Optional)
Medium

---

# 1. Original Customer Intent

As a owner at the machine, I want loopback-only binding, a per-session token, Host/Origin checks and CSRF protection on every API route, so that no other process or web page can read or change my repository through the portal.

---

# 2. Initial Goal

Server and web-client side of the local security model (ADR-006): loopback bind, token on every `/api` route except health, Host/Origin/content-type checks, write-scope guard, and a web token module (fragment → `sessionStorage` → bearer header).

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Depends on AP0101 (walking skeleton, Done). AP0108 shell is Done; the 401 message styling stays with it.
- Token delivery by the launcher and the token file writing are upstream (AP0110, not yet in the plan); this story only consumes `PORTAL_TOKEN` and reads the token file for reuse.
- Workshop 2026-10-20 decisions: token in a gitignored `.portal/` file (0600 / `icacls`); `/api/health` unauthenticated; middleware order Host → token → Origin/content type; SSE via `fetch` with bearer header.

---

# 5. Known Constraints

- Python standard library only (NFR-08); no keyring or crypto library.
- NFR-01, NFR-02, NFR-03; ADR-006 (revised 2026-10-20).
- No write route exists yet; no skeleton file edited here.
- Token never logged and never in a URL other than the launch fragment.

---

# 6. Expected Fix (Optional)

Middleware in `server/portal_server/http/`, `safe_path`/`write_guard` helper, `web/src/api/` token module, tests including route enumeration.

---

# 7. Open Questions

- Placement of AP0110 in S1/S2 (PO decision, PLAN.md); not blocking this story.

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.  
> Add clarifications here.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0102
- RUN: RUN-AP0102
