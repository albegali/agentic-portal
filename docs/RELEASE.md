# Release procedure

The portal is released as a bundle on GitHub Releases (ADR-003); projects pin it with `project.toml [portal] version` and start it with `make portal` (skeleton launcher `tools/portal.py`).

## Cut a release (owner)
1. On an up-to-date `main` (CI green): set `VERSION` (e.g. `0.1.0`), merge it.
2. `git tag v$(cat VERSION) && git push origin v$(cat VERSION)`. The tag is the release; no release branch (`delivery/guide/git.md`).
3. The `portal-release` workflow runs; read its result in the Actions tab.

## What the pipeline checks before it publishes (`.github/workflows/release.yml`)
- Tag equals `v$(cat VERSION)` and the tagged commit is reachable from `origin/main` (`scripts/release_checks.py tag|ancestor`).
- No release exists yet for the tag: an existing release is never overwritten. To republish, bump `VERSION` and tag again.
- Lint, web build and the full test suite pass.
- The built zip matches its `manifest.json` (format 1: `manifest`, `version`, `asset`, `size`, `sha256`, `requires_python`; plus `contract_built_for`), has only `portal_server/`, `web/dist/` and `VERSION` at its root, safe entry names and no tests or caches (`release_checks.py verify`).
- `0.*` versions are published with `--prerelease` until R1 closes; `1.0.0` is the R1 release.

The same build and verification run as `release-dry-run` on pull requests that touch `scripts/build_bundle.py`, `scripts/release_checks.py` or `release.yml`; job `launcher` runs the real skeleton launcher against the built bundle on Linux, macOS and Windows (`scripts/tests/launcher_smoke.py`).

## Verify a published release
- The release lists `agentic-portal-<version>.zip` and `manifest.json`.
- `python scripts/release_checks.py verify agentic-portal-<version>.zip manifest.json` (download both next to each other; run from a checkout of the tagged commit so `VERSION` matches).
- In a project: pin `version` in `project.toml [portal]`, run `make portal`.
- NFR-10 browsers: the owner checks the OS × browser matrix per release; CI only proves that the server starts on the three OSes.
