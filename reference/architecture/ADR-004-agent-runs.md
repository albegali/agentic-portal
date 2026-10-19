---
artifact_type: adr
id: ADR-004
status: accepted
date: 2026-10-19
drivers: [FR-07, FR-08, FR-09, FR-10, FR-11, FR-12, FR-15, NFR-04, NFR-12]
---

# ADR-004 — Agent runs: headless CLI adapters with scope locks on one working tree

## Context
The portal launches the configured agent CLI headless with the tier model from `models.toml` (FR-07, FR-08, FR-09), streams it (FR-10), stops at every gate (FR-11), can cancel (FR-12), and allows parallel runs only when they do not conflict on the codebase (owner, mockup decision). Commands must be allow-listed (NFR-04) and every run audited (NFR-12).

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. Scope locks on one working tree: each run declares a scope (the story's artifact chain + package paths from its Spec/RUN, via `context.py --json`; inception, `/architecture`, `/backlog`, `/release-plan` and repo-wide steps lock everything); overlapping runs queue; after the run, `git status`/`git diff` flags files changed outside the scope | Simple; same tree the human sees; queue matches the mockup | Parallelism only between disjoint stories; undeclared writes are detected after the fact, not prevented | Good |
| B. One git worktree per run, merged after its gate | Real isolation | Merge conflicts, artifacts on unmerged branches, gates on work not in main tree | Weaker for gate flow; candidate for later |

## Decision
Option A (owner-confirmed 2026-10-19). One adapter per CLI (`claude -p`, `codex exec`, …) builds the command line from an allow-list in `workflow/workflow.toml` (step → command) and `models.toml` (tier → model); processes start in their own process group (POSIX) / `CREATE_NEW_PROCESS_GROUP` (Windows) so cancel kills the whole tree. A run ends `at gate` when the step reaches a human gate (detected from the step definition and the agent's exit/output marker), `done`, `failed` or `cancelled`. Out-of-scope writes become a workflow finding on the run.

## Consequences
- Positive: no merge step; runs map 1:1 to the workflow; audit record per run.
- Negative / trade-offs: scope quality depends on Specs/RUNs listing their packages; two runs on the same package wait.
- Follow-up stories: CLI adapters and allow-list; run manager (queue, locks, cancel); post-run scope check.

## Reversibility
Medium: the run manager owns locking; worktrees can be added later as a second strategy behind it.
