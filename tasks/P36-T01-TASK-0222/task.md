# Task: Reconcile source version + ship 0.5.0

## Metadata
- **ID:** TASK-0222
- **Status:** ready
- **Mode:** simple
- **Phase:** Phase 36 — v0.5.0 Release Readiness & Fleet Hardening
- **Backlog:** P36-T01 — Reconcile source version + ship 0.5.0 (tag push credit-blocked)
- **Packet Path:** tasks/P36-T01-TASK-0222/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Ship grain-kit 0.5.0 to PyPI. The release was fully prepared (version bump, CHANGELOG,
local tag `grain-v0.5.0` at `ff8d06c`) but the tag was never pushed, so the
`release-python.yml` pipeline (triggers on `grain-v*` tag push) has never run for 0.5.0.
The original blocker — exhausted GitHub Actions credits — has cleared (operator deploys
ran successfully on 2026-07-03). Run the release pre-flight from the 0.5.0 audit
(`docs/working/grain-audit-0.5.0.md` §3), fix anything that ships into immutable PyPI
metadata, then push the tag and verify the pipeline publishes.

## Why This Task Exists
Backlog P36-T01/P36-T03/P36-T04; audit §3 "PyPI-publish blockers". Strategic framing from
the audit: "a tool that isn't installable isn't first-class" — the familiars architecture
depends on grain being a pinnable dependency.

## Scope
- Verify source version coherence: `pyproject.toml` version vs installed vs tag vs CHANGELOG; confirm `grain doctor` no longer reports the 0.1.0/0.5.0 mismatch
- Fix `pyproject [project.urls]` to point at `Diwata-Domains/Grain` (immutable PyPI metadata) — folds in P36-T03
- Clean stale `dist/` artifacts (0.4.0 wheel); `twine check` the 0.5.0 artifacts — folds in P36-T04
- Confirm `PYPI_TOKEN_GRAIN` + `SYNC_TOKEN` secrets exist and `release-python.yml` triggers on `grain-v*`
- Push the `grain-v0.5.0` tag (human-gated) and watch the pipeline through to PyPI
- Out of scope: heavy-deps-to-extras split (P36-T02, next release), Homebrew formula, staleness feature

## Constraints
- Tag push publishes to PyPI — operator confirms before the push (irreversible surface)
- If `[project.urls]` fix requires re-tagging, move the tag to the fixed commit before pushing (tag was never on the remote, so this is safe)
- No `--force` operations; no changes beyond the release-blocking items

## Escalation Conditions
- Release workflow fails at publish (token/permissions) — needs operator's PyPI account
- Actions credits exhausted again
- Version incoherence that requires deciding what 0.5.0 actually contains
