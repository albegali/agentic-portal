# RUN-AP0108

## References
- Story ID: AP0108
- Spec: SPEC-AP0108
- Started at (datetime): 2026-10-20T12:13
- Completed at (datetime): 2026-10-20T14:40

---

## Status
Closed

> A RUN MUST NOT be Closed before Persisted.

---

# 1. Execution Strategy (Agent)

> MUST be written before any code.

### Required Reads
- [x] Target Spec
- [x] Scoped package `AGENTS.md` files, if applicable:
  - `web/AGENTS.md`
  - `server/AGENTS.md` (not touched; no server change)
- [x] `delivery/templates/RUN-template.md`

### Plan
- Step 1 (TSK-01): `web/src/styles/tokens.css` — custom properties for light/dark (mockup `.app` / `.app.light` values), `prefers-color-scheme` default, `[data-theme]` override, glass/radius/shadow/focus/motion tokens; `web/src/styles/contrast.ts` declares token pairs; Vitest contrast test computing WCAG ratios with blended glass backgrounds. Fix tokens (not the test) if a pair fails; lime stays fill-only.
- Step 2 (TSK-02): add Quicksand variable woff2 + OFL licence under `web/src/assets/fonts/`, `@font-face` with `font-display: swap`, stack `Quicksand, ui-sans-serif, system-ui`; monospace kept for code.
- Step 3 (TSK-03): `web/src/routes.tsx` registry (path, label, element) for the nine mockup sections in mockup order; React Router (`createBrowserRouter` is avoided: use `HashRouter`, since the server serves static files only) with placeholder pages; Vitest checks every registry entry renders a level-1 heading.
- Step 4 (TSK-04): shell in `web/src/components/Shell/` — skip link, `header`/`nav`/`main`, `aria-current`, visible focus, sidebar ≥ 900 px, drawer below (menu button with `aria-expanded`, Escape and scrim close, focus returned), 44 px targets < 640 px, no horizontal overflow at 375 px, reduced motion; component tests. Existing health display moves into the Overview placeholder or footer.
- Step 5 (TSK-05): `@playwright/test` + `@axe-core/playwright` devDependencies; `web/playwright.config.ts` (webServer `vite preview` on built `dist/`, projects chromium/webkit/firefox), `npm run e2e`; specs: axe over `routes` registry × both themes (via `emulateMedia` colorScheme), keyboard order/drawer, 375 px overflow, font loaded and zero non-localhost requests. Registry is imported by the spec so new routes are covered without edits (AC7).
- Step 6 (TSK-06): `docs/accessibility-checklist.md` (items, how to check, result table); CI job `e2e` (Linux, `playwright install --with-deps`, three engines, report artifact); `project.toml [stack]` e2e entry only if that table already supports it, else logged as deviation.
- Step 7 (TSK-07): update `web/AGENTS.md` (shell, registry, e2e), project summary for 375 px; leave Spec §11 and RUN §7–10 to `/persist`.
- After each step: `npm --prefix web test -- --run`, lint, typecheck; before closing: build, `make test`, `make lint`, full e2e locally.

### Assumptions
- `HashRouter` is acceptable: the Python server serves only static files and `/api`; deep links are not required by the Spec. Token launch fragment (web/AGENTS.md) is handled by a later story and must not be broken by hash routes — to be revisited in AP0102 (flagged, not decided here).
- Mockup values are the token source; where a pair fails AA the darker/lighter derivative is chosen and noted in `tokens.css`.
- `vite preview` over `dist/` is enough for e2e; the Python server is not needed (API failure shows the existing "Server unreachable" alert, which must itself pass axe).
- Playwright browsers install locally via `npx playwright install`; WebKit/Firefox run on macOS and Ubuntu CI.
- Spec status is Ready (set by the owner); owner decisions of 2026-10-20 (React Router allowed, toggle in AP0602, lime fill-only) apply.

### Risks / Open Questions
- Glass blur over gradients: effective background depends on what is behind; the test blends against the worst-case page background (bg gradient extremes). Mitigation: panels keep an opaque-enough alpha.
- Hash routing vs the token-in-URL-fragment rule in `web/AGENTS.md` (AP0102): possible conflict; stop condition if resolved only by changing architecture.
- WebKit/Firefox on CI or locally unavailable → stop condition (Spec §8).
- Font weight files increase bundle size (single variable woff2, ~100 KB); acceptable.
- Rule Spec §6 allows only React Router as new runtime dependency; `@axe-core/playwright`, `@playwright/test` are dev-only.

### Scoped Agent Rules Check
- Applies: Yes
- Files read:
  - `web/AGENTS.md`
- Notes:
  - Tokens in `web/src/styles/tokens.css`, screens under `web/src/screens/`, shared primitives in `web/src/components/`, e2e with `npm --prefix web run e2e`, axe per screen, nav drawer < 900 px, new runtime dependency needs a reason in the RUN (React Router: routing for nine sections, owner-approved 2026-10-20).

---

# 2. Human Approval

- [x] Strategy reviewed
- [x] Scope correctly understood
- [x] No out-of-scope work detected

Decision:
- [x] Approved
- [ ] Revisions requested
- [ ] Stopped

Notes:
- …

Reviewer: Alberto Galimberti
Date: 2026-10-20

---

# 3. Execution Log (Agent)

