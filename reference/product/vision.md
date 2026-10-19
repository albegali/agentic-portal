---
artifact_type: vision
status: approved            # draft | approved
owner: Alberto Galimberti
sources:
  - docs/sources/portal-brief.md
  - docs/sources/portal-prototype.dc.html
last_updated: 2026-10-19
---

# Vision — Agentic Portal

## 1. Problem
The agentic-skeleton workflow lives in files and CLI commands (`make next`, slash commands, step files). State, plan, backlog, pending human gates and codebase health are only visible by running scripts or reading Markdown/TOML. *(From brief: intent.)*
- Cost of the status quo (assumption): slow orientation at session start, human gates missed or delayed, no overview of codebase health (weak files, security, untested code, diagrams).

## 2. Why now
The skeleton exists and can already adopt existing codebases (`make adopt`); a visual layer makes the workflow usable beyond the people who know its commands. Deadline: not stated. *(Open question.)*

## 3. Target users
| User | Job to be done | Pain today |
|---|---|---|
| Product owner / approver | See where the project stands, approve or request changes at gates | Must read files and edit `status:` by hand *(assumption)* |
| Developer using agents | Launch the next workflow step with the right model, follow the run | Terminal-only; context switching *(assumption)* |
| Analyst / reviewer | Browse stories, analyses, findings | Navigation across many files *(assumption)* |
| Tech lead | Watch codebase health and architecture | No consolidated view *(assumption)* |

## 4. Product statement
For teams working with the agentic-skeleton workflow who need visibility and control, Agentic Portal is a local developer-experience console that shows workflow state, plan, backlog and codebase health, launches workflow commands and exposes human gates as explicit actions. Unlike the terminal and raw files, it gives one console-like view where AI appears as actions on stories, findings and gates, not as a chat.

## 5. Outcomes and success metrics
No metrics were given; proposed ones are assumptions for the owner to confirm.
| Outcome | Metric | Baseline | Target | How measured |
|---|---|---|---|---|
| Faster orientation | Time to know next step and open gates | TBD | TBD | Owner test on a real repo |
| Gates handled through the portal | Share of gates passed via portal | 0 | TBD | Journal / artifact history |
| Portability | Repos running the portal without changes | 0 | ≥ 2 (incl. one adopted codebase) *(assumption)* | Manual check |

## 6. Scope
### In scope (first release)
- Local portal, one per repository, started with `make portal` on localhost.
- Screens from the prototype: Overview, Plan, Backlog, Story detail, Approvals, Agent runs, Insights, Architecture, Journal, Settings, command palette.
- Read state through the skeleton's tools; write the same changes a human or agent would.
- Launch the configured agent CLI headless (`claude -p`, `codex exec`, …) with the tier model from `models.toml`, stream the session, stop at every human gate.
- Human gates as actions (approve, request changes) that write to the artifact; agents can never pass them.
- Codebase health: weak files, security, untested code, architecture and infrastructure diagrams.
### Out of scope
- Hosted multi-repo server.
- Chat-style AI interface.
### Later
- Hosted / multi-repo deployment *(brief: "for now" not)*.
- Further analyzers beyond the first built-in set.

## 7. Constraints
- Time / milestones: not stated.
- Budget / team: not stated.
- Regulatory / privacy: a local server that can launch agents and write files must be secured (localhost bind, token, CSRF); no secrets or personal data in logs.
- Systems to integrate: agentic-skeleton tools and files (source of truth); agent CLIs.
- Technology mandates: frontend React + Vite + TypeScript shipped as a prebuilt static bundle (Node only to develop the portal); backend Python standard library only; developed in this repository, separate from the skeleton (improvements go upstream); portable to any repo using the workflow, including adopted codebases.

## 8. Assumptions to validate
- [High] The skeleton's tools can expose state as stable JSON (contract and versioning not yet defined).
- [High] A localhost server with token and CSRF protection is an acceptable security level for launching agents and writing files.
- [Medium] Headless agent CLIs expose a streamable session sufficient for the "Agent runs" screen.
- [Medium] A prebuilt bundle can be distributed to projects and pinned by `make portal`.
- [Medium] Users listed in §3 and their pains are as assumed.

## 9. Risks
- Portal and skeleton drift apart without a versioned contract.
- A local server with write and agent-launch capability is an attack surface.
- Built-in analyzers duplicate scanners already on the machine.

## 10. Open questions
- Contract between portal and skeleton tools (JSON outputs, versioning).
- Distribution of the portal to projects (release bundle pinned by `make portal`?).
- Which analyzers are built in vs. delegated to installed scanners.
- Security model of the local server.
- Target date, team size, success metric targets.
