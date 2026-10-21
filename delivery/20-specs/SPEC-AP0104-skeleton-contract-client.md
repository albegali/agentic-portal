# SPEC-AP0104 - Skeleton contract client

## References
- Story ID: AP0104
- Brief: BRIEF-AP0104
- RUN: RUN-AP0104

---

## Status
Done

---

# 1. Goal

The portal server reads all project state by calling the eight skeleton tools through the versioned `--json` envelope, validates every envelope at runtime, gates on the contract version, and reports incompatible, missing or older skeletons with a message and a recovery proposal while refusing data calls.

---

# 2. User / Business Value

As a portal server
I want to call skeleton tools through the versioned --json envelope, validate it and check the contract version
So that the portal never parses Markdown and detects incompatible, missing or older skeletons.

---

# 3. Scope

Included:
- **Runner** (`server/portal_server/contract/runner.py`): fixed table `tool name → argv` for `version`, `next`, `next-story`, `backlog`, `check`, `plan`, `journal`, `story`; `sys.executable`, argument list (no shell), cwd = repo root, 30 s timeout (process group killed), 5 MB output cap, env `PYTHONUTF8=1`. Returns `Ok(data)` or `ContractError(kind, message)`, kinds `incompatible`, `missing-tool`, `tool-error`, `bad-output`, `timeout`. Error envelope (non-zero exit, `error{code,message}`) → `tool-error`.
- **Validator** (`contract/validator.py`): stdlib validator of the JSON Schema 2020-12 subset used by `schemas/`: `$schema`/`$id`/`title`/`description` (ignored), `$ref` (local, `#/$defs/…` and sibling schema files by `$id`/filename), `$defs`, `type` (string or list), `properties`, `required`, `additionalProperties` (boolean or schema), `items` (schema), `const`, `enum`, `minLength`, `minimum`, `pattern`, `oneOf`, `not`. Any other keyword in a schema raises `UnsupportedSchemaKeyword` at load (an internal error, not a `ContractError`), so subset drift is caught by CI. Every envelope is checked against `envelope.schema.json` and the tool schema; violation → `bad-output`.
- **Version gate** (`contract/gate.py`): `tools/wf.py version --json` read once at start, re-read on Settings re-check and after a failed call; state `compatible | incompatible | missing`; compatible = same major and minor ≥ `CONTRACT_BUILT_FOR` (constant in `contract/__init__.py`, `1.0`); unknown extra fields tolerated, adapters check required keys.
- **Refusal**: while not `compatible`, every `/api` data route answers 409 `{"error":{"code":"contract_incompatible","message":…,"recovery":{…}}}`; `/api/health` and the Settings routes (state read, re-check) stay available behind the existing auth.
- **State and re-check API**: `GET /api/contract` (state, skeleton and contract versions, built-for, message, recovery proposal) and `POST /api/contract/recheck`.
- **Recovery proposal**: payload `{summary, steps[], command, runnable:false}` computed from the state (missing `tools/wf.py` → restore/re-checkout skeleton at `SKELETON_PIN`; major mismatch or lower minor → update/re-pin skeleton to the pinned tag). Proposal only: executing it through an agent run waits for the runs epic.
- **Health and manifest**: fill `contract` (`built_for`, `skeleton_contract`) and `skeleton` in `/api/health`, keeping existing fields (AP0101 contract, datetime/status); replace `contract_built_for: "unknown"` in `scripts/build_bundle.py` with the constant.
- **Fixtures and tests**: recorded envelopes of all eight tools in `server/tests/fixtures/envelopes/`; unit tests (runner kinds, validator subset, gate rules incl. extra fields and lower minor, 409 shape, health, recheck); route-enumeration test extended; contract tests (`jsonschema`, test-only) validating each recorded envelope and a live run against the pinned skeleton checkout.
- **CI**: job `contract` checking out agentic-skeleton at `SKELETON_PIN` (tag with AP0109 and AP0105 outputs) and running the contract tests; `scripts/check_deps.py` keeps `jsonschema` allowed in tests only.
- Docs: `server/AGENTS.md` (call API, error shapes), `architecture.md` §6 if present, ADR-002 untouched (revision already recorded).

Out of scope:
- Gate writes, run launching, executing the recovery through an agent run.
- Caching (hook point only: single call function, no cache).
- The Settings screen (UI) and showing the message outside Settings.
- Any skeleton file edit (NFR-14); AP0109 upstream emitters.

---

# 4. Acceptance Criteria

- [x] AC1: Given a recorded envelope of each of the eight tools, when the contract tests run, then each validates against its schema in the pinned skeleton checkout (CI job `contract`).
- [x] AC2: Given a skeleton whose contract major differs, or a lower minor, or no `tools/wf.py version`, when the portal starts, then `GET /api/contract` reports the incompatibility message and a recovery proposal, and data routes answer 409 `contract_incompatible`.
- [x] AC3: Given a compatible minor with unknown extra fields, when the portal reads it, then the call returns `Ok` and data routes work.
- [x] AC4: Given non-JSON output, a failing tool, output over 5 MB or a call over 30 s, when a call is made, then a typed `ContractError` (`bad-output`, `tool-error`, `bad-output`, `timeout`) is returned and the process is gone.
- [x] AC5: Given an envelope that violates its schema (missing required key, wrong type, wrong `tool`), when read at runtime, then it is rejected as `bad-output`.
- [x] AC6: Given Settings, when `POST /api/contract/recheck` runs after the skeleton is fixed, then the state is re-evaluated and data routes recover without restart.
- [x] AC7: Given `GET /api/health`, then `contract` and `skeleton` carry real values (or `unknown` when missing) and the bundle manifest carries the real `contract_built_for`.
- [x] AC8: Given every schema file in `schemas/`, when the validator loads it, then no keyword outside the supported subset is present (test fails otherwise).
- [x] AC9: Given `make test`, then the server has no third-party runtime import (`check_deps`), and `jsonschema` is imported only under `server/tests/`.

