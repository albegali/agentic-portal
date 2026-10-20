# BRIEF-AP0108 - App shell and accessibility baseline

## References
- Story ID: AP0108
- Source: `analysis/30-refined/REFINED_AP0108_app_shell_accessibility.md` · external tracker URL: n/a
- Captured at (datetime): 2026-10-20T17:00
- Captured by: Alberto Galimberti (with Claude)
- Closed at (datetime): 2026-10-20T14:40

---

## Status
Closed

---

## Type
Feature

---

## Urgency (Optional)
Medium

---

# 1. Original Customer Intent

As a developer using the workflow, I want a keyboard-operable, responsive shell with navigation, light and dark CSS tokens of the lime glassmorphism theme from the mockup, bundled Quicksand font and automated accessibility checks, so that every screen starts accessible and consistent from 375 px up.

---

# 2. Initial Goal

A web app shell (layout, navigation, themes, font, placeholder routes) on top of the AP0101 scaffold, with accessibility checks in place from the start so later screens inherit them.

---

# 3. Impact (Required for Hotfix)

n/a (not a hotfix)

---

# 4. Context

- Requirements: NFR-11 (WCAG 2.2 AA, audit tool + manual); NFR-06 not measured here; NFR-08/09 unaffected (Playwright and axe are web devDependencies only).
- Navigation derived from the mockup screen map (`reference/product/mockup-reference.md`, `SCREENS` in `reference/mockup/agentic-portal.html`): Overview, Plan, Backlog, Approvals, Agent runs, Insights, Architecture, Journal, Settings. Story detail is reached from Backlog, not from the nav.
- Mockup responsive rules (owner 2026-10-19): below 900 px the navigation becomes a drawer (menu button, closes on Escape or tap outside); below 640 px touch targets ≥ 44 px. Visual direction: Quicksand, lime accent `#C8F169` as primary, radii 4–8 px, glass panels with blur and soft shadows; dark and light token sets in the mockup `.app` / `.app.light` rules.
- Workshop 2026-10-19 decisions: Quicksand bundled (no CDN); 375 px in scope; light and dark only; navigation delegated to the AI; axe in Playwright over Chromium, WebKit and Firefox with WCAG 2.0/2.1/2.2 A+AA, over every registered route in both themes; contrast unit test of declared token pairs; manual per-release checklist (tab order, skip link, landmarks, 200%/400% reflow, reduced motion, screen reader smoke test).
- Package rules: `web/AGENTS.md` (tokens in `web/src/styles/tokens.css`, screens in `web/src/screens/`).

---

# 5. Known Constraints

- Depends on AP0101 (closed): `web/` Vite/React/TS scaffold.
- Placeholder routes only; no real screens, no data.
- No CDN, no external requests at runtime; works offline on localhost.
- No new runtime dependency without a reason logged in the RUN (NFR-09); e2e tooling is dev-only.
- Glassmorphism translucency is a contrast risk: the contrast test must use the effective (blended) background.
- Out of scope: individual screens, NFR-06 measurement.

---

# 6. Expected Fix (Optional)

`tokens.css`, shell layout with skip link, landmarks, nav and drawer, route registry with placeholders, bundled Quicksand, contrast unit test, Playwright + axe e2e (`npm --prefix web run e2e`), manual checklist document.

---

# 7. Open Questions

- Theme behaviour (OS preference vs manual toggle, persistence): assumed OS preference; the mockup shows a toggle (FR-28). Non-blocking.
- Project summary still says "desktop browsers (assumption)": update for the 375 px decision.
- CI wiring of the e2e job (browsers install, three engines) is not stated in the Story.

---

# 8. Clarifications / Addenda

> Do not rewrite the original intent after capture.
> Add clarifications here.

### Addendum - 2026-10-20

- Source: owner, chat review of SPEC-AP0108 (Draft).
- Clarification: theme follows the OS preference in this story; the manual toggle (FR-28, AP0602) is required before the project release. React Router accepted as runtime dependency. Playwright on WebKit and Firefox in CI unavailable is a stop condition. Lime accent used only as fill; accessibility is mandatory.
- Impact: Spec Notes updated; no scope change for AP0108; AP0602 priority to be raised from Could (backlog, product mode).

---

# 9. Derived Artifacts

- Spec: SPEC-AP0108 (Done)
- RUN: RUN-AP0108 (Closed)
