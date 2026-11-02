# Decision Record

## Status

Accepted

## Owner's words

> "Owner decision: fix upstream; no rebase, no force-push. The skeleton will exempt skeleton-sync commits in check_approval_order (release 1.25.2). Record this decision. Leave PR #11 as it is and commit only the pending RUN/Spec edits. When 1.25.2 is out I'll tell you to run make sync-skeleton and then /persist AP0111."

Alberto Galimberti, chat, 2026-11-02.

## Context

`workflow-check` on PR #11 (run 41516926661) fails: `RUN-AP0111: code committed before the strategy approval (87dc32d …)`.
`87dc32d` is the skeleton 1.25.1 sync commit, which precedes the approval commit `cd55ca6`; `check_approval_order`
(`tools/check_workflow.py`) counts it as code. `portal-ci` passes.

## Decision

Fix upstream: the skeleton exempts skeleton-sync commits in `check_approval_order` (release 1.25.2). No rebase, no
force-push; PR #11 stays as it is. Once 1.25.2 is out the owner asks for `make sync-skeleton`, then `/persist AP0111`.
RUN-AP0111 stays in `Tuning` until then.

## Rationale

Framework fixes go upstream (NFR-14); the Spec forbids amending `87dc32d` and a history rewrite of a pushed branch is avoided.

## Alternatives Considered

Reorder commits (rebase) and force-push PR #11: rejected by the owner.

## Consequences

AP0111 closure waits for skeleton 1.25.2; `workflow-check` stays red on PR #11 until the sync.

## Links

- PR #11, RUN-AP0111 §5 Entry #2, `project-journal/decisions/2026-11-02-validator-anyof.md`
