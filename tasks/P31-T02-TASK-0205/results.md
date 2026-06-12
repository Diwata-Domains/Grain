# Results — TASK-0205

## Summary

Implemented all 6 enforcement layers. 1024 tests pass. `grain workflow guard` and `grain hooks install/uninstall/status` are live.

## Deliverables

### Layer 1 — Hardened workflow state machine
- `packet_required` stop reason: when `current_task.md` is none AND 1 ready task exists, workflow returns `ok=True, stop_reason="packet_required"` with the ready task and a `grain task create` command. Agents must create a packet before executing — no silent skip to execution.
- `no_execution_artifacts` warning: added to `execution_in_flight` when results.md is absent; also populates `task_packet_path` for direct agent reference.
- `WorkflowEvaluation` extended with `task_packet_path`, `task_title`, `warnings` fields.
- `WorkflowTaskState` extended with `task_id` field; backlog parser now reads `TASK-ID:` line.
- `workflow run`, `workflow loop`, `task next`, `workflow explain`, `workflow diagnostics` all updated to handle `packet_required` correctly.

### Layer 2 — `grain workflow guard`
- New service: `src/grain/services/guard_service.py`
- 4 active checks: `packet_open`, `results_not_stub`, `phase_alignment`, `implementation_ahead_of_packet`
- 2 stub checks: `dev_alignment` (T06), `docs_health` (T04)
- `--strict` treats warnings as violations; `--check-docs` and `--check-dev-alignment` enable optional checks
- `grain --format json workflow guard` returns structured JSON with status/checks array
- Exit code 1 on violation

### Layer 3 — Git hooks
- New service: `src/grain/services/hooks_service.py`
- New CLI: `src/grain/cli/hooks.py` — `grain hooks install/uninstall/status`
- Pre-commit hook: runs `grain workflow guard --strict`, blocks on violations, skips metadata-only commits, `GRAIN_SKIP_GUARD=1` escape hatch writes to tooling_notes.md
- Post-checkout hook: writes `.grain/last_workflow_state.json`, warns on `stale_task_pointer`
- Idempotent install — re-running is safe; non-grain hooks are never touched

### Layer 4 — `prompts/workflow.resume.md`
- New seed file: `src/grain/data/prompts/workflow.resume.md`
- Agent-agnostic session resume protocol (4 steps: read state, verify packet, create if needed, proceed)
- Degraded path documented (fall back to current_task.md if grain fails)
- Added to `_SEED_FILE_SOURCES` in `init_service.py`

### Layer 5 — PROJECT_RULES.md hard rules
- Added `## 2. Hard Rules — These Are Not Suggestions` section with 4 numbered rules
- Rules cover: no implementation without open packet, session start checklist, pre-commit enforcement, tooling friction logging

### Layer 6 — AGENTS.md block
- Updated `_grain_block()` in `agents_md_service.py`
- Hard constraint header: "You MUST NOT create or modify implementation files without an open packet"
- References `prompts/workflow.resume.md` by path
- Fixed `--format` global flag order in block
- Agent-agnostic: no Claude-specific syntax

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
