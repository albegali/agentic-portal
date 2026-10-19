---
artifact_type: analysis
us_id: STORY_AP0108
title: App shell and accessibility baseline
roadmap_phase: R1
status: workshop-ready
source_files:
  - analysis/10-stories/STORY_AP0108_app_shell_accessibility.md
  - reference/project-summary.md
related_references:
  - reference/product/non-functional-requirements.md#NFR-11
  - reference/product/non-functional-requirements.md#NFR-06
last_updated: 2026-10-19
---

# Analysis AP0108 - App shell and accessibility baseline

## 1. References

- ID: AP0108
- Source story: analysis/10-stories/STORY_AP0108_app_shell_accessibility.md
- Roadmap phase: R1
- Sources used: project summary, Story, NFR-11, NFR-06
- Missing sources: reference/product/mockup-reference.md (tokens, behaviours, screen map, cited by the Story but not provided); prototype docs/sources/portal-prototype.dc.html; navigation structure; NFR-10 text beyond the cited extract

## 2. Original User Story

### Story text

As a developer using the workflow, I want a keyboard-operable shell with navigation, CSS tokens from the mockup, and automated accessibility checks, so that every screen starts accessible and consistent.

### Description

Epic EP-01 · Must · R1 · M · technical · NFR-11, NFR-06 · Depends on: AP0101 · Notes: tokens and behaviours per mockup-reference.md · Out of scope: individual screens.

## 3. Intent Understanding

### Functional goal

- A common shell (navigation, layout, light/dark tokens) with an automated accessibility gate that later screens inherit.

### Actors involved

- Developers/POs/analysts using the portal; later screen teams.

### Expected outcome

- Keyboard-reachable navigation with visible focus, WCAG 2.2 AA clean in both themes, usable at 375 px.

## 4. Information Classification

### Facts

- NFR-11: WCAG compliance, keyboard operability, contrast in both themes; target WCAG 2.2 AA; verification audit tool + manual. Owner said "WCAG compliant"; version and level are assumed.
- NFR-06 (Should): screens render < 1 s after data load for ~500 stories/files; assumption, to be assessed later.
- Project summary: desktop browsers (assumption); NFR-10 requires latest 2 versions of Chrome, Edge, Safari, Firefox and Chromium-based browsers.
- Depends on AP0101 (server and web scaffold).

### Clarifications received

- NFR-06 target accepted for now, assessment deferred (owner 2026-10-19).

## 5. Original Acceptance Criteria

- Given the shell, when I use only the keyboard, then all navigation is reachable with visible focus.
- Given any screen in light and dark tokens, when axe-core runs in Playwright, then no WCAG 2.2 AA violations.
- Given a 375 px viewport, when the shell renders, then no horizontal scroll and navigation remains usable.

## 6. Ambiguities, Functional Gaps, and Technical Gaps to Clarify

### Functional ambiguities

- "Navigation": which items/sections? Source presumably the mockup screen map (not read).
- "Any screen" while individual screens are out of scope: which pages does the check cover (shell + placeholder routes)?
- Theme selection: follows OS preference, manual toggle, or both; persisted where (state lives in `.portal/`)?
- A 375 px requirement sits against the "desktop browsers" assumption: is mobile layout truly in scope?

### Functional gaps

- NFR-06 is cited but has no AC or measurement approach.
- Manual WCAG checks (NFR-11) not covered: screen reader, zoom/reflow, reduced motion, focus order, skip link, landmarks.
- Behaviour when a screen is loading, empty or in error is not part of the shell definition.

### Technical gaps

- Playwright and axe-core as dev dependencies (allowed by NFR-08/09 as dev-only?) and browser matrix in CI; automated checks cover only part of WCAG.
- Which tokens are binding (colours, spacing, typography) and how they are checked for contrast in both themes.
- Fonts: bundled vs. system (offline, localhost).

### Dependencies or ownership points to clarify

- Mockup-reference must be approved/stable before tokens are fixed (mockup is an inception artifact).
- All later screen stories inherit the shell; changes here have wide impact.

## 7. Workshop Refinement Preparation

Points to resolve before the story is ready for development (input for Brief, Spec and delivery).

### Functional points to resolve

Business or functional questions: an answer from the PO / stakeholder is mandatory.

- [High impact] Which navigation sections does the R1 shell show? — the inventory drives routes and the axe scope; mockup-reference.md not read here.
- [High impact] Is a 375 px (mobile) layout in scope, given the "desktop browsers" assumption? — changes design and test effort for every screen.
- [Medium impact] Theme: follow the OS, manual toggle, or both; remembered between sessions? — user-visible behaviour.

### Technical points to resolve

Analyst proposals: they stand unless the team overrides them in the workshop.

- [High impact] Accessibility tooling in CI — **Proposal**: Playwright + `@axe-core/playwright` as web devDependencies; CI runs on Chromium, WebKit and Firefox against the built bundle served by the stdlib server, with WCAG 2.0/2.1/2.2 A+AA tags · **Why**: dev-only, so NFR-08/09 are unaffected; covers the NFR-10 engines · **Alternatives**: Lighthouse CI · **Confidence**: high
- [High impact] "Any screen" and manual checks — **Proposal**: the test enumerates every route registered in the shell (placeholders now, real screens later) in both themes; a manual checklist per release: tab order, skip link, landmarks, 200%/400% zoom reflow, reduced motion, VoiceOver/NVDA smoke test · **Why**: axe finds only part of WCAG issues; NFR-11 requires manual verification · **Confidence**: high
- [Medium impact] Token source and contrast — **Proposal**: tokens as CSS custom properties in one file derived from mockup-reference.md; a unit test computes the contrast ratio of declared foreground/background pairs in both themes · **Why**: contrast in both themes is part of NFR-11 · **Confidence**: medium
- [Low impact] Fonts — **Proposal**: system font stack, no web fonts · **Why**: offline, localhost, no extra assets · **Confidence**: medium (depends on mockup tokens)
- [Low impact] NFR-06 — **Proposal**: no AC in this story; defer explicitly to the first data-heavy screen · **Why**: owner decided to assess later; the shell has no data · **Confidence**: high

### Readiness outcome expected

- Story scope confirmed or reformulated
- Acceptance criteria clarified and testable
- High-impact functional points answered by the PO / stakeholder
- Technical proposals accepted or overridden by the team (unchallenged proposals stand)
- Residual assumptions explicitly documented

## 8. Workshop update (2026-10-19)

See the Refined Story. Changes to §7 proposals: Font Quicksand (bundled) replaces the system stack; 375 px in scope; light/dark of the lime glassmorphism theme only.
