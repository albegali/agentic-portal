---
artifact_type: functional-requirements
status: approved            # draft | approved
sources:
  - reference/product/vision.md
  - docs/sources/portal-brief.md
  - docs/sources/portal-prototype.dc.html
last_updated: 2026-10-19
---

# Functional requirements

> IDs are stable: never renumber or reuse. Deprecated requirements keep their ID with `Status: deprecated`.
> One heading per requirement (`### FR-01 — …`): tools extract sections by heading.

## Workflow state and navigation

### FR-01 — Next-step state
- **Statement**: The portal shall show the project's current workflow state and next step, computed from the skeleton's tools (`make next`).
- **Rationale**: Orientation without exploring files.
- **Source**: docs/sources/portal-brief.md Intent; docs/sources/portal-prototype.dc.html Overview
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Overview shows lifecycle stage, next command, mode and tier; matches `make next` output.
- **Status**: active

### FR-02 — Plan view
- **Statement**: The portal shall show the release plan and sprints from PLAN.md.
- **Rationale**: See delivery sequence and dependencies.
- **Source**: docs/sources/portal-brief.md Prototype (Plan)
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Releases and sprints rendered; stories link to detail.
- **Status**: active

### FR-03 — Backlog view
- **Statement**: The portal shall list epics and stories from backlog/stories.toml with status, filtering and sorting.
- **Rationale**: Single backlog overview.
- **Source**: docs/sources/portal-brief.md Prototype (Backlog)
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Filter by epic, status, owner mode; counts match `make backlog`.
- **Status**: active

### FR-04 — Story detail
- **Statement**: The portal shall show one story's artifact chain (Story, Analysis, Refined Story, Brief, Spec, RUN, tasks) with status and content.
- **Rationale**: Follow one ID end to end.
- **Source**: docs/sources/portal-brief.md Prototype (Story detail); AGENTS.md §2
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: All chain artifacts of an ID reachable; missing steps shown as pending.
- **Status**: active

### FR-05 — Journal view
- **Statement**: The portal shall show the project journal (context, decisions, learnings, weekly, monthly).
- **Rationale**: Project memory is browsable.
- **Source**: docs/sources/portal-brief.md Prototype (Journal)
- **Priority**: Should
- **UI**: yes
- **Acceptance hints**: Entries listed by date and type.
- **Status**: active

### FR-06 — Command palette
- **Statement**: The portal shall provide a command palette to navigate and launch actions by keyboard.
- **Rationale**: Console-like speed.
- **Source**: docs/sources/portal-brief.md Prototype (command palette)
- **Priority**: Should
- **UI**: yes
- **Acceptance hints**: Palette opens by shortcut; searches screens, stories and actions.
- **Status**: active

## Agent runs

### FR-07 — Launch workflow step
- **Statement**: The portal shall launch a workflow step (e.g. kickoff, requirements, brief, run) by invoking the configured agent CLI headless.
- **Rationale**: Run the workflow without a terminal.
- **Source**: docs/sources/portal-brief.md Decisions (Agents)
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Action on a story/gate starts the CLI with the step's command; refuses when preconditions fail.
- **Status**: active

### FR-08 — Tier model selection
- **Statement**: The portal shall pick the model for a launched step from the step's tier in models.toml for the configured vendor.
- **Rationale**: Respect token discipline.
- **Source**: docs/sources/portal-brief.md Decisions (Agents); AGENTS.md §5
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Chosen model displayed before launch and matches models.toml.
- **Status**: active

### FR-09 — Agent CLI support
- **Statement**: The portal shall support configurable agent CLIs, at least `claude -p` and `codex exec`.
- **Rationale**: Tool-agnostic workflow.
- **Source**: docs/sources/portal-brief.md Decisions (Agents); project.toml tools
- **Priority**: Must
- **UI**: no
- **Acceptance hints**: Switching the configured CLI changes the launched command.
- **Status**: active

### FR-10 — Session streaming
- **Statement**: The portal shall stream the output of a running agent session and keep a history of runs.
- **Rationale**: Observe and audit runs.
- **Source**: docs/sources/portal-brief.md Decisions (Agents); docs/sources/portal-prototype.dc.html Agent runs
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Live output while running; finished runs listed with status, step, model, duration.
- **Status**: active

### FR-11 — Stop at gates
- **Statement**: The portal shall stop a run at every human gate and report that a human decision is pending.
- **Rationale**: Gates are never bypassed.
- **Source**: docs/sources/portal-brief.md Decisions (Human gates); AGENTS.md §3
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Run ends in 'waiting for human' state; gate appears in Approvals.
- **Status**: active

### FR-12 — Cancel run
- **Statement**: The portal shall let the user cancel a running agent session.
- **Rationale**: Control cost and mistakes.
- **Source**: owner decision 2026-10-19
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Cancel terminates the process; run marked cancelled.
- **Status**: active

## Human gates

### FR-13 — Approvals inbox
- **Statement**: The portal shall list all pending human gates (inception approvals, workshop, Spec Ready, RUN strategy, tuning acceptance).
- **Rationale**: Never miss a gate.
- **Source**: docs/sources/portal-brief.md Prototype (Approvals); AGENTS.md §3
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Each gate shows artifact, what is being approved and age.
- **Status**: active

### FR-14 — Approve and request changes
- **Statement**: The portal shall provide approve and request-changes actions that write the change to the artifact exactly as a human edit (e.g. `status: approved`) and record the approval as given by the owner defined in project.toml, with date.
- **Rationale**: Gates as explicit actions.
- **Source**: docs/sources/portal-brief.md Decisions (Human gates); attribution: owner decision 2026-10-19
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Action modifies only the gate field; request-changes records a comment.
- **Status**: active

