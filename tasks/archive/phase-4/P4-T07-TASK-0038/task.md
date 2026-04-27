# Task: Implement `forge context export`

## Metadata
- **ID:** TASK-0038
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T07
- **Dependencies:** TASK-0035 (P4-T04, done)

## Objective
Implement `forge context export` so packet context can be exported for external coding agents. Text mode must write a single assembled markdown file with a metadata header listing selected sources. JSON mode must emit structured source metadata only.

## Why This Task Exists
Phase 4 requires a portable context export path to support external execution tools while preserving explicit source traceability.

## Scope
- Add markdown export adapter in `src/forge/adapters/export.py`
- Implement `context export` command in `src/forge/cli/context.py`
- Add source metadata helper in `src/forge/services/context_service.py`
- Add command tests in `tests/test_context_export_cmd.py`
- No additional context-selection policy changes

## Constraints
- Use the existing `ContextBundle` assembly path
- Keep export format v1 aligned with Q7 resolution
- `--format json` returns source metadata only (no full content body)

## Escalation Conditions
- If export requires sidecar files or directory bundles beyond single markdown in text mode, stop and record the mismatch
