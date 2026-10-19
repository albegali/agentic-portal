# Glossary

| Term | Definition | Not to be confused with | Source |
|---|---|---|---|
| Portal | Local web console for one repository that uses the workflow | Hosted multi-repo server | brief |
| agentic-skeleton | The workflow/skeleton repository the portal sits on | The portal repository | brief |
| Workflow | Lifecycle inception → analysis → delivery driven by step files and commands | A CI pipeline | AGENTS.md |
| Human gate | Approval point only a human can pass (approve, request changes) | Automated check | brief |
| Tier | fast / balanced / deep, mapped to a model per vendor in `models.toml` | Model name | AGENTS.md |
| Headless agent run | Agent CLI invoked non-interactively (`claude -p`, `codex exec`) and streamed | Chat session | brief |
| Adopt | `make adopt`: apply the workflow to an existing codebase | Greenfield kickoff | brief |
| Prototype | `portal-prototype.dc.html`, clickable design-canvas reference | Standalone page | brief |
| Insights | Codebase-health views: weak files, security, untested code | Workflow metrics | brief |
| Contract | Versioned JSON envelope (`contract: 1.x`) emitted by skeleton tools with `--json` and read by the portal | Internal tool functions | ADR-002 |
| Run scope | Files and packages a run may touch; overlapping scopes queue | Story scope in the Spec | ADR-004 |
| Scope lock | Lock held by a running agent run on its scope | git lock | ADR-004 |
| Finding | Normalized analyzer result: category, severity, location, tool | Review finding | ADR-007 |
| `.portal/` | Gitignored directory with portal-only state (runs, logs, findings, bundle) | Project state | ADR-008 |
| Session token | Random secret created at portal start, required on every API call | Agent API keys | ADR-006 |
| SSE | Server-Sent Events: one-way HTTP stream used for run output and state changes | WebSocket | ADR-005 |
