# Task: Finalize packaging metadata and build configuration

## Metadata
- **ID:** TASK-0085
- **Status:** done
- **Phase:** Phase 11 — Distribution and Global Install
- **Backlog:** P11-T01
- **Packet Path:** tasks/P11-T01-TASK-0085/
- **Dependencies:** TASK-0084
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Finalize packaging metadata in `pyproject.toml` and verify a clean wheel build from `src/` layout with the `grain` entry point and no dev/test artifact leakage.

## Why This Task Exists
Phase 11 begins with distribution readiness. Packaging metadata quality and build correctness are prerequisites for PyPI and install-path tasks.

## Scope
- Add missing package metadata fields in `pyproject.toml` (description, readme, license, URLs, keywords, classifiers).
- Keep `grain` script entry point intact.
- Build wheel and verify produced artifact contents are package-only and do not include dev/test directories.

## Constraints
- Keep changes limited to packaging/build metadata and verification artifacts for this task.
- Do not modify canonical docs.

## Escalation Conditions
- If packaging metadata requires canonical policy change, stop and log proposal candidate.
- If wheel includes unexpected dev artifacts after configuration changes, stop and record blocker details.
