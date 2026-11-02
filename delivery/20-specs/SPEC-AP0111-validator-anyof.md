# SPEC-AP0111 - Skeleton 1.25.1 upgrade: validator accepts anyOf

## References
- Story ID: AP0111 (statement: `analysis/10-stories/STORY_AP0111_validator_anyof.md`, not copied here)
- Brief: BRIEF-AP0111
- RUN: RUN-AP0111
- Requirements: NFR-14

---

## Status
In Progress

---

# 1. Goal

Skeleton 1.25.1 schemas load and validate in the portal. Cause: `gates.schema.json` (`data`) uses `anyOf`, which `SUPPORTED` in `validator.py` lacks, so `check_subset` raises `UnsupportedSchemaKeyword` and `test_contract_*` fail.

---

# 2. User / Business Value

Unblocks the 1.25.1 upgrade (PR #11) and the gates contract (AP0105).

---

# 3. Scope

Included:
- `anyOf` in `SUPPORTED`, the `check_subset` walk and `_check` (valid when at least one alternative has no errors).
- Validator tests; ADR-002 revision line and validator docstring.

Out of scope:
- Other keywords; changes to skeleton files or schemas.

---

# 4. Acceptance Criteria

- [x] AC1: the 1.25.1 schemas load (`check_subset` accepts `anyOf`, including nested alternatives) → test: `server/tests/test_contract_validator.py::SkeletonSchemasTest::test_every_schema_file_stays_inside_the_subset` (fails before the fix)
- [x] AC2: a value matching none of the `anyOf` alternatives is rejected, one or several matches pass → test: `server/tests/test_contract_validator.py::KeywordTest::test_any_of`
- [x] AC3: the rest of the subset is unchanged (`allOf`, `if`, `format` still raise) → test: `server/tests/test_contract_validator.py::KeywordTest::test_unsupported_keyword_raises_at_load`
- [x] AC4: recorded gates envelopes validate against `gates.schema.json` → test: `server/tests/test_contract_*` (full suite)

---

# 5. Tasks

- `TSK-AP0111-01` Tests first: `test_any_of`, move `anyOf` out of the unsupported list; confirm AC1/AC2 fail.
- `TSK-AP0111-02` Implement `anyOf` in `validator.py`.
- `TSK-AP0111-03` ADR-002 revision line; docstring.
- `TSK-AP0111-04` Gates, retitle PR #11 to AP0111.

---

# 6. Execution Boundaries

The agent is allowed to:
- Edit `server/portal_server/contract/validator.py`, `server/tests/test_contract_validator.py`, ADR-002 (revision line).

The agent is not allowed to:
- Edit skeleton files or `schemas/`; add keywords other than `anyOf`; amend the upgrade commit `87dc32d`.

---

# 7. Quality Gates

- [x] Full test suite green
- [x] Build and lint pass
- [x] App starts and the smoke path works (`make run`) — n/a, no runtime change (RUN §5 #2)
- [x] No public interface change (API, CLI, formats)
- [x] Release notes / advisories of each upgraded package read; breaking changes listed in the RUN — none (RUN §5 #2)
- [x] Lockfile diff limited to the intended packages (no lockfile change expected)

---

# 8. Stop Conditions

- none

---

# 9. Impacted Areas

- Code: `server/portal_server/contract/validator.py`
- Interfaces: none
- Domain: none
- UX: none
- Platforms / distribution: none
- Tests: `server/tests/test_contract_validator.py`
- Docs: ADR-002 revision line

---

# 10. Notes / Clarifications

- Owner decision: `project-journal/decisions/2026-11-02-validator-anyof.md`.

---

# 11. Final Reconciliation

Facts written by `/persist` before Done (no checkboxes):

- Reconciled at: 2026-11-02
- AC met: 4/4
- Tasks deferred: none
- Spec changes since Ready: none
- Reference docs updated: reference/architecture/ADR-002-skeleton-contract.md
---

## Revisions

---

## Gates
