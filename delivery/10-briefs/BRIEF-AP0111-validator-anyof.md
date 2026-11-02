# BRIEF-AP0111 - Skeleton 1.25.1 upgrade: validator accepts anyOf

## References
- Story ID: AP0111
- Source: `analysis/10-stories/STORY_AP0111_validator_anyof.md` · external tracker URL: n/a
- Captured at (datetime): 2026-11-02
- Captured by: Alberto Galimberti (owner decision `project-journal/decisions/2026-11-02-validator-anyof.md`)
- Closed at (datetime): 2026-11-02T22:37+01:00

---

## Status
Closed

---

## Type
Chore

---

## Urgency (Optional)
Medium

---

# 1. Original Customer Intent

"Widen the validator subset with anyOf (portal side); no upstream change." Scope: the 1.25.1 upgrade already on `chore/skeleton-1.25.1` plus the `anyOf` support and its tests.

---

# 2. Initial Goal

PR #11 (skeleton 1.25.1) passes CI: `schemas/gates.schema.json` uses `anyOf` in `data`, the only keyword outside the portal validator's subset.

---

# 4. Context

- `server/portal_server/contract/validator.py`: `SUPPORTED`, `check_subset`, `_check` (`oneOf` is the model).
- `server/tests/test_contract_validator.py::test_unsupported_keyword_raises_at_load` lists `{"anyOf": []}` as unsupported: it must change.
- ADR-002 revision 2026-10-20 defines the subset; `server/AGENTS.md` says not to widen silently: this is the owner-approved widening.

---

# 5. Known Constraints

- Same branch and PR #11 (retitle to AP0111); the upgrade commit and the fix commit stay separate.
- Standard library only at runtime; no change to skeleton files (NFR-14).

---

# 6. Expected Fix (Optional)

Add `anyOf` (at least one alternative matches) to the validator, tests, and an ADR-002 revision line.

---

# 7. Open Questions

- none

---

# 9. Derived Artifacts

- Spec: SPEC-AP0111
- RUN: RUN-AP0111
- PR: #11 (https://github.com/albegali/agentic-portal/pull/11)

---

## Revisions
