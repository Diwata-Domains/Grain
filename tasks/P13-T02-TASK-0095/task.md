# Task: Codebase scanner service

## Metadata
- **ID:** TASK-0095
- **Status:** done
- **Phase:** Phase 13 — Existing Project Adoption
- **Backlog:** P13-T02
- **Packet Path:** tasks/P13-T02-TASK-0095/
- **Dependencies:** TASK-0094
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** docs_adapter

## Objective
Implement a read-only `CodebaseScanner` service that inspects an existing repository tree and returns a structured `ScanResult` with language detection, adapter signals, key repo files, CI config paths, and existing documentation paths.

## Why This Task Exists
Phase 13 existing-project adoption requires scanner signals before draft canonical generation can begin. `P13-T03` depends directly on scanner output shape and deterministic detection behavior.

## Scope
- Add `ScanResult` domain model in `src/grain/domain/scan_result.py`
- Add `CodebaseScanner` in `src/grain/services/codebase_scanner.py`
- Detect primary languages from file extensions
- Detect applicable adapters (`code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`)
- Detect key files (`README*`, `package.json`, `pyproject.toml`, `Makefile`)
- Detect CI configs (`.github/workflows/*.yml|yaml`, `.gitlab-ci.yml`, `.circleci/config.yml`, Azure pipeline file names)
- Detect existing documentation files and return sorted relative paths
- Add focused unit tests in `tests/test_codebase_scanner.py`

## Constraints
- Scanner must be read-only and deterministic
- Scanner must ignore common generated/dependency directories
- Output must be additive data only; no packet generation or doc mutation in this task

## Escalation Conditions
- If scanner requirements require canonical schema updates for `ScanResult`, stop and route via `change_proposals.md`
