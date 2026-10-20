# SPEC-AP0108 - App shell and accessibility baseline

## References
- Story ID: AP0108
- Brief: BRIEF-AP0108
- RUN: RUN-AP0108

---

## Status
Done

---

# 1. Goal

A responsive, keyboard-operable app shell in `web/` (skip link, landmarks, navigation with drawer below 900 px, placeholder routes for the nine mockup sections), lime glassmorphism light/dark tokens in one CSS file, bundled Quicksand, and automated accessibility checks (token contrast unit test, axe-core in Playwright) that every later screen inherits.

---

# 2. User / Business Value

As a developer using the workflow
I want an accessible, consistent shell from 375 px up
So that every screen starts WCAG 2.2 AA-compliant and no accessibility debt accumulates.

---

# 3. Scope

Included:
- Route registry (single list: path, label, placeholder) for Overview, Plan, Backlog, Approvals, Agent runs, Insights, Architecture, Journal, Settings; placeholders render a heading and a short "not yet implemented" text.
- Shell: skip link, `header`/`nav`/`main` landmarks, current-page indication, visible focus, nav as sidebar ≥ 900 px and drawer below (menu button, closes on Escape and on tap outside, focus returned to the button), touch targets ≥ 44 px below 640 px, no horizontal scroll at 375 px.
- `web/src/styles/tokens.css`: all colours, radii, shadows, glass values as CSS custom properties; light and dark sets; theme follows `prefers-color-scheme`; a `data-theme` attribute on the root overrides it (used by tests); `prefers-reduced-motion` respected.
- Quicksand bundled in the web assets (woff2, self-hosted via `@font-face`; licence file included); monospace kept for code and paths.
- Contrast unit test: declared token pairs (text/background, muted, accent/onaccent, status colours as used) in both themes against WCAG 2.2 AA ratios, using effective blended backgrounds for glass panels.
- Playwright e2e (devDependency): axe-core (WCAG 2.0/2.1/2.2 A+AA) over every registered route, both themes, Chromium + WebKit + Firefox; keyboard test; 375 px test; offline-font test.
- Manual per-release checklist `docs/` or `delivery/` location chosen in the RUN: tab order, skip link, landmarks, 200%/400% reflow, reduced motion, screen reader smoke test.
- `make`/`project.toml` wiring for the e2e command and, if feasible, a CI job; update `web/AGENTS.md` and the project summary (375 px).

Out of scope:
- Real screens, data, API calls, command palette, story detail, Approvals/Runs behaviour.
- Manual theme toggle and persistence (open; see Notes).
- NFR-06 measurement; native screen-reader automation.
- Any change to skeleton files (NFR-14); any server change.

---

# 4. Acceptance Criteria

- [x] AC1: Given the shell, when I use only the keyboard, then the skip link and all navigation items are reachable in a logical order with visible focus, and the drawer opens, traps no focus incorrectly and closes with Escape.
- [x] AC2: Given every route registered in the shell, in light and dark themes, when axe-core runs in Playwright on Chromium, WebKit and Firefox, then there are no WCAG 2.0/2.1/2.2 A+AA violations.
- [x] AC3: Given the declared token pairs in both themes (with blended glass backgrounds), when the contrast unit test runs, then each pair meets its WCAG 2.2 AA ratio (4.5:1 text, 3:1 UI components/large text).
- [x] AC4: Given a 375 px viewport, when the shell renders any route, then there is no horizontal scroll and navigation is usable (drawer, targets ≥ 44 px).
- [x] AC5: Given the app served offline from the bundle, when the shell renders, then text uses bundled Quicksand and no request leaves localhost.
- [x] AC6: Given the manual checklist, when a release is prepared, then each item is listed with how to check it and a place to record the result.
- [x] AC7: Given a new entry in the route registry, when the e2e suite runs, then it is covered by the axe check without editing the test.

---

# 5. Tasks

