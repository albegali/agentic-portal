---
artifact_type: adr
id: ADR-006
status: accepted
date: 2026-10-19
drivers: [NFR-01, NFR-02, NFR-03, NFR-04, NFR-05, FR-15]
---

# ADR-006 — Local server security model

## Context
A local server that launches agents and writes files is an attack surface: other local processes, malicious web pages (CSRF, DNS rebinding) and the agents it launches (FR-15: agents never pass gates). NFR-01..05 are confirmed by the owner.

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. Loopback bind + random session token + Host/Origin checks + allow-lists + token withheld from agents | Covers browser attacks and rebinding; no accounts | Does not stop a malicious process of the same OS user that can read the browser | Good for a local dev tool |
| B. A + OS-level auth (e.g. Unix socket permissions, OS keychain) | Stronger against local processes | Cross-platform complexity (Windows) | Over-engineered for R1 |

## Decision
Option A:
- bind `127.0.0.1` only, random free port (NFR-01);
- a 256-bit token generated at start, printed once in the launch URL fragment (`#token=…`, never in logs or files), kept by the web app in `sessionStorage`, sent as `Authorization: Bearer`; every API route rejects missing/invalid tokens (NFR-02);
- `Host` must be `127.0.0.1:<port>`/`localhost:<port>` and `Origin` must match on state-changing requests (CSRF, DNS rebinding);
- writes only through the skeleton commands (ADR-002), with paths resolved and checked to stay inside the repository root (NFR-03);
- agent commands only from the allow-list (ADR-004, NFR-04);
- agent processes get an environment without the token and no portal URL; gate endpoints additionally require a fresh confirm nonce issued to the UI (FR-15);
- secret redaction on run logs before they are written or streamed (NFR-05).

## Consequences
- Positive: meets NFR-01..05 with stdlib only.
- Negative / trade-offs: reopening the browser needs the URL from the terminal (or `make portal` reopens it).
- Follow-up stories: auth middleware + host/origin checks; redaction filter; security tests (NFR-02 100% routes).

## Reversibility
Low cost: contained in the server's request pipeline.

## Revisions
- 2026-10-20, owner decisions in `analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md` (AP0102): the token **may be stored in a file** if it is not readable by other users or applications: gitignored `.portal/` file, POSIX mode 0600, Windows `icacls` restricted to the current user (best effort, warning on failure); no encryption with a co-located key and no third-party keyring (NFR-08). The launcher generates the token, writes the file, passes it to the server as `PORTAL_TOKEN` and opens `/#token=…`; a reused running portal reads the token from the file. This supersedes "never in logs or files" for that one file (logs still never contain it). `GET /api/health` stays unauthenticated (Host-checked, no repository data) as a documented exception to NFR-02; every other `/api` route requires the token. The launcher change is upstream (AP0110).
