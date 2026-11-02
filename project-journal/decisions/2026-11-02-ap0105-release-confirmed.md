# Decision Record

## Status

Accepted

## Owner's words

> "AP105 has some open points. but we moved on, we are now at v.1.25.2 or so" … "do 1, 2 and 3. so the everything is ok and we can move on with AP0201 +"

Alberto Galimberti, chat, 2026-11-02.

## Context

RUN-AP0105 listed one pending owner action: confirm skeleton release v1.18.0 (PR #41 merged, tag exists), then bump the skeleton pin. The portal has since synced to skeleton 1.25.2 (`project.toml` `[skeleton] version`; AP0111 for 1.25.1).

## Decision

The AP0105 release is confirmed and superseded by the 1.25.2 sync; the pending owner action is closed. The contract-test pin (`project.toml` `[portal] skeleton_pin`, CI `SKELETON_PIN`, still `v1.3.0`) is not changed here: tracked as story AP0112.

## Rationale

The action only asked for confirmation of a release that exists and has been overtaken. The pin bump is a portal change and needs its own story.

## Alternatives Considered

Bump the pin inside AP0105: rejected, AP0105 is closed and the change is portal code.

## Consequences

`make next` no longer lists the AP0105 owner action. AP0112 added to the backlog.
