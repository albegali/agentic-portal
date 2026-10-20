# BRIEF-AP0103 - Upstream: --json envelope and JSON Schemas

## References
- Story ID: AP0103
- Source: `analysis/30-refined/REFINED_AP0103_upstream_json_envelope.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-19T21:35
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-20T10:00

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

As a portal (consumer of agentic-skeleton), I want the skeleton tools the portal reads (next, backlog, check, plan, journal, story chain) and `wf.py version` to emit a versioned --json envelope with published JSON Schemas, so that the portal reads state without parsing Markdown and can report skeleton and contract versions.

(Backlog wording: "a versioned --json envelope, an error envelope, `wf.py version --json`, `next_step.py --json` in the envelope, and published JSON Schemas for every contract 1.0 tool (next, backlog, check, plan, journal, story chain, version)".)

---

# 2. Initial Goal

Release contract 1.0 of the skeleton: envelope and error envelope, `wf.py version --json`, `next_step.py --json` wrapped in the envelope, and JSON Schemas for every contract 1.0 tool, with CI schema tests and a tagged release. Emitting `--json` for backlog, check, plan, journal and story chain is AP0109.

---

# 3. Impact (Required for Hotfix)

n/a

---

# 4. Context

- Delivered in the agentic-skeleton repository (NFR-14); AI implements and tags, human + AI review.
- ADR-002: semver on `contract`; same major accepted, minor ≥ built-for; minor only adds fields; subprocess calls only.
- Workshop 2026-10-19 (`analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md`): Story list kept; `wf.py version --json` added; error envelope; Python 3.14 baseline.
- Backlog split already applied: AP0103 = envelope, version, next, all v1.0 schemas, CI, tag; AP0109 = `--json` of the remaining tools.
- Only `next_step.py` has --json today.

---

# 5. Known Constraints

- Skeleton files change upstream only; no portal runtime dependency (NFR-14).
- JSON Schema 2020-12 under `schemas/`; `jsonschema` is a CI/test dependency only.
- Skeleton tools run on Python 3.14.
- Breaking output change bumps the contract major.
- Error envelope `{contract, tool, error:{code, message}}`, no `data`, non-zero exit; empty states are valid `data` with empty lists.

---

# 6. Expected Fix (Optional)

Envelope helper module, `wf.py version`, schemas for all seven v1.0 outputs, schema tests in skeleton CI, tagged release.

---

# 7. Open Questions

- Exact tool names for plan, journal and story chain (ADR-002: fixed in the Spec).
- Compatibility of the Python 3.14 baseline with existing workflow repos (not assessed).
- Skeleton repository state (existing tools, test setup, CI) not seen yet.

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.
> Add clarifications here.

---

# 9. Derived Artifacts

- Spec: SPEC-AP0103-upstream-json-envelope
- RUN: RUN-AP0103
- Code: agentic-skeleton commit 73c5f4c (`feat/contract-1.0-envelope`, merged into `main` as ad43875) + review fix branch `fix/tools-version-fresh-fixture`
