# Current week — notes

## 2026-10-19 — New capabilities to add (owner input, not yet in requirements/backlog)

1. **AI autonomy level (1–5)**
   - 1: the AI makes no decisions on its own and asks the user every question it needs answered to proceed; human review at every step.
   - 2–4: autonomy grows step by step; the AI takes decisions on its own from the simplest to the most complex, depending on the level.
   - 5: fully autonomous; the human gives the prompt of what to build, the AI organizes its agents and works until completion.
   - Open point: level 5 conflicts with the hard boundary "agents never pass a human gate" (AGENTS.md §3, FR-15, AP0404). We need to decide which gates, if any, a level can delegate, and how that delegation is recorded and audited.
   - Open point: we need to define which decisions belong to which level (decision taxonomy).

2. **Model effort selection**
   - The user picks the model's reasoning effort in model selection (default per tier in models.toml / Settings) and can override it for a single task/run.

Next: `/requirements` (new FRs) → `/backlog` (stories, likely EP-03/EP-06) → `/release-plan`. Each step needs human approval.
