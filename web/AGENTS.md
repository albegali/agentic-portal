# web/ — package rules

React + Vite + TypeScript, shipped as a prebuilt static bundle (NFR-09). See ADR-001 and `reference/product/mockup-reference.md`.

## Layout
- `web/src/screens/<Screen>/` — one folder per mockup screen (Overview, Plan, Backlog, Story, Approvals, Runs, Insights, Architecture, Journal, Settings).
- `web/src/components/` — shared accessible primitives (Dialog, Tabs, Drawer, Chip group, Pill, Terminal, Diff).
- `web/src/api/` — typed client, TanStack Query hooks, SSE hook; types generated from the contract JSON Schemas.
- `web/src/styles/tokens.css` — design tokens ported from the mockup (Quicksand, lime accent, glass, radii 4–8 px, dark/light).

## Rules
- Behaviors marked normative in `mockup-reference.md` are acceptance criteria; sample data is not.
- WCAG 2.2 AA: semantic elements, labels, visible focus, keyboard paths, 44 px touch targets below 640 px; axe check per screen in e2e.
- Responsive from 375 px; nav drawer below 900 px.
- Token only in `sessionStorage`; never log it; never put it in URLs other than reading it from the launch fragment.
- New runtime dependency only with a reason in the RUN.

## Commands
- Setup: `npm --prefix web ci`
- Dev: `npm --prefix web run dev`
- Test: `npm --prefix web test -- --run`
- Lint: `npm --prefix web run lint && npm --prefix web run typecheck`
- E2E + a11y: `npm --prefix web run e2e`
