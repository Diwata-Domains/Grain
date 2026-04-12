# Task: Add Homebrew formula and installation documentation

## Metadata
- **ID:** TASK-0089
- **Status:** blocked
- **Phase:** Phase 11 — Distribution and Global Install
- **Backlog:** P11-T05
- **Packet Path:** tasks/P11-T05-TASK-0089/
- **Dependencies:** TASK-0086
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add a Homebrew formula for Grain and document a supported macOS install path alongside uv/pip install methods.

## Why This Task Exists
Phase 11 includes a Homebrew path so macOS users can install Grain globally through a first-class distribution option.

## Scope
- Add a Homebrew formula file under a repo-local contrib path.
- Document brew install usage in README with verification and troubleshooting alignment.
- Validate the formula with a local build-from-source install command.

## Constraints
- Keep distribution work scoped to install path and docs only.
- Do not modify canonical docs.

## Escalation Conditions
- If Homebrew install requires external publish infrastructure not available in-repo, keep scope to local formula + documentation and note follow-up.

## Defer Note
Deferred by operator on 2026-04-11. Resume this task when Homebrew tap/release flow is prioritized.
