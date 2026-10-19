---
artifact_type: non-functional-requirements
status: approved            # draft | approved
sources:
  - reference/product/vision.md
  - docs/sources/portal-brief.md
last_updated: 2026-10-19
---

# Non-functional requirements

> One heading per requirement (`### NFR-01 — …`). Make every target measurable when possible.

## Security

### NFR-01 — Localhost binding
- **Statement**: The server shall bind only to the loopback interface.
- **Target**: No listener on non-loopback addresses
- **Verification**: Test + port scan
- **Source**: docs/sources/portal-brief.md Open questions; confirmed: owner decision 2026-10-19
- **Priority**: Must
- **Status**: active

### NFR-02 — Request authentication
- **Statement**: Every API call shall require a per-session token; state-changing calls shall be CSRF-protected and origin-checked.
- **Target**: 100% of API routes reject missing/invalid token
- **Verification**: Automated tests
- **Source**: docs/sources/portal-brief.md Open questions; confirmed: owner decision 2026-10-19
- **Priority**: Must
- **Status**: active

### NFR-03 — Write scope
- **Statement**: The server shall write only inside the repository and only to workflow artifacts and settings.
- **Target**: Writes outside repo root: 0
- **Verification**: Path-traversal tests
- **Source**: assumption; confirmed: owner decision 2026-10-19
- **Priority**: Must
- **Status**: active

### NFR-04 — Agent launch control
- **Statement**: Agent processes shall be launched only from allow-listed commands defined in configuration.
- **Target**: No arbitrary command execution via API
- **Verification**: Review + tests
- **Source**: assumption; confirmed: owner decision 2026-10-19
- **Priority**: Must
- **Status**: active

## Privacy

### NFR-05 — No secrets in logs
- **Statement**: Logs and streamed sessions stored by the portal shall not contain secrets or personal data.
- **Target**: Redaction applied to known secret patterns
- **Verification**: Tests with seeded secrets
- **Source**: AGENTS.md §3
- **Priority**: Must
- **Status**: active

## Performance

### NFR-06 — Screen load
- **Statement**: Screens shall render within an acceptable time on a repository of typical size.
- **Target**: < 1 s after data load for repos up to ~500 stories/files (assumption)
- **Verification**: Measured on sample repo
- **Source**: assumption, accepted for now; to be assessed later (owner decision 2026-10-19)
- **Priority**: Should
- **Status**: active

### NFR-07 — Stream latency
- **Statement**: Agent output shall appear in the UI with low latency.
- **Target**: < 500 ms from process output (assumption)
- **Verification**: Manual/automated timing
- **Source**: assumption, accepted for now; to be assessed later (owner decision 2026-10-19)
- **Priority**: Should
- **Status**: active

## Compatibility and platforms

### NFR-08 — Backend dependencies
- **Statement**: The backend shall use only the Python standard library.
- **Target**: 0 third-party runtime dependencies
- **Verification**: Dependency check in CI
- **Source**: docs/sources/portal-brief.md Decisions (Backend)
- **Priority**: Must
- **Status**: active

### NFR-09 — Prebuilt frontend
- **Statement**: The frontend shall ship as a prebuilt static bundle; Node shall be needed only to develop the portal.
- **Target**: `make portal` works without Node
- **Verification**: Run on machine without Node
- **Source**: docs/sources/portal-brief.md Decisions (Frontend)
- **Priority**: Must
- **Status**: active

### NFR-10 — OS and browsers
- **Statement**: The portal shall run on macOS, Windows and Linux, in the latest 2 versions of the most used browsers (Chrome, Edge, Safari, Firefox and other Chromium-based browsers).
- **Target**: 100% of screens functional on that OS × browser matrix
- **Verification**: Manual matrix
- **Source**: owner decision 2026-10-19
- **Priority**: Must
- **Status**: active

## Accessibility

### NFR-11 — WCAG compliance
- **Statement**: The UI shall comply with WCAG, including keyboard operability and sufficient contrast in both themes.
- **Target**: WCAG 2.2 level AA (owner: "WCAG compliant"; version and level assumed)
- **Verification**: Audit tool + manual
- **Source**: owner decision 2026-10-19
- **Priority**: Must
- **Status**: active

## Observability

### NFR-12 — Run audit trail
- **Statement**: Each agent run shall record step, model, start/end, outcome and who triggered it.
- **Target**: 100% of runs recorded
- **Verification**: Test
- **Source**: assumption
- **Priority**: Should
- **Status**: active

## Maintainability

### NFR-13 — Contract versioning
- **Statement**: The portal–skeleton interface shall be versioned and covered by contract tests.
- **Target**: Contract tests in CI
- **Verification**: CI
- **Source**: docs/sources/portal-brief.md Open questions
- **Priority**: Must
- **Status**: active

### NFR-14 — Repository separation
- **Statement**: The portal shall be developed in this repository, separate from the skeleton; skeleton changes go upstream.
- **Target**: No skeleton files modified locally
- **Verification**: Review
- **Source**: docs/sources/portal-brief.md Decisions (Repository)
- **Priority**: Must
- **Status**: active

## Resource usage

### NFR-15 — Idle footprint
- **Statement**: The idle portal shall use few resources.
- **Target**: < 100 MB RAM idle (assumption)
- **Verification**: Measurement
- **Source**: assumption
- **Priority**: Could
- **Status**: active

## Open questions
- [Medium] Performance targets (NFR-06, NFR-07) accepted for now; reassess on real repositories.
- [Low] WCAG version and level: AA on 2.2 assumed (NFR-11).
- [Low] Idle resource limit (NFR-15) still an assumption.
