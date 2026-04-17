# Handoff: TASK-0068

## Final State
`forge workflow run` implemented as a guarded one-step runner: activates a ready task (writes `current_task.md`) or stops at an explicit gate with a machine-readable reason.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0068
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** `forge workflow run` command is implemented, tested (11 tests, 476/476 total), and ready for reviewer inspection.

## What Was Built
- `src/forge/services/workflow_run_service.py` — runner service with activate/gate logic
- `src/forge/cli/workflow.py` — `workflow run` command added (text + JSON output)
- `tests/test_workflow_run_cmd.py` — 11 tests covering all gate conditions and activation

## What Review Should Check
- Gate conditions match Q16 stop-condition contract (blocked, review, phase-gate, validation-conflict, planning, conflicting tasks)
- `current_task.md` is written correctly on activation (task_id, task_path, status: in_progress)
- No state mutation on any gate path — verify `test_workflow_run_does_not_mutate_state_on_gate`
- JSON output shape is stable: `action_taken`, `gate_reason`, `gate_condition`, `task_activated`, `recommended_prompt`, `blocking_reasons`, `affected_artifacts`, `active_phase`, `active_task_id`
- Exit code is 0 for both ok and gated cases; only hard service failure triggers non-zero
- `workflow_run_service.py` does not call any write functions on gate paths

## What Was Not Done
- `--dry-run` flag deferred to P8-T09
- Sentinel verification bridge deferred to P8-T10 (blocked)
- No canonical docs modified

## Known Issues or Follow-ups
- `_find_packet_dir_for_ref` matches by prefix (`P8-T08-`); no collision risk with current naming scheme but worth noting for future phases if task_ref format changes.
- P8-T09 (harden machine-readable outputs + integration tests) should extend coverage across all P8 runner commands together.

## Files Changed
- `src/forge/services/workflow_run_service.py` — new file
- `src/forge/cli/workflow.py` — added `workflow run` command
- `tests/test_workflow_run_cmd.py` — new file, 11 tests
- `docs/working/current_task.md` — updated to TASK-0068
- `docs/working/backlog.md` — P8-T08 status → review
- `tasks/P8-T08-TASK-0068/` — packet created (task.md, context.md, plan.md, deliverable_spec.md, results.md, handoff.md)

## Reviewer Notes
This task completes the Phase 8 runner command surface: `workflow next` → `task next` → `phase next` → `task prepare` → `prompt show` → `workflow run`. P8-T09 (hardening) and P8-T10 (Sentinel bridge, blocked) remain.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- P8-T09: harden machine-readable automation outputs and add runner integration tests across all P8 commands together
