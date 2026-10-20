# BRIEF-AP0104 - Skeleton contract client

## References
- Story ID: AP0104
- Source: `analysis/30-refined/REFINED_AP0104_skeleton_contract_client.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-20T20:00
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-20T22:40

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

As a portal server, I want to call skeleton tools through the versioned --json envelope, validate it against the JSON Schemas and check the contract version, so that the portal never parses Markdown and detects incompatible, missing or older skeletons.

---

# 2. Initial Goal

Portal-side contract client (ADR-002): subprocess runner with typed errors, runtime validation with a small stdlib validator, version gate with 409 `contract_incompatible` and a recovery proposal, `/api/health` and bundle manifest filled, contract tests for the eight tools in CI against the pinned skeleton tag.

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Depends on AP0101 and AP0103 (Done). Sprint order AP0109 → AP0104 (workshop 2026-10-20): `backlog`/`check` are still flat and `plan`, `journal`, `story` have no emitter until AP0109 is delivered upstream.
- Consumers: AP0105, AP0201–AP0203 and the screens rely on the call API and error shapes defined here.
- Workshop 2026-10-20 decisions: runtime stdlib validator (ADR-002 revision), one L story, message + refused data calls + manageable Settings + recovery proposal, all eight tools under contract tests.

---

# 5. Known Constraints

- Python standard library only at runtime (NFR-08); `jsonschema` test-only.
- NFR-13 (contract tests in CI), NFR-14 (no skeleton file edited locally), FR-25, FR-27.
- Mismatch is shown only in Settings (ADR-002); the API exposes the state.
- Unknown keys are ignored; a lower minor than built-for is incompatible.

---

# 6. Expected Fix (Optional)

New `server/portal_server/contract/` (runner, validator, version gate), 409 guard in `app.py`, health and manifest fields, fixtures of recorded envelopes, CI contract job at `SKELETON_PIN`.

---

# 7. Open Questions

- Exact recovery steps and which part waits for the runs epic (Spec decides: detection, message and proposal ship here).
- Pinned skeleton tag must include AP0109 and AP0105 outputs for the full contract test set.

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.  
> Add clarifications here.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0104 (Done)
- RUN: RUN-AP0104 (Closed)
- Code: `server/portal_server/contract/`, `server/portal_server/app.py`, `health.py`, `scripts/build_bundle.py`, `scripts/check_deps.py`, `server/tests/` (fixtures `envelopes/`), CI job `contract`, `SKELETON_PIN` in `project.toml [portal]`