---

# 5. Tasks

- `TSK-AP0104-01` Runner, `Ok`/`ContractError`, tool table, subprocess policy (timeout, cap, process group, UTF-8) with tests.
- `TSK-AP0104-02` Stdlib schema validator for the declared subset, schema loader and subset-drift test against `schemas/`.
- `TSK-AP0104-03` Version gate, `CONTRACT_BUILT_FOR`, state machine (start, re-check, after failed call) and tests.
- `TSK-AP0104-04` 409 guard in `app.py`, `GET /api/contract`, `POST /api/contract/recheck`, recovery proposal payload, route-enumeration update.
- `TSK-AP0104-05` Health `contract`/`skeleton` fields and bundle manifest `contract_built_for` (scripts tests).
- `TSK-AP0104-06` Fixtures of recorded envelopes (eight tools) and contract tests with `jsonschema` (test-only), dependency check update.
- `TSK-AP0104-07` CI job `contract` at `SKELETON_PIN`; `make test` stays green without the pinned checkout (contract live tests skip with a clear reason locally, run in CI).
- `TSK-AP0104-08` Docs: `server/AGENTS.md` and reference updates; Spec reconciliation inputs for persist.

---

# 6. Execution Boundaries

The agent is allowed to:
- Edit `server/portal_server/` (new `contract/`, `app.py`, `health.py`), `server/tests/`, `scripts/build_bundle.py` and its tests, `scripts/check_deps.py`, `.github/workflows/ci.yml`, and the docs named in §9.

The agent is not allowed to:
- Edit skeleton files (`tools/`, `schemas/`, …): changes go upstream (NFR-14).
- Add third-party runtime dependencies (NFR-08).
- Add write routes, launch agent runs, or add caching.
- Change the AP0102 auth pipeline order or the health public exception beyond the new fields.

---

# 7. Quality Gates

- [x] Tests added/updated (`make test`)
- [x] Build passes (`make lint`, web build)
- [x] Public interfaces updated if impacted (`/api/contract`, 409 shape, health fields, manifest)
- [x] Domain invariants respected (ADR-002, NFR-08, NFR-13, NFR-14)
- [x] No breaking changes unless explicitly approved
- [x] CI job `contract` green at the pinned tag (PR #5)

---

# 8. Stop Conditions

Stop and ask for supervision if:
- acceptance criteria are ambiguous
- a breaking change is required (health contract, error shapes already used)
- security or permission rules are unclear (subprocess allow-list, recovery proposal commands)
- the pinned skeleton tag lacks AP0109/AP0105 outputs, or a schema uses a keyword outside the subset (needs skeleton change or a Spec update)
- work appears out of scope

---

# 9. Impacted Areas

- Code: `server/portal_server/contract/`, `app.py`, `health.py`; `scripts/build_bundle.py`, `scripts/check_deps.py`
- Interfaces (API, CLI, file formats, protocols, library API): `GET /api/contract`, `POST /api/contract/recheck`, 409 `contract_incompatible`, `/api/health`, bundle `manifest.json`
- Domain: n/a
- UX: none here (Settings screen consumes the state later)
- Platforms / distribution: subprocess and process-group handling on Windows; CI pin
- Tests: `server/tests/` (fixtures `envelopes/`), `scripts/tests/`
- Docs: `server/AGENTS.md`, `reference/architecture/architecture.md`

---

# 10. Notes / Clarifications

- Sources: `analysis/30-refined/REFINED_AP0104_skeleton_contract_client.md`, workshop 2026-10-20, ADR-002.
- `SKELETON_PIN` does not exist yet in the repository: TSK-07 defines it (CI variable and `project.toml` `[portal]` pin shared with AP0107).
- Validator subset above was derived from keyword counts in `schemas/` today; AC8 keeps it honest.

---

# 11. Final Reconciliation

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- Delivered `server/portal_server/contract/` (runner, stdlib validator, version gate, single `call`), the 409 `contract_incompatible` guard, `GET /api/contract`, `POST /api/contract/recheck`, health `contract`/`skeleton` and the bundle manifest constant. Fixtures recorded from the eight real emitters; contract tests with `jsonschema` (test-only) plus a live run; CI job `contract`.
- Deviation: the RUN stopped at Step 6 until the AP0109 emitters were upstream; the skeleton changes up to `d00c402` (1.3.0) were vendored into `tools/` + `schemas/` as an equivalent of merging `skeleton/main`. Tool table uses `tools/wf.py plan|journal|story <ID> --json`.
- `main` gained `--repo` (default cwd) so tool calls run at the repo root; a non-zero exit with a data envelope stays `Ok` (`check` reports problems that way).
- `SKELETON_PIN` = `d00c402bcac1b76d5adf5557359d1bbdee22a54d` (`project.toml [portal] skeleton_pin`, CI variable default); to become `v1.3.0` once the owner approves the upstream tag.

---

## Revisions
- 2026-10-20 — owner decision in chat (`/run AP0104 revise`): skeleton entry point is `tools/wf.py` (not a root `wf.py`); Spec text aligned, status stays `Ready`.
- 2026-10-21: `SKELETON_PIN` moved from d00c402 to tag `v1.3.0` (same commit), as planned in §10 once the tag existed. Source: project-journal/decisions/2026-10-21-close-open-points.md.
