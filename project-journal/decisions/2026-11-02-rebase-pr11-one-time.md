# Decision Record

## Status

Accepted

## Owner's words

> "only for this time, please, Rebase and force-push. Don't change the rule later, no rebase and force push in the future, only for now"

Alberto Galimberti, chat, 2026-11-02. Supersedes, for this one action, "no rebase, no force-push" in
`project-journal/decisions/2026-11-02-approval-order-skeleton-sync.md`.

## Context

`workflow-check` on PR #11 fails (`check_approval_order`): the skeleton sync commit `87dc32d` precedes the strategy approval
commit `cd55ca6`. Skeleton 1.25.2 exempts sync commits, but not when they also change `AGENTS.md`, as `87dc32d` does.

## Decision

One-time exception: reorder `chore/skeleton-1.25.1` so the approval commit comes first, then `87dc32d`, then the rest
(content unchanged), and force-push PR #11 (`--force-with-lease`). The 1.25.2 sync goes on top as its own commit.
The rule stays: no rebase and no force-push in future, this covers only PR #11.

## Rationale

Avoids a third skeleton release and unblocks AP0111.

## Alternatives Considered

Upstream 1.25.3 accepting `AGENTS.md` in a sync commit: not chosen by the owner.

## Consequences

Commit hashes cited in RUN-AP0111 (`87dc32d`, `b201ea5`) change; the Spec still holds, the upgrade commit's content is untouched.

## Links

- PR #11, RUN-AP0111 §5 Entry #2