### Steps
- Step 1 (TSK-01) done: `web/src/styles/tokens.css` (light-dark() tokens), `contrast.ts`, `contrast.test.ts` (51 pairs, both themes, blended glass). Light blue/orange/green/red/yellow darkened slightly to pass AA (logged as token tuning, not a deviation).
- Step 2 (TSK-02) done: `@fontsource-variable/quicksand` (devDependency, bundled by Vite) imported in `base.css`; OFL licence at `web/public/licenses/Quicksand-OFL.txt`.
- Step 3 (TSK-03) done: `routes.ts`, `screens/Placeholder.tsx`, `App.tsx` (HashRouter), `App.shell.test.tsx` (heading, title, aria-current per route); react-router added as runtime dependency (owner-approved 2026-10-20: routing for nine sections).
- Step 4 (TSK-04) done: `components/Shell/` (Shell.tsx, Shell.css, ServerStatus.tsx), `styles/base.css`; drawer state derived from the route (lint rule set-state-in-effect); focus returns to the menu button after Escape/scrim via post-render effect (found by e2e); component tests for skip link, landmarks, keyboard nav, drawer.
- Step 5 (TSK-05) done: `playwright.config.ts` (vite preview of `dist/`, chromium/webkit/firefox), `e2e/a11y|keyboard|responsive|font.e2e.ts`; axe over the route registry × light/dark plus open drawer at 375 px; `npm run e2e`. Dev dependencies: @playwright/test, @axe-core/playwright, @fontsource-variable/quicksand, @testing-library/user-event, @types/node. WebKit on macOS needs Option+Tab to reach links: the test uses Alt+Tab there.
- Step 6 (TSK-06) done: `docs/accessibility-checklist.md` (12 checks, results table); CI job `e2e` (Linux, 3 engines, report on failure) in `.github/workflows/ci.yml`; `web/.gitignore`.
- Step 7 (TSK-07) done: `web/AGENTS.md` (registry, tokens/contrast rule, hash routing, font, checklist), `reference/project-summary.md` (375 px, WCAG 2.2 AA). Spec §11 and RUN §7-10 left to `/persist`.
- PAUSED 2026-10-20 (owner session limit) and resumed at 14:00 CET; no code was lost.

### Changes (high-level)
- Code: `web/src/` (styles, routes, shell, placeholders), `web/e2e/`, `web/playwright.config.ts`, `web/public/licenses/`
- Interfaces: route registry (`routes.ts`), CSS custom property names, `npm --prefix web run e2e`
- Domain: none
- Tests: contrast (51 pairs), shell/registry (Vitest), Playwright e2e (111 across 3 engines)
- Specs: none changed

---

# 4. Verification

- Build: OK
- Tests: OK
- Interfaces / target platforms: OK
- Manual (if any): not run (checklist is a release-time procedure; first run goes to the owner at tuning)

Notes:
- `make lint`, `PY=python3.14 make test` (server 10, scripts 6, web 68), web build, `npm run e2e` (111 passed: Chromium, WebKit, Firefox; axe 9 routes × 2 themes + drawer, keyboard, 375 px, 44 px targets, reduced motion, bundled font, zero external requests).
- The default `python3` here is 3.12: use `PY=python3.14` locally (unchanged from AP0101).
- CI e2e job is unverified until the first GitHub run.

If FAIL → move to Tuning.

---

# 5. Tuning Log (If needed)

> Only within scope.

- No tuning entries: the owner accepted the result and all deviations on 2026-10-20 (chat).

---

# 6. Deviations

1. Light-theme status colours (blue, orange, green, red, yellow) darkened a few percent from the mockup so they pass AA on the tinted page background. Scope impact: None (tokens, owner's accessibility rule).
2. `project.toml [stack]` e2e entry not added: the skeleton Makefile only runs setup/test/lint/run and cannot be changed (NFR-14). e2e runs via `npm --prefix web run e2e` and the CI job. Scope impact: None.
3. Added dev dependencies not named in the Spec: @fontsource-variable/quicksand (bundles Quicksand), @testing-library/user-event, @types/node. Dev-only; no runtime impact beyond react-router. Scope impact: Minor.
4. Flag for AP0102: hash routing and the launch token in the URL fragment (`#token=…`, ADR-006) share the fragment. The token must be read and stripped before the router mounts; noted in `web/AGENTS.md`. Scope impact: None here.

---

# 7. Persistence / Reconciliation

- [x] Spec updated (if needed)
- [x] Specs updated (if needed)
- [x] Acceptance Criteria aligned

Summary:
- SPEC-AP0108 §11 and status Done; Brief closed; index updated. Reference docs touched by the story: `reference/project-summary.md` (375 px, WCAG 2.2 AA), `web/AGENTS.md` (registry, tokens/contrast, hash routing, font, checklist). No ADR or architecture change.

---

# 8. Quality Gates Check

- [x] Acceptance criteria satisfied (AC1-AC7, locally on 3 engines)
- [x] Tests passing
- [x] No scope creep (deviations owner-approved)
- [x] Persistence completed

---

# 9. Outcome

Tasks completed:
- TSK-AP0108-01 … TSK-AP0108-07

Tasks deferred:
- None

Goal achieved:
- [x] Yes
- [ ] Partial
- [ ] No

Summary:
- Accessible, responsive shell with lime glass tokens, bundled Quicksand and automated checks (contrast test, axe on every registered route in both themes on three engines) that new screens inherit by registering a route.

---

# 10. Next Steps

- Follow-ups: first GitHub run of the CI `e2e` job; AP0102 must read and strip `#token=…` before the router mounts; AP0602 (manual theme toggle, required before project release); run `docs/accessibility-checklist.md` at the first release.
- Risks: WebKit/Firefox availability on CI runners; glass contrast depends on the page backdrop modelled in the contrast test.
- Improvements: none.

---

# 11. Addendum (Post-Closure Only)

### 2026-10-20
- Note: first GitHub CI run on PR #1 is green, including the new `e2e` job (axe on Chromium, WebKit, Firefox). The pending CI verification is resolved.
- Impact: none; merged into `main`.
