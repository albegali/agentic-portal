# Portal brief (kickoff source)

Input for `/kickoff`, `/requirements`, `/mockup` and `/architecture`. Decisions below were taken by the product owner before kickoff; everything else is open.

## Intent
A developer-experience portal on top of the agentic workflow of [agentic-skeleton](https://github.com/albegali/agentic-skeleton): see the repository's workflow state, plan and backlog, launch the workflow commands, pass human gates, and watch codebase health (weak files, security, untested code, architecture and infrastructure diagrams). Portable to any repository that uses the workflow, including existing codebases adopted with `make adopt`. Clean, modern, console-like UX: AI appears as actions on stories, findings and gates, not as a chat.

## Decisions already taken
| Topic | Decision |
|---|---|
| Runtime | Local, one portal per repository (`make portal`, localhost). No hosted multi-repo server for now. |
| Source of truth | The repository files. The portal reads them through the skeleton's tools and writes the same changes a human or agent would. |
| Frontend | React + Vite + TypeScript, shipped as a prebuilt static bundle; Node is needed only to develop the portal. |
| Backend | Python standard library only (same constraint as the skeleton tools). |
| Agents | The portal launches the configured agent CLI headless (`claude -p`, `codex exec`, …) with the model of the step's tier from `models.toml`, streams the session, and stops at every human gate. |
| Human gates | Shown as explicit actions (approve, request changes) that write to the artifact; agents can never pass them. |
| Repository | Developed here, separate from the skeleton; skeleton improvements found while building go upstream. |

## Prototype
`portal-prototype.dc.html` — clickable prototype on sample data (screens: Overview, Plan, Backlog, Story detail, Approvals, Agent runs, Insights, Architecture, Journal, Settings, command palette). It is a design-canvas source file, not a standalone page; treat it as the behaviour and look reference for `/mockup`.
Live version: https://claude.ai/artifact/AtU3txsXME1418B711KWnK (private to the owner).

## Open questions for inception
- Contract between portal and skeleton tools (JSON outputs, versioning).
- How the portal is distributed to projects (release bundle pinned by `make portal`?).
- Which analyzers are built in vs. delegated to scanners installed on the machine.
- Security of a local server that can launch agents and write files (bind to localhost, token, CSRF).
