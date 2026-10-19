# BRIEF-AP0101 - Walking skeleton

## References
- Story ID: AP0101
- Source: `analysis/30-refined/REFINED_AP0101_walking_skeleton.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-19
- Captured by: Alberto Galimberti (with agent)
- Closed at (datetime): 2026-10-19T20:04:16Z

---

## Status
Refined into Spec

---

## Type
Feature

---

## Urgency (Optional)
Medium

---

# 1. Original Customer Intent

As a development team, I want a Python stdlib server on 127.0.0.1 serving a Vite/React page and GET /api/health, with build, tests and CI (GitHub Actions) that produce a release bundle zip with a manifest, so that every later story has its place ready and a runnable artifact exists from day one.

---

# 2. Initial Goal

A runnable, tested, releasable skeleton of the portal: loopback-only server, placeholder page showing the portal version, health endpoint, and a CI pipeline that builds the bundle and manifest and publishes the release.

---

# 3. Impact (Required for Hotfix)

n/a

---

# 4. Context

- Epic EP-01, Release R1, size M, Must. Requirements: NFR-01, NFR-08, NFR-09, NFR-14. ADR-003 (distribution).
- The first bundle may report skeleton and contract versions as "unknown"; AP0103 completes them. The page is a placeholder; the shell belongs to AP0108, the launcher to AP0106.
- Layout per `reference/architecture/architecture.md` §2 (`server/`, `web/`); health shape per §6 (already aligned with the workshop decision).
- Bundle and manifest format is shared with AP0106.

---

# 5. Known Constraints

- Loopback only; a non-loopback host option is refused (NFR-01).
- Backend stdlib only, Python >= 3.14; older Python exits with a clear message (NFR-08).
- Prebuilt frontend; the bundle runs without Node (NFR-09).
- No skeleton files modified locally (NFR-14).
- Release assets: `agentic-portal-<version>.zip` (`server/`, `web/dist/`, `VERSION`) plus `manifest.json` `{version, contract_built_for, python_min, assets:[{name, sha256}]}`.
- Dependency check: stdlib `ast` script allowing only `sys.stdlib_module_names` and local packages.
- CI: full pipeline on Linux; server tests and bundle start smoke test on macOS and Windows.

---

# 6. Expected Fix (Optional)

n/a

---

# 7. Open Questions

- Resolved in Addendum: release publication is part of this story.
- AWS infrastructure "to be decided later" vs ADR-003: not blocking while GitHub Releases is used.

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.  
> Add clarifications here.

### Addendum - 2026-10-19

- Source: Refined Story §6 (open technical point) and §3 (in scope: publishing from GitHub Actions)
- Clarification: publishing the release (tag, GitHub Release, manifest) is a task of this story, run by the owner's GitHub Actions pipeline on a version tag.
- Impact: Spec includes a release workflow; actual publication needs the owner's repository settings.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0101
- RUN: RUN-AP0101
