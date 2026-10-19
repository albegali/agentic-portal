---
artifact_type: adr
id: ADR-001
status: accepted         # proposed | accepted | superseded by ADR-xxx | rejected
date: 2026-10-19
drivers: [NFR-08, NFR-09, NFR-10, NFR-11, FR-23, FR-24]
---

# ADR-001 — Local runtime: Python stdlib server + React/Vite/TypeScript static bundle

## Context
The brief fixes the runtime (local, one portal per repository, localhost), the backend (Python standard library only, NFR-08) and the frontend (React + Vite + TypeScript shipped prebuilt, Node only for portal development, NFR-09). It has to run on macOS, Windows and Linux in the latest 2 versions of the main browsers (NFR-10), comply with WCAG (NFR-11) and follow the approved mockup's look (Quicksand, lime accent, glass panels, responsive down to 375 px). Still open: the frontend libraries and the minimum Python version.

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. Lean frontend: React + React Router + TanStack Query, hand-written CSS with design tokens ported from the mockup, Mermaid for diagrams | Few dependencies, small bundle, the mockup CSS is reused as is, TanStack Query handles caching/refetch of tool outputs | Accessible widgets (dialog, tabs, menus) written by hand or with a small headless library | Good: NFR-09, NFR-11 (with axe tests), mockup fidelity |
| B. Component library (e.g. MUI/Chakra) + Tailwind | Ready accessible components | Heavy bundle, fights the mockup's custom look, more upgrade churn | Weaker fit to the mockup; larger bundle |

## Decision
Option A, with Python ≥ 3.14 for the portal server (owner decision 2026-10-19; the skeleton tools themselves keep working on ≥ 3.14) and `http.server.ThreadingHTTPServer` as the server; accessible primitives come from a headless library only if hand-written ones fail the axe/keyboard tests.

## Consequences
- Positive: zero runtime dependencies on the backend; the static bundle is served by the same Python process; the design tokens come straight from `reference/mockup/agentic-portal.html`.
- Negative / trade-offs: accessible dialog/tabs/menu must be built and tested; `http.server` is minimal (routing, JSON and SSE handled by our own thin layer).
- Python ≥ 3.14 is checked by the launcher (`tools/portal.py`) and by `make adopt`, which warn with the detected version and how to install 3.14; projects on older Python can use the workflow but not the portal.
- Follow-up stories: Python version check in launcher and adopt (upstream); walking skeleton (server serves the bundle + one JSON endpoint); design tokens and app shell (nav drawer, header, palette, theme).

## Reversibility
Medium for frontend libraries (localized in `web/`); high for the backend constraint (owner decision).
