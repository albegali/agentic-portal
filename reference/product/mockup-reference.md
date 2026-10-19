---
artifact_type: mockup-reference
status: approved            # draft | approved
mockup: reference/mockup/agentic-portal.html
last_updated: 2026-10-19
---

# Mockup reference

The mockup is the **reference for behavior**, not for architecture. Look and flows derive from `docs/sources/portal-prototype.dc.html`; the mockup is a standalone single file with sample data about this project (prefix AP). Open it in a browser.

## Screen and function map
| Screen / area | Where in the mockup (JS function) | FR |
|---|---|---|
| Overview: next step, waiting for you, sprint, health | `renderOverview` | FR-01, FR-07, FR-08 |
| Plan: releases and sprints | `renderPlan` | FR-02 |
| Backlog: board/list, owner filter | `renderBacklog` | FR-03 |
| Story detail: artifact chain, gate, next action | `renderStory` | FR-04, FR-07, FR-08, FR-14 |
| Journal | `renderJournal` | FR-05 |
| Command palette (Ctrl/⌘ K) | `openPal`, `palList` | FR-06 |
| Launch a step (tier, model, CLI shown before launch) | `launch`, `scriptFor` | FR-07, FR-08 |
| Agent runs: history, live stream, stop at gate, cancel; parallel runs, queued on file overlap | `renderRuns`, `launch`, `conflictOf`, `release`, `cancel` | FR-10, FR-11, FR-12 |
| Approvals inbox: diff preview, approve, request changes | `renderApprovals` | FR-13, FR-14, FR-16 |
| Insights: weak files, security, untested code; filter by category, group by category or file; finding → agent run | `renderInsights` | FR-17, FR-18, FR-19, FR-21 |
| Architecture diagrams (components, infrastructure; source: generated from code or from ADRs) | `renderArchitecture` | FR-20 |
| Settings: skeleton contract status (mismatch shown only here), agent CLI, tiers, project | `renderSettings` | FR-26, FR-27 |
| Light/dark theme | `render` (theme toggle) | FR-28 |

## Normative vs illustrative
- Normative (must be implemented as shown): agent runs execute in parallel unless their declared files overlap, in which case the later run is queued and starts when the conflicting run ends; "Create a story" from a finding is an agent run; findings can be grouped by category or by file; architecture diagrams switch between generated-from-code and from-ADRs; a portal–skeleton contract mismatch is shown only in Settings; a run ends in "waiting for human" at a gate and the gate appears in Approvals; approve and request-changes record the owner and date; the diff is shown before the decision; the next step shows mode, tier and the model resolved from the tier for the selected CLI; a running session can be cancelled; empty states for Approvals and filters; error state for a missing scanner; keyboard operation of palette, filters, tabs and gates.
- Responsive (owner, 2026-10-19): usable from 375 px wide; below 900 px the navigation becomes a drawer (menu button, closes on Escape or tap outside) and two-column screens stack; below 640 px filters scroll horizontally, story rows put the status under the title, the backlog opens in list view, diagrams stack vertically, touch targets are ≥ 44 px.
- Visual direction (owner, 2026-10-19): Quicksand for UI text (monospace kept for code and paths), lime accent as primary, slightly rounded corners (4–8 px), glass panels with blur and soft shadows.
- Illustrative (sample data, styling, placeholders): all story titles, findings, runs, journal entries, diagrams, model names, timings and the simulated streaming.

## FRs with UI not covered
- FR-09 and FR-15 have no UI (`ui: no`).
- FR-22, FR-23, FR-24, FR-25 have no UI.
- FR-26 covers CLI, tiers and read-only project fields; editing language, prefix and owner is not mocked.

## Decisions (owner, 2026-10-19)
- Contract mismatch: Settings only.
- Finding → story: agent run.
- Parallel runs: allowed only when they do not conflict on the codebase. Feasibility (how a run declares the files it touches, isolation e.g. one git worktree per run) is open for /architecture.
- Insights: both groupings (category, file).
- Architecture: source toggle generated vs ADRs.

## Open UX questions
- How is a conflict detected before a run starts (Spec/RUN file list, package rules) and what if a run touches undeclared files?