### FR-15 — Agents cannot pass gates
- **Statement**: The portal shall ensure no agent-launched run can execute an approve action.
- **Rationale**: Hard boundary.
- **Source**: AGENTS.md §3
- **Priority**: Must
- **UI**: no
- **Acceptance hints**: Gate endpoints reject calls originating from agent sessions; tested.
- **Status**: active

### FR-16 — Artifact preview before decision
- **Statement**: The portal shall show the artifact content and diff since last review before a gate decision.
- **Rationale**: Informed approval.
- **Source**: owner decision 2026-10-19
- **Priority**: Must
- **UI**: yes
- **Acceptance hints**: Diff shown for modified artifacts.
- **Status**: active

## Codebase health

### FR-17 — Weak files
- **Statement**: The portal shall surface weak files (e.g. large, complex, frequently changed) of the repository.
- **Rationale**: Find risk hotspots.
- **Source**: docs/sources/portal-brief.md Intent; docs/sources/portal-prototype.dc.html Insights
- **Priority**: Should
- **UI**: yes
- **Acceptance hints**: Ranked list with metric and rationale.
- **Status**: active

### FR-18 — Security findings
- **Statement**: The portal shall surface security findings for the repository.
- **Rationale**: Watch security.
- **Source**: docs/sources/portal-brief.md Intent
- **Priority**: Should
- **UI**: yes
- **Acceptance hints**: Findings with severity and location; source analyzer named.
- **Status**: active

### FR-19 — Untested code
- **Statement**: The portal shall surface untested or poorly covered code.
- **Rationale**: Watch test debt.
- **Source**: docs/sources/portal-brief.md Intent
- **Priority**: Should
- **UI**: yes
- **Acceptance hints**: Coverage gaps by file/package.
- **Status**: active

### FR-20 — Architecture diagrams
- **Statement**: The portal shall display architecture and infrastructure diagrams of the repository.
- **Rationale**: Understand structure.
- **Source**: docs/sources/portal-brief.md Intent; docs/sources/portal-prototype.dc.html Architecture
- **Priority**: Should
- **UI**: yes
- **Acceptance hints**: Diagrams from reference/architecture/ rendered.
- **Status**: active

### FR-21 — Findings to actions
- **Statement**: The portal shall let the user turn a finding into an agent action or backlog story.
- **Rationale**: AI as actions on findings.
- **Source**: docs/sources/portal-brief.md Intent
- **Priority**: Could
- **UI**: yes
- **Acceptance hints**: Action creates a launch request or story draft; no auto-approval.
- **Status**: active

### FR-22 — Analyzer sources
- **Statement**: The portal shall use existing analyzers available from the language's library ecosystem where they exist, installed according to the languages and frameworks selected in /architecture; it builds its own analyzer only where none exists.
- **Rationale**: Avoid duplicating tools.
- **Source**: owner decision 2026-10-19
- **Priority**: Should
- **UI**: no
- **Acceptance hints**: Missing scanner is reported, not fatal.
- **Status**: active

## Portability and setup

### FR-23 — Start with make portal
- **Statement**: The portal shall be distributed to projects as a release bundle pinned and started by `make portal` on localhost.
- **Rationale**: Zero-friction start.
- **Source**: docs/sources/portal-brief.md Decisions (Runtime); distribution: owner decision 2026-10-19
- **Priority**: Must
- **UI**: no
- **Acceptance hints**: Command serves the UI for the current repo.
- **Status**: active

### FR-24 — Any workflow repository
- **Statement**: The portal shall work in any repository using the workflow, including codebases adopted with `make adopt`.
- **Rationale**: Portability.
- **Source**: docs/sources/portal-brief.md Intent
- **Priority**: Must
- **UI**: no
- **Acceptance hints**: Runs against a greenfield and an adopted repo.
- **Status**: active

### FR-25 — Files as source of truth
- **Statement**: The portal shall read state from repository files via the skeleton's tools and write only changes a human or agent could make.
- **Rationale**: No hidden state.
- **Source**: docs/sources/portal-brief.md Decisions (Source of truth)
- **Priority**: Must
- **UI**: no
- **Acceptance hints**: Deleting portal data loses nothing about project state.
- **Status**: active

### FR-26 — Settings view
- **Statement**: The portal shall show and edit project settings (project.toml, models.toml: tiers, tools, language).
- **Rationale**: Configure without editing files.
- **Source**: docs/sources/portal-brief.md Prototype (Settings)
- **Priority**: Should
- **UI**: yes
- **Acceptance hints**: Edits written to the files; validated.
- **Status**: active

### FR-27 — Versioned skeleton contract
- **Statement**: The portal shall consume skeleton tools through a versioned JSON contract and detect incompatible versions.
- **Rationale**: Avoid drift. Contract design (which tools emit JSON, direction tool-to-portal, versioning scheme) is delegated to /architecture (owner decision 2026-10-19).
- **Source**: docs/sources/portal-brief.md Open questions
- **Priority**: Must
- **UI**: no
- **Acceptance hints**: Version mismatch shows a clear message.
- **Status**: active

### FR-28 — Theme
- **Statement**: The portal shall offer dark and light themes.
- **Rationale**: Prototype includes both.
- **Source**: docs/sources/portal-prototype.dc.html (.app.light)
- **Priority**: Could
- **UI**: yes
- **Acceptance hints**: Toggle persists locally.
- **Status**: active

## Open questions
- None open. Resolved on 2026-10-19 by the owner: contract design delegated to /architecture (FR-27); analyzers from existing language tools (FR-22); distribution via bundle pinned by `make portal` (FR-23); approvals attributed to the project.toml owner (FR-14); cancel run and diff preview in the first release (FR-12, FR-16).

## Conflicts between sources
- None found. The brief says the prototype is a reference for look and behaviour, not a spec: items marked assumption go beyond it.
