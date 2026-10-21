# BRIEF-AP0107 - Release bundle for make portal

## References
- Story ID: AP0107
- Source: `analysis/30-refined/REFINED_AP0107_bundle_launcher.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-21T15:56
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-21T17:49

---

## Status
Closed

---

## Type
Technical

---

## Urgency (Optional)
High

---

# 1. Original Customer Intent

As a developer using the workflow, I want the portal release pipeline to publish a versioned bundle zip with SHA-256 manifest that the skeleton launcher starts, so that I get the portal with zero setup and no Node.

---

# 2. Initial Goal

Align the release artifact and the server with the released launcher (skeleton `tools/portal.py`): manifest format 1, `portal_server/` at the zip root, `--repo`, no reverse-DNS stall at bind. Prove the real chain (launcher → bundle → `/api/health`) in CI on Linux, macOS and Windows without Node, and harden the release workflow.

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Depends on AP0101 and AP0106 (Done); AP0102 and AP0104 are Done and ship in the same first release. AP0110 (launcher token) is not released yet: CI starts with `--no-browser` and checks health only.
- Current state: `scripts/build_bundle.py` writes the pre-launcher manifest (`file`, `python_min`, no `manifest`/`asset`/`size`) and a `server/` prefix inside the zip; `release.yml` publishes on any `v*` tag after only a `VERSION` match; `main` gained `--repo` in AP0104.
- Workshop 2026-10-20 decisions: manifest format 1 now; no `server/` prefix; `--repo`; `server_bind` override; CI job running the real launcher on three OSes; every iteration keeps the build green.
- Standing proposals accepted by default (Refined §4): launcher obtained by checking out agentic-skeleton at the pinned tag (same pin as AP0104); "incompatible" proven at server level; zip hygiene; release procedure doc.

---

# 5. Known Constraints

- ADR-003 (distribution), NFR-09 (no Node at runtime), NFR-10 (macOS/Windows/Linux), NFR-14 (no skeleton file edited here), NFR-08 (stdlib only at runtime).
- Launcher contract: `tools/README.md` "Portal launcher" (manifest format 1, safe-extraction rules, `PORTAL_BUNDLE`, `--repo`).
- Release pipeline owned by the owner on GitHub Actions; public repository; checksum without signing is accepted.
- Releases `0.x` are pre-releases until R1 closes (residual assumption, confirm at the first release).

---

# 6. Expected Fix (Optional)

`build_bundle.py` (format 1, layout, hygiene, safe-name check), `server_bind` override and `--repo` validation, CI job `launcher` on three OSes with the real launcher, hardened `release.yml`, release-procedure doc.

---

# 7. Open Questions

- Release scheme and republish policy: assumptions above, confirm at the first release.
- End-to-end first run with token waits for AP0110.

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.
> Add clarifications here.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0107
- RUN: RUN-AP0107
- PR: https://github.com/albegali/agentic-portal/pull/9
