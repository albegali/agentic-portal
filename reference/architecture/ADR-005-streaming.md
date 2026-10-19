---
artifact_type: adr
id: ADR-005
status: accepted
date: 2026-10-19
drivers: [FR-10, NFR-07, NFR-08]
---

# ADR-005 — Streaming: Server-Sent Events

## Context
Agent output must reach the browser live (< 500 ms, NFR-07) with a stdlib-only backend (NFR-08). Commands (launch, cancel, approve) are rare and can be plain requests.

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. SSE (`text/event-stream`) per run and one for state changes; commands as POST | Trivial with `http.server`; browser auto-reconnect with `Last-Event-ID` replays from the run log | One-way only; ~6 connections per origin on HTTP/1.1 | Good |
| B. WebSocket | Bidirectional | No stdlib server: hand-written RFC 6455 | Poor fit to NFR-08 |

## Decision
Option A (owner-confirmed 2026-10-19). One multiplexed SSE stream per browser tab (events tagged by run ID and by "state changed") to stay under the per-origin connection limit.

## Consequences
- Positive: simple, resumable from the run log on disk.
- Negative / trade-offs: the event bus and replay are ours to write and test.
- Follow-up stories: SSE endpoint with replay; file watcher that emits "state changed" when workflow files change.

## Reversibility
Low cost: confined to one endpoint and one client hook.
