---
artifact_type: adr
id: ADR-003
status: accepted
date: 2026-10-19
drivers: [FR-23, FR-24, NFR-09, NFR-10]
---

# ADR-003 — Distribution: pinned release bundle downloaded by `make portal`

## Context
The portal is developed in this repository and must reach every project that uses the workflow, greenfield or adopted (FR-23, FR-24), without Node on the project machine (NFR-09), on macOS, Windows and Linux (NFR-10). The owner confirmed "release bundle pinned by `make portal`".

## Options
| Option | Pros | Cons | Fit to drivers |
|---|---|---|---|
| A. `project.toml [portal] version = "x.y.z"`; `make portal` downloads the release zip (Python server + prebuilt web) from this repository's GitHub Releases (owner-confirmed 2026-10-19) into gitignored `.portal/<version>/`, verifies SHA-256 against the release manifest, starts it | Nothing committed to projects; easy upgrades by changing one line; integrity checked | Network on first run; GitHub Releases as a dependency | Good |
| B. Bundle vendored and committed into each project | Offline | 1–2 MB of built assets in every project history; upgrades are big diffs | Weaker |

## Decision
Option A (owner-confirmed 2026-10-19). The launcher is a stdlib script added to the skeleton (`tools/portal.py`, called by `make portal` and runnable as `python tools/portal.py` on Windows without make); `PORTAL_BUNDLE=<path>` overrides the download for offline or development use.

## Consequences
- Positive: one-line version pin; reproducible; works where `make` is missing.
- Negative / trade-offs: release pipeline (build web, zip, checksum, publish) must exist before the first project can use it; first run needs network.
- Follow-up stories: release pipeline; `tools/portal.py` launcher (upstream); `.portal/` in `.gitignore` via `make adopt`.

## Reversibility
Medium: the launcher hides where the bundle comes from; switching source later touches only the launcher.

## Revisions
- 2026-10-20, owner decisions in chat (AP0106 Spec review): stays on GitHub Releases; launcher Python baseline >= 3.11 (bundle declares its own `requires_python`); manifest = release asset `manifest.json` format 1 (`manifest`, `version`, `asset`, `size`, `sha256`, `requires_python`); running-instance detection via `.portal/run.json` + `/api/health`. Launcher released in agentic-skeleton v1.1.0 (`tools/portal.py`, `make portal`).
- 2026-10-20, owner decisions in `analysis/workshops/WORKSHOP_2026-10-20_AP0102-AP0104-AP0105-AP0107.md` (AP0107): the bundle manifest switches to format 1 now; `portal_server/` at the zip root (no `server/` prefix); the server accepts `--repo` and overrides `server_bind` (no `getfqdn()`); CI runs the real skeleton launcher against the built bundle on Linux, macOS and Windows; every iteration keeps the build green.
