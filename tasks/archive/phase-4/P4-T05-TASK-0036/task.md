# Task: Implement `forge context build`

## Metadata
- **ID:** TASK-0036
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T05
- **Dependencies:** TASK-0035 (P4-T04, done)

## Objective
Implement `forge context build` to assemble a packet-scoped `ContextBundle` for a task ID, show selected sources in text mode, and emit structured bundle data in JSON mode.

## Why This Task Exists
Phase 4 requires a runnable context assembly path before display/export and model-routing steps. This command is the first CLI entrypoint that assembles selected packet and document sources.

## Scope
- `build_context_bundle(...)` in `services/context_service.py`
- `context build` CLI command in `src/forge/cli/context.py`
- tests for command behavior in `tests/test_context_build_cmd.py`
- no context export yet (P4-T07)
- no context show implementation yet (P4-T06)

## Constraints
- Keep selection minimal and packet-scoped
- Preserve canonical/working selection rules from prior tasks
- Keep CLI behavior aligned with existing command and error patterns

## Escalation Conditions
- If context-tag inference requires canonical changes to selection policy, stop and record the ambiguity
