---
artifact_type: refined
us_id: STORY_AP0108
title: App shell and accessibility baseline
roadmap_phase: R1
status: refined
source_files:
  - analysis/10-stories/STORY_AP0108_app_shell_accessibility.md
  - analysis/20-analysis/ANALYSIS_AP0108_app_shell_accessibility.md
workshop_evidence:
  - analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md
related_references:
  - reference/product/non-functional-requirements.md#NFR-11
  - reference/product/non-functional-requirements.md#NFR-06
last_updated: 2026-10-19
---

# Refined Story AP0108 - App shell and accessibility baseline

## 1. References

- ID: AP0108
- Title: App shell and accessibility baseline
- Roadmap phase: R1
- Sources used: Story, Analysis, workshop minutes, NFR-11, NFR-06
- Missing sources: reference/product/mockup-reference.md and the prototype (never read by the analyst; tokens and navigation must be derived from them in the Brief)
- Workshop evidence: analysis/workshops/WORKSHOP_2026-10-19_AP0101-AP0103-AP0106-AP0108.md

## 2. Refined User Story

### Refined story text

As a developer using the workflow, I want a keyboard-operable, responsive shell with navigation, light and dark CSS tokens of the lime glassmorphism theme from the mockup, bundled Quicksand font and automated accessibility checks, so that every screen starts accessible and consistent from 375 px up.

### Refined description

The shell registers placeholder routes now; real screens come later and inherit the checks.

## 3. Scope

### In scope

- Navigation sections derived from the mockup screen map (delegated to the AI).
- Keyboard operation with visible focus; 375 px layout without horizontal scroll and with usable navigation.
- Light and dark themes of the lime glassmorphism theme; tokens as CSS custom properties in one file.
- Quicksand bundled with the web assets (no CDN, works offline on localhost).
- axe-core in Playwright (Chromium, WebKit, Firefox, WCAG 2.0/2.1/2.2 A+AA) over every registered route in both themes; contrast unit test of declared token pairs; manual per-release checklist (tab order, skip link, landmarks, 200%/400% reflow, reduced motion, screen reader smoke test).

### Out of scope

- Individual screens; NFR-06 measurement (deferred to the first data-heavy screen).

## 4. Confirmed Information

### Facts

- NFR-11 targets WCAG 2.2 AA; verification by audit tool and manual checks. Depends on AP0101.
- Playwright/axe are web devDependencies only (NFR-08/09 unaffected).

### Decisions confirmed during refinement

- Font: Quicksand, bundled (override of the system font stack).
- 375 px mobile layout is in scope.
- Themes: light and dark only, of the lime glassmorphism theme.
- Navigation sections: delegated to the AI, derived from the mockup.
- Not overridden, therefore standing: the accessibility tooling, route enumeration, manual checklist and contrast test above; no AC for NFR-06.

### Residual assumptions

- Theme selection (OS preference, manual toggle, or both; persistence) was not stated: assumed to follow the OS preference, to be confirmed in the Brief.
- Project summary "desktop browsers (assumption)" is outdated and should be updated.

## 5. Confirmed Acceptance Criteria

- Given the shell, when I use only the keyboard, then all navigation is reachable with visible focus.
- Given every route registered in the shell in light and dark themes, when axe-core runs in Playwright, then no WCAG 2.2 AA violations.
- Given the declared token pairs in both themes, when the contrast test runs, then each meets WCAG 2.2 AA ratios.
- Given a 375 px viewport, when the shell renders, then no horizontal scroll and navigation remains usable.
- Given the app served offline from the bundle, when the shell renders, then text uses the bundled Quicksand with no external requests.

## 6. Remaining Open Points

### Functional

- Theme behaviour (OS vs toggle, persistence): non-blocking, default OS.

### Technical

- Glassmorphism translucency is a contrast risk in both themes; the contrast test must use the effective (blended) background. Not blocking.
- Mockup-reference.md must be stable before tokens are fixed.
- Update the project summary for the 375 px decision.

## 7. Brief Handoff Notes

### Candidate Brief Tasks

- Token file and contrast test; shell layout and navigation; Quicksand bundling; Playwright + axe in CI; manual checklist.

### Boundaries to respect

- No real screens; no CDN or runtime dependency added; depends on the AP0101 scaffold.

## 8. Refinement Outcome

- Story ready with residual open points to track
