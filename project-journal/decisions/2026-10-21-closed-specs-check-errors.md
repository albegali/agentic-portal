# Decision Record

## Status

Accepted

## Owner's words

> "2. fix this as you prefer"

Alberto Galimberti, chat, 2026-10-21, answering the two `make check` errors raised after the skeleton 1.17.1 upgrade
(SPEC-AP0101 Done with unchecked AC2/AC7; SPEC-AP0103 Done with unchecked quality gates).

## Context

Skeleton 1.17.1 checks that a `Done` Spec has no unchecked acceptance criterion or quality gate. Two Specs closed under
skeleton 1.3.0 fail it: their boxes were left unticked at closure, pending facts that happened later or not at all.

## Decision

Record the facts as they stand on 2026-10-21, with the evidence; nothing is ticked without it.
- SPEC-AP0101 AC2: met (CI on `main`). AC7: still open, deferred to the owner's `v0.1.0` tag, tracked in RUN-AP0101
  `## Pending owner actions`; RUN-AP0101 Goal achieved corrected from `Yes` to `Partial`.
- SPEC-AP0103 §7: all five gates met (agentic-skeleton CI and tests at the AP0103 merge).

## Rationale

Ticking boxes without evidence would make the Specs claim what the check exists to catch; reopening the stories would
redo delivered work. Recording verified facts and the one open owner action keeps both honest.

## Alternatives Considered

- Tag `v0.1.0` now to close AC7: a release is an owner action (AGENTS.md, RUN template), not the agent's.
- Reopen AP0101/AP0103: no code change is needed.

## Consequences

`make check` is green; `make next` lists the `v0.1.0` tag as a pending owner action until it is done.

## Links

- delivery/20-specs/SPEC-AP0101-walking-skeleton.md, delivery/30-runs/RUN-AP0101.md
- delivery/20-specs/SPEC-AP0103-upstream-json-envelope.md
- CI run https://github.com/albegali/agentic-portal/actions/runs/39490675830 (`main` 0525bca, artifact `portal-bundle`)
- agentic-skeleton `8b2dd71` (AP0103 merge), CI on `ad43875` (Python 3.11, 3.14)
