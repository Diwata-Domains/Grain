# Task: Implement agent enforcement — workflow guard, hooks, resume prompt, PROJECT_RULES

## Metadata
- **ID:** TASK-0205
- **Status:** done
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T02
- **Packet Path:** tasks/P31-T02-TASK-0205/
- **Dependencies:** TASK-0204
- **Primary Adapter:** code

## Objective
Implement the 6-layer agent enforcement model from `docs/canonical/enforcement_spec.md`. All primary enforcement (Layers 1–3) must work with zero AI involvement.

## Implementation Steps

### Layer 1 — Harden workflow state machine
File: `src/grain/services/workflow_service.py`
1. Add `packet_required` stop reason: when `current_task.md` is unset/none AND ready tasks exist, route to `packet_required` instead of `task_execute`. Output includes ready task IDs and create commands.
2. Done-task stale-pointer fix: if `current_task.md` points to `done` task, route to `phase_boundary` or `packet_required`, never `task_execute`.
3. `task_execute` output always includes `task_id`, `packet_path`, `task_title`.
4. `no_execution_artifacts` warning when in_progress packet has stub-only results.md.

### Layer 2 — `grain workflow guard` command
Files: `src/grain/services/guard_service.py` (new), `src/grain/cli/workflow.py`
Checks: `packet_open`, `results_not_stub`, `phase_alignment`, `implementation_ahead_of_packet`, optional `dev_alignment` (`--check-dev-alignment`), optional `docs_health` (`--check-docs`).
Output: `grain --format json workflow guard` returns structured findings.
Flags: `--strict`, `--check-docs`, `--check-external`, `--format`.

### Layer 3 — Git hooks
Files: `src/grain/services/hooks_service.py` (new), `src/grain/cli/hooks.py` (new)
Commands: `grain hooks install`, `grain hooks uninstall`, `grain hooks status`
Pre-commit hook: runs `grain workflow guard --strict`, blocks on violations, skips metadata-only commits, `GRAIN_SKIP_GUARD=1` escape hatch with auto-notes add.
Post-checkout hook: writes `.grain/last_workflow_state.json` from `grain workflow next` output.

### Layer 4 — `prompts/workflow.resume.md`
File: `src/grain/data/runtime/prompts/workflow.resume.md` (new seed file)
Content: agent-agnostic session resume protocol. No AI-specific syntax. References `.grain/last_workflow_state.json` as fast path. Degraded path if `grain workflow next` fails.
Also: update `grain init` to seed this file via `_SEED_FILE_SOURCES`.

### Layer 5 — PROJECT_RULES.md hard rules
File: `src/grain/data/runtime/PROJECT_RULES.md`
Add: hard rule section (no implementation without open packet), session start checklist (3 steps).

### Layer 6 — AGENTS.md block
File: `src/grain/services/agents_service.py` (or wherever AGENTS.md generation lives)
Add hard constraint header, reference `workflow.resume.md` by path, remove Claude-specific syntax.

## Deliverable
- All 6 enforcement layers implemented and tested
- `grain hooks install` writes working pre-commit and post-checkout hooks
- `grain workflow guard` returns structured JSON output
- `workflow.resume.md` seeded by `grain init`
- Tests for guard checks, hook installation, state machine changes

## Constraints
- All Layer 1–3 enforcement must work without an agent present
- `GRAIN_SKIP_GUARD=1` must log to tooling_notes (can stub `grain notes add` if not yet implemented — write directly to file)
- Do not break existing `grain workflow next` routing for the common case (open in_progress packet)
