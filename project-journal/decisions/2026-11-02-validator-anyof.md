# Decision Record

## Status

Accepted

## Owner's words

> "Approved, as the owner:
> - Widen the validator subset with anyOf (portal side); no upstream change.
> - Add AP0111 to backlog/stories.toml: type "chore", size "XS", deps ["AP0105"], title "Skeleton 1.25.1 upgrade: validator accepts anyOf". Scope: the 1.25.1 upgrade already on chore/skeleton-1.25.1 plus the anyOf support and its tests.
> - Same branch chore/skeleton-1.25.1, same PR #11 (retitle it to AP0111); keep the upgrade commit and the fix commit separate.
> Record this decision, then run /quick AP0111."

Alberto Galimberti, chat, 2026-11-02.

## Context

Skeleton 1.25.1 `schemas/gates.schema.json` uses `anyOf` in `data`; the portal validator's supported subset
(`server/portal_server/contract/validator.py`, ADR-002 revision 2026-10-20) lacks it, so `test_contract_*` fail on PR #11.
It is the only keyword outside the subset.

## Decision

Widen the portal validator subset with `anyOf` (at least one alternative matches). No change requested upstream.
Tracked as story AP0111 (chore, XS) on the existing branch `chore/skeleton-1.25.1` and PR #11, retitled to AP0111;
the upgrade commit and the validator fix stay separate commits.

## Rationale

`anyOf` is standard JSON Schema and fits the gates list-or-single shape; the validator is portal code and
`check_subset` still catches any further drift in CI.

## Alternatives Considered

Ask upstream to keep schemas inside the subset: rejected by the owner.

## Consequences

ADR-002 subset list and the validator docstring gain `anyOf`; tests added. No public interface change.

## Links

- PR #11, `schemas/gates.schema.json`, `server/portal_server/contract/validator.py`
