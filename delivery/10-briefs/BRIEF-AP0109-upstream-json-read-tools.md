# BRIEF-AP0109 - Upstream: --json for backlog, check, plan, journal, story chain

## References
- Story ID: AP0109
- Source: `analysis/10-stories/STORY_AP0109_upstream_json_read_tools.md` (no Analysis or Refined Story: split from AP0103 at the workshop of 2026-10-19) · external tracker URL: n/a
- Captured at (datetime): 2026-10-20T21:46
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-20T22:03

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

As a portal (consumer of agentic-skeleton), I want the skeleton tools for backlog, check, plan, journal and story chain to emit the contract 1.x envelope against the schemas published by AP0103, so that the portal views read state without parsing Markdown.

---

# 2. Initial Goal

Finish the contract v1.0 surface in the skeleton: the five remaining read tools print the versioned envelope and validate against the schemas already shipped in `schemas/`; then tag the release.

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Delivered in the agentic-skeleton repository (NFR-14); AI implements and tags, human + AI review.
- ADR-002: tools `gen_backlog.py --json`, `check_workflow.py --json`, plan, journal and story chain `--json`; tool names `backlog`, `check`, `plan`, `journal`, `story`; empty states are valid `data` with empty lists.
- State after AP0103 (skeleton `tools/VERSION` 1.2.0, `CONTRACT_VERSION` 1.0): `backlog` and `check` still print the flat `"schema": 1`-style output through `wf.dump_json`; `plan`, `journal` and `story` have a schema but no emitter.
- Requirements: FR-25, NFR-13, NFR-14. Depends on AP0103 (done).
- Blocks the `v1.0.0` tag and AC5 of AP0103 (CI green on 3.11/3.14 plus tag); consumed by AP0104 (`SKELETON_PIN`) and the views AP0201–AP0205.

---

# 5. Known Constraints

- Only in agentic-skeleton; stdlib only; Python >= 3.11 for the tools; no local modification of skeleton files in this repository.
- Out of scope: write commands, context/repo_map/gates, schema changes beyond minor additions.

---

# 6. Expected Fix (Optional)

Wrap `backlog` and `check` in `wf.dump_envelope`/`fail_envelope`; add emitters for plan, journal and story chain (command names decided in the Spec); extend the contract tests with real tool output validated against each schema, including empty states; CI green; tag after human review.

---

# 7. Open Questions

- Command names and entry points for plan, journal and story chain (Spec decision).
- Whether the flat `backlog`/`check` shape is kept anywhere (consumers: `make backlog`, `make check` text output stay unchanged; only `--json` changes).

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.  
> Add clarifications here.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0109 (Done)
- RUN: RUN-AP0109 (Closed)
- Code: agentic-skeleton `tools/wf.py`, `tools/gen_backlog.py`, `tools/check_workflow.py`, `tools/tests/`, `tools/README.md`, `tools/VERSION` 1.3.0 (tag `v1.3.0` pending owner approval)
