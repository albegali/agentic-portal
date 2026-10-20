# RUN-AP0104

## References
- Story ID: AP0104
- Spec: SPEC-AP0104
- Started at (datetime): 2026-10-20 21:29
- Completed at (datetime): 2026-10-20 22:40

---

## Status
Closed

> A RUN MUST NOT be Closed before Persisted.

---

# 1. Execution Strategy (Agent)

### Required Reads
- [x] Target Spec
- [x] Scoped package `AGENTS.md` files, if applicable:
  - `server/AGENTS.md` (`web/AGENTS.md` not touched)
- [x] `delivery/templates/RUN-template.md`
- [x] ADR-002, `reference/architecture/architecture.md`, NFR-08/13/14

### Plan
Branch `ap0104-skeleton-contract-client` created before the first change. One verifiable step per task; `make test` + `make lint` after each.
- Step 1 (TSK-01): `contract/runner.py` — `Ok`/`ContractError`, fixed table tool → argv (`sys.executable tools/<script> --json`, cwd = repo root, no shell), 30 s timeout with process-group kill (POSIX `start_new_session`, Windows `CREATE_NEW_PROCESS_GROUP` + `taskkill /T`), 5 MB cap, `PYTHONUTF8=1`. Tests with a fake tool script (non-JSON, error envelope, oversize, sleep → timeout, process gone).
- Step 2 (TSK-02): `contract/validator.py` — stdlib subset validator + loader resolving `$ref` by `#/$defs` and sibling `$id`/filename; unknown keyword → `UnsupportedSchemaKeyword`. Tests per keyword; AC8 test loads every file in `schemas/`.
- Step 3 (TSK-03): `contract/__init__.py` (`CONTRACT_BUILT_FOR = "1.0"`), `contract/gate.py` (state `compatible|incompatible|missing`; same major and minor ≥ built-for; extra fields tolerated; read at start, on re-check, after a failed call). Single `call(tool, ...)` function (cache hook point, no cache). Every envelope validated against `envelope.schema.json` + tool schema → `bad-output`.
- Step 4 (TSK-04): `app.py` — 409 `contract_incompatible` guard on every `/api` data route (health and `/api/contract*` exempt, still behind auth), `GET /api/contract`, `POST /api/contract/recheck`, recovery payload `{summary, steps[], command, runnable:false}`. Route-enumeration test (AP0102) and a test per new route extended; auth pipeline order untouched.
- Step 5 (TSK-05): `health.py` fills `contract` (`built_for`, `skeleton_contract`) and `skeleton`; `scripts/build_bundle.py` manifest uses the constant. Existing health fields kept.
- Step 6 (TSK-06): recorded envelopes of the eight tools in `server/tests/fixtures/envelopes/`; contract tests with `jsonschema` (test-only) + live run against the skeleton checkout (skip with reason if absent); `scripts/check_deps.py` allows `jsonschema` under `server/tests/` only.
- Step 7 (TSK-07): `SKELETON_PIN` (CI variable + `project.toml [portal]` pin), CI job `contract` checking out agentic-skeleton at the pin; `make test` green locally without it.
- Step 8 (TSK-08): `server/AGENTS.md` (call API, error shapes), `architecture.md` §6, notes for Spec reconciliation.

### Assumptions
- The skeleton ships in this repo's `tools/` (1.2.0, contract 1.0); entry point is `tools/wf.py`. Owner decision 2026-10-20: Spec aligned to `tools/wf.py` (revision line added, status stays `Ready`).
- Owner decision 2026-10-20: the missing `--json` emitters (`plan`, `journal`, `story`, envelope form of `check`/`backlog`) are anticipated, delivered upstream (NFR-14) before AP0104 needs them, not left to AP0109 timing. AP0104 does not write them: it consumes them. Fixtures are recorded from real emitter output, not hand-built; the live test covers all eight tools.
- Python ≥ 3.14 on the server; `http.server` handler stays synchronous, gate state held in a lock-protected object.

### Risks / Open Questions
- **Pinned tag**: owner OK; `SKELETON_PIN` takes the value the upstream emitters ship under (tag if available, else a commit SHA), recorded in TSK-07.
- **Emitters dependency (blocking for Steps 6-7)**: Steps 1-5 need no emitter. Before Step 6 the upstream emitters must exist at the pin. If not, stop per Spec §8 and report; I will not build them in this repo. Release plan: AP0109 emitters need to move ahead of AP0104 Step 6 in `PLAN.md` (human artifact, not changed by me).
- Windows: owner OK; process-group kill is covered by the code branch and the CI `cross-platform` job only.
- A schema using a keyword outside the subset → stop (skeleton change or Spec update). Current keyword scan of `schemas/` shows only the subset.

### Scoped Agent Rules Check
- Applies: Yes
- Files read:
  - `server/AGENTS.md`
- Notes:
  - Argument lists only, own process group, timeouts; every new route gets a test and goes through auth + Host/Origin; no third-party runtime imports; `pathlib`, Windows branch for process handling.

---

# 2. Human Approval

- [x] Strategy reviewed
- [x] Scope correctly understood
- [x] No out-of-scope work detected

Decision:
- [x] Approved
- [ ] Revisions requested
- [ ] Stopped

Notes:
-

Reviewer: Alberto Galimberti
Date: 2026-10-20

---

