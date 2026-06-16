# Handoff — TASK-0205

## What Was Done

All 6 enforcement layers are implemented and tested (1024 tests pass):

1. **Layer 1 — Workflow state machine** — `packet_required` stop reason (ok=True) routes agents to create a packet before executing. `stale_task_pointer` stop reason replaces silent reset. `WorkflowEvaluation` extended with `task_packet_path`, `task_title`, `warnings`. `WorkflowTaskState` extended with `task_id`.

2. **Layer 2 — `grain workflow guard`** — `src/grain/services/guard_service.py` (new). 4 active checks: `packet_open`, `results_not_stub`, `phase_alignment`, `implementation_ahead_of_packet`. `--strict` elevates warnings to violations. Exit code 1 on violation.

3. **Layer 3 — Git hooks** — `src/grain/services/hooks_service.py` (new), `src/grain/cli/hooks.py` (new). `grain hooks install/uninstall/status`. Pre-commit runs guard --strict; `GRAIN_SKIP_GUARD=1` logs to tooling_notes.md. Post-checkout writes `.grain/last_workflow_state.json`.

4. **Layer 4 — `prompts/workflow.resume.md`** — New seed file. Agent-agnostic 4-step session resume protocol. Seeded by `grain init`.

5. **Layer 5 — PROJECT_RULES.md hard rules** — `## 2. Hard Rules — These Are Not Suggestions` section with 4 numbered rules.

6. **Layer 6 — AGENTS.md block** — Hard constraint header added; references `workflow.resume.md`; `--format` flag order fixed; agent-agnostic language throughout.

## State Left For Next Task

- `grain hooks install` is opt-in — not auto-installed. Users invoke it manually.
- `dev_alignment` guard check is a stub deferred to T06 (`grain doctor`).
- `docs_health` guard check is a stub deferred to T04 (`grain docs audit`).
- Branch policy enforcement (T08) depends on this task — guard infrastructure is ready for it.

## Files Changed

Core services: `workflow_service.py`, `guard_service.py` (new), `hooks_service.py` (new), `agents_md_service.py`, `workflow_run_service.py`, `workflow_loop_service.py`, `workflow_diagnostics_service.py`, `init_service.py`.
CLI: `workflow.py`, `hooks.py` (new), `task.py`, `__init__.py`.
Data: `workflow.resume.md` (new), `PROJECT_RULES.md`.
Domain: `workflow.py`.
Tests: 10+ test files updated/added.