- `TSK-AP0108-01` Tokens file (light/dark, glass, radii, focus, motion) and contrast unit test with blended backgrounds.
- `TSK-AP0108-02` Bundle Quicksand (woff2 + licence) with `@font-face`; fallback stack.
- `TSK-AP0108-03` Route registry, router, placeholder routes, Vitest tests.
- `TSK-AP0108-04` Shell layout: skip link, landmarks, nav sidebar/drawer, focus management, responsive rules, 44 px targets, reduced motion; component tests.
- `TSK-AP0108-05` Playwright setup (`npm run e2e`), axe over all registered routes × themes × 3 engines, keyboard, 375 px and offline-font tests.
- `TSK-AP0108-06` Manual per-release checklist; CI e2e job and `project.toml`/Makefile wiring.
- `TSK-AP0108-07` Docs: `web/AGENTS.md`, project summary (375 px), persistence.

---

# 6. Execution Boundaries

The agent is allowed to:
- Edit `web/` (src, styles, assets, config, devDependencies), `.github/workflows/`, `project.toml [stack]` e2e entry, and add the checklist document.
- Add React Router as the one runtime dependency named in architecture §3 (reason logged in the RUN); add Playwright and axe-core as devDependencies.

The agent is not allowed to:
- Add runtime dependencies beyond the router, or load anything from a CDN.
- Implement real screens, data fetching or a theme toggle.
- Modify skeleton files (`tools/`, `workflow/`, templates) or `server/`.
- Weaken or skip an accessibility rule to make a check pass without logging it as a deviation.

---

# 7. Quality Gates

- [x] Tests added/updated (Vitest, contrast, Playwright)
- [x] Build passes (`make lint`, `make test`, web build)
- [x] Public interfaces updated if impacted (route registry, token names, e2e command)
- [x] Domain invariants respected (no CDN, offline-capable, no runtime deps beyond router)
- [x] No breaking changes unless explicitly approved
- [x] axe clean on 3 engines × 2 themes × all routes (local; CI job pending first GitHub run); manual checklist delivered, first run at release

---

# 8. Stop Conditions

Stop and ask for supervision if:
- acceptance criteria are ambiguous
- a token pair cannot meet AA without changing the lime accent or glass look
- Playwright browsers cannot run on CI or locally
- a runtime dependency other than the router seems necessary
- work appears out of scope (real screens, theme toggle, skeleton or server change)

---

# 9. Impacted Areas

- Code: `web/src/` (styles, shell, routes), `web/e2e/`, `web/package.json`
- Interfaces: route registry; CSS custom property names; `npm run e2e`
- Domain: none
- UX: shell, navigation, themes, typography
- Platforms / distribution: bundle grows by the font files
- Tests: contrast unit test, Vitest, Playwright + axe
- Docs: `web/AGENTS.md`, project summary, manual checklist

---

# 10. Notes / Clarifications

- Theme (owner 2026-10-20): follows the OS preference here; the manual toggle with persistence (FR-28) is AP0602 and is required before the project release. The `data-theme` override exists for tests and for AP0602.
- React Router accepted by the owner (2026-10-20) as the only runtime dependency added.
- Nav order follows the mockup `SCREENS` list; Story detail is a child of Backlog and not registered here.
- Accent `#C8F169` (owner 2026-10-20: accessibility is mandatory): fill only, with `onaccent` text; a darker derivative where accent-coloured text or borders are needed.

---

# 11. Final Reconciliation

To be completed before marking Done.

- [x] Acceptance criteria still aligned
- [x] Tasks completed or explicitly deferred
- [x] Specs updated if needed
- [x] RUN completed and persisted

Summary:
- TSK-01..07 done. Final state: route registry `web/src/routes.ts` (nine sections, HashRouter); shell in `web/src/components/Shell/` (skip link, nav/main landmarks, drawer below 900 px with Escape/scrim close and focus return, 44 px targets below 640 px, reduced motion); tokens as `light-dark()` in `web/src/styles/tokens.css`, contrast test over the pairs in `contrast.ts` with blended glass; Quicksand bundled via `@fontsource-variable/quicksand`; Playwright + axe (`npm --prefix web run e2e`, 3 engines) driven by the registry; CI job `e2e`; checklist `docs/accessibility-checklist.md`.
- Owner-accepted deviations (2026-10-20): light status colours darkened for AA; no `project.toml` e2e entry (skeleton Makefile, NFR-14); extra dev dependencies (font package, user-event, @types/node).
- Open: CI e2e job unverified until the first GitHub run; hash routing vs launch token fragment handed to AP0102; manual toggle in AP0602.
