# Decision Record

## Status

Accepted

## Owner's words

> "ok, let's close all the open points, I want to close this context to be able to launch /next and continue the development of the portal"

Alberto Galimberti, chat, 2026-10-21, after the skeleton 1.17.2 sync; the open points listed just before were the
`v0.1.0` tag (SPEC-AP0101 AC7), the agentic-skeleton tags (`v1.3.0` was pending since AP0109), AP0105 vs `make gates`,
and the leftover history-rewrite ref.

## Context

Release tags are owner actions (RUN template, `## Pending owner actions`). Several closed RUNs waited on them:
RUN-AP0101 (`v0.1.0`, AC7), RUN-AP0109 (`v1.3.0`, AC5 open on the tag only), RUN-AP0104 (`SKELETON_PIN` to move from the
SHA to `v1.3.0` once tagged, SPEC-AP0104 §10).

## Decision

The owner's instruction authorises the agent to do these owner actions now:
- agentic-portal: tag `v0.1.0` on `main` 106cfba; the release workflow publishes Release `v0.1.0`.
- agentic-skeleton: tag `v1.3.0` on d00c402 (the commit already pinned) and `v1.17.2` on 27ad3fc.
- `SKELETON_PIN` (project.toml `[portal] skeleton_pin`, CI default) moves from the SHA to `v1.3.0` (same commit).
- AP0105 stays open: re-scoped at its Spec gate on top of skeleton `tools/gates.py` / `tools/approve.py` (note in its Spec §10).

## Rationale

Each action was already decided in the artifacts and only waited for the owner's go; the tags point at commits whose
CI is green.

## Alternatives Considered

Leaving the tags to the owner: keeps three RUNs Partial or waiting with nothing left to decide.

## Consequences

SPEC-AP0101 AC7 and SPEC-AP0109 AC5 met; RUN-AP0101 and RUN-AP0109 Goal achieved `Yes`; no pending owner actions.

## Links

- Release https://github.com/albegali/agentic-portal/releases/tag/v0.1.0 (run 39605248208), manifest sha256 5afeecf9… = zip
- agentic-skeleton tags `v1.3.0` (d00c402), `v1.17.2` (27ad3fc)
