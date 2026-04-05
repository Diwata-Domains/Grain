# Task: Implement `forge context show`

## Metadata
- **ID:** TASK-0037
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T06
- **Dependencies:** TASK-0036 (P4-T05, done)

## Objective
Implement `forge context show` to display assembled packet context sources for a task ID, including selected packet files and selected canonical/working docs.

## Why This Task Exists
Phase 4 requires an inspectable, display-only context command separate from context build/export so users can verify source selection clearly.

## Scope
- Implement `context show` in `src/forge/cli/context.py`
- Reuse context bundle assembly from `context_service`
- Add command tests in `tests/test_context_show_cmd.py`
- No export file generation in this task

## Constraints
- Keep behavior display-focused and packet-scoped
- Preserve selection rules from existing context domain/service logic
- Follow existing CLI error and JSON/text output patterns

## Escalation Conditions
- If display requirements require changing context selection semantics, stop and record the mismatch
