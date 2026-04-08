# Handoff: TASK-0066

## Final State
`forge task prepare` is implemented and packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0066
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added task-level readiness checks for packet and prompt prerequisites with text/json outputs.

## What Was Built
- New task-prepare service for packet prerequisite checks.
- New `task prepare` CLI command.
- Command tests for readiness, missing prerequisites, JSON contract, and missing packet behavior.

## What Review Should Check
- Command behavior is read-only and does not modify packet/workflow docs.
- Missing prerequisites are surfaced explicitly and consistently in text/json output.
- Prompt recommendation behavior for `review` vs non-review task status is correct.

## What Was Not Done
- `forge prompt show` implementation (`P8-T07`)
- `forge workflow run` implementation (`P8-T08`)
- Canonical workflow contract changes

## Known Issues or Follow-ups
- As additional task statuses are introduced, prompt recommendation mapping may need expansion.

## Files Changed
- `src/forge/services/task_prepare_service.py` — new prerequisite check service
- `src/forge/cli/task.py` — new `task prepare` command
- `tests/test_task_prepare_cmd.py` — command tests
- `docs/working/backlog.md` — `P8-T06`/`P8-T07` status-readiness updates, then close transition
- `docs/working/current_focus.md` — immediate-goal updates, then shifted to `P8-T07`
- `docs/working/current_task.md` — active task pointer cleared at close
- `tasks/P8-T06-TASK-0066/task.md` — packet metadata/scope
- `tasks/P8-T06-TASK-0066/context.md` — packet context
- `tasks/P8-T06-TASK-0066/plan.md` — packet plan
- `tasks/P8-T06-TASK-0066/deliverable_spec.md` — deliverable contract
- `tasks/P8-T06-TASK-0066/results.md` — packet results
- `tasks/P8-T06-TASK-0066/handoff.md` — handoff

## Reviewer Notes
This command is advisory and validation-oriented; it does not create missing artifacts.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Implement `P8-T07` (`forge prompt show`) using the same machine-readable output contract style.