# 3. Execution Log (Agent)

- Branch `ap0104-skeleton-contract-client` created from main before the first change.
- Step 1 (TSK-01) done: `contract/runner.py` (`Ok`/`ContractError`, tool table, process group kill, 5 MB cap, 30 s, `PYTHONUTF8=1`); tests `test_contract_runner.py`. A non-zero exit with a data envelope stays `Ok` (`check` reports problems that way); the decision is by envelope shape.
- Step 2 (TSK-02) done: `contract/validator.py` (subset, `$ref` local/sibling, `UnsupportedSchemaKeyword`), AC8 test over `schemas/`.
- Step 3 (TSK-03) done: `CONTRACT_BUILT_FOR`, `contract/gate.py` (state, refresh at start/re-check/after failed call, single `call`, per-root registry).
- Step 4 (TSK-04) done: `app.py` 409 guard, `GET /api/contract`, `POST /api/contract/recheck`, recovery payload; `--repo` option added to `main` (default cwd) so cwd of tool calls is the repo root; routes may return `(status, body)`. `tests/support.py` builds a fake compatible skeleton; `test_security.py` setUp uses it.
- Step 5 (TSK-05) done: health `contract` `{built_for, skeleton_contract}` and `skeleton`, existing `contract_version`/`skeleton_version` kept and now real (`unknown` when missing); manifest uses the constant.
- Step 6 (TSK-06) done after the block (§6): emitters landed upstream (`skeleton/main` d00c402, skeleton 1.3.0). Skeleton changes since the merge base vendored into `tools/` + `schemas/` (uncommitted, via patch, equivalent to merging `skeleton/main`; includes the AP0110 launcher changes). Tool table aligned to upstream: `tools/wf.py plan|journal|story <ID> --json`. Fixtures in `server/tests/fixtures/envelopes/` recorded from the eight real emitters; `test_contract_fixtures.py` (recorded + `jsonschema` agreement + live run, `SKELETON_DIR` override); `check_deps.py` allows `jsonschema`/`referencing` under `tests/` only (+ test).
- Step 7 (TSK-07) done: `SKELETON_PIN` = d00c402bcac1b76d5adf5557359d1bbdee22a54d (tag v1.3.0 pending upstream) in `project.toml [portal] skeleton_pin` and as default of CI variable `SKELETON_PIN`; CI job `contract` (checkout of agentic-skeleton at the pin, `pip install jsonschema`, `WF_REQUIRE_JSONSCHEMA=1`). `make test` is green locally without it.
- Step 8 (TSK-08) done: `server/AGENTS.md` (call API, error kinds), `architecture.md` §6 and §8.

---

# 4. Verification

Final (python3.14): `unittest discover -s server/tests` 77 OK (2 skipped: pre-existing + jsonschema absent locally; the agreement test ran green with jsonschema 4.26 on 3.12), `check_deps server` OK, `scripts/tests` OK, `compileall` OK, `make check` OK, live run of the eight tools green against this repo and against `../agentic-skeleton`. CI job `contract` and the web checks (web untouched) not run locally.

After step 5 (partial): `unittest discover -s server/tests` 73 OK (1 skipped, pre-existing), `scripts/tests` OK, `check_deps` OK, `compileall` OK. Web build/tests not run (web untouched). Full verification at the end.

---

# 5. Tuning Log (If needed)

---

# 6. Deviations

- What changed: Steps 6-7 cannot proceed. `skeleton/main` (fetched 2026-10-20, `tools/VERSION` 1.2.0, tags v1.1.0, v1.1.1) has no emitter for `plan`, `journal`, `story`, and `check`/`backlog` still print the flat `"schema": 1` form. The runner table names them provisionally (`tools/plan.py`, `tools/journal.py`, `tools/story.py <ID>`): upstream may choose other names.
- Why: precondition of the approved strategy (emitters upstream before Step 6; Spec §8 stop condition).
- Scope impact: Requires approval — the owner must say how to proceed (emitters upstream first, or narrow TSK-06/AC1 to the tools that emit today).
- 2026-10-20 — owner decision in chat: option 1, the emitters go upstream first (agentic-skeleton); the RUN resumes at Step 6 with `/run AP0104` once they are on `skeleton/main`, aligning the tool table to the upstream names.

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- Spec §4, §7, §11 reconciled, status Done, index row set to Done. Reference docs touched: `architecture.md` §6/§8, `server/AGENTS.md` (done in Step 8). ADR-002 untouched.
- Tuning: none needed.

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied
- [x] Tests passing (77 locally on 3.14, 2 skipped; `make check` OK; CI green on PR #5 incl. `contract`)
- [x] No scope creep
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0104-01 to TSK-AP0104-08

Tasks deferred:
- none

Goal achieved:
- [x] Yes
- [ ] Partial
- [ ] No

Summary:
- The portal server calls the eight skeleton tools through the validated `--json` envelope, gates on the contract version and refuses data routes with a recovery proposal when incompatible.

---

# 10. Next Steps

- Follow-ups: owner approves tag `v1.3.0` in agentic-skeleton, then `SKELETON_PIN` moves from the SHA to `v1.3.0`. Next: AP0105 and the screens consume `contract.call`.
- Risks: until the tag exists the pin is a commit SHA.
- Improvements: none.

---

# 11. Addendum (Post-Closure Only)
