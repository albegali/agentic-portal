# Project summary — Agentic Portal

> The short context every step reads. Keep it ≤ 60 lines; link to details instead of copying them.

- **What**: A local developer-experience portal on top of the agentic-skeleton workflow (state, plan, backlog, agent runs, human gates, codebase health).
- **For whom**: Product owners, developers, analysts/reviewers and tech leads of repos using the workflow (users beyond the owner are assumptions).
- **Why**: Workflow state and gates live in files and CLI; no overview or one-click control.
- **Type and platforms**: Web app served locally (localhost, one portal per repository); React + Vite + TypeScript static bundle, Python stdlib backend; desktop and mobile browsers from 375 px wide (owner, 2026-10-19), WCAG 2.2 AA.
- **First release**: Screens of the prototype with read/write through skeleton tools, headless agent launch, gates as actions, codebase-health insights. Target date: not stated.
- **Out of scope**: Hosted multi-repo server; chat-style AI.
- **Key constraints**: Python stdlib only on the backend; repo files are the source of truth; localhost security (token, CSRF); portable to adopted codebases.
- **Stack**: Python ≥ 3.14 stdlib server (`server/`) + React/Vite/TS bundle (`web/`); skeleton via versioned JSON contract; SSE; state in `.portal/` — see `reference/architecture/architecture.md` (ADR-001..008, proposed).
- **Owner / approver**: Alberto Galimberti
- **Artifact language**: en

## Domain facts not to forget
- Agents never pass human gates (approvals, workshop, Spec `Ready`, RUN strategy, tuning acceptance).
- The portal launches the agent CLI with the tier model from `models.toml`.
- Skeleton improvements discovered while building go upstream to agentic-skeleton.
- Prototype (`docs/sources/portal-prototype.dc.html`) is the look and behaviour reference for /mockup.

## Where things are
- Vision: `reference/product/vision.md`
- Requirements: `reference/product/functional-requirements.md`, `reference/product/non-functional-requirements.md`
- Mockup: `reference/product/mockup-reference.md`
- Architecture: `reference/architecture/`
- Glossary: `reference/domain/glossary.md`
- Plan: `PLAN.md`
- Sources: `docs/sources/`
