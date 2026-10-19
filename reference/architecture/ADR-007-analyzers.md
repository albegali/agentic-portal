---
artifact_type: adr
id: ADR-007
status: accepted
date: 2026-10-19
drivers: [FR-17, FR-18, FR-19, FR-20, FR-21, FR-22]
---

# ADR-007 — Analyzers: adapters over existing tools, one finding model

## Context
The owner decided that analyzers come from existing tools of each language's ecosystem, installed according to the project's languages and frameworks; the portal builds its own only where none exists (FR-22). Insights groups findings by category and by file; diagrams switch between generated-from-code and from-ADRs (FR-20).

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. Adapter per tool, normalized to one finding model (SARIF-like: id, category, severity, location, tool, message); tool output read from SARIF/JSON where offered; tools detected on PATH or in the project's dev dependencies; missing tools reported, never fatal | Reuses mature tools; one UI model; SARIF already supported by many tools | Each adapter to maintain; results depend on what the machine has | Good |
| B. Portal ships its own analyzers | Uniform results | Reinvents scanners; contradicts owner decision | Poor |

## Decision
Option A. Initial adapter set (built-in = stdlib, no external tool):
| Category | Built-in | Delegated (when installed) |
|---|---|---|
| Weak files | size + git churn ranking (`repo_map.py --json`, `git log`) | radon (Python), eslint complexity rules (JS/TS) |
| Security | secret patterns | semgrep, gitleaks, pip-audit, npm audit, trivy |
| Untested code | test-file heuristic | coverage reports read from file: `coverage.xml`/Cobertura, `lcov.info`, JaCoCo |
| Diagrams | Mermaid generated from `repo_map.py --json` and infra files; Mermaid blocks from ADRs/`architecture.md` | — |
Findings are cached in `.portal/findings.json`; "Create a story" from a finding launches an agent run (`/backlog` with the finding as input).

## Consequences
- Positive: no reinvented scanners; adding a language means adding adapters.
- Negative / trade-offs: results vary by machine; adapter tests need recorded tool outputs.
- Follow-up stories: finding model + built-in analyzers; one story per delegated adapter group; Mermaid rendering in the web app.

## Reversibility
Low cost per adapter; the finding model is the stable part.
