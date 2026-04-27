# Handoff: TASK-0063

## Final State
`forge workflow next` is implemented and packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0063
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added workflow command surface for evaluator decisions with text and JSON output plus command tests.

## What Was Built
- New `workflow` command group with `workflow next`.
- `workflow next` integration with read-only evaluator to report one next action or explicit stop reason.
- Command tests covering success path, stop path, and JSON payload shape.

## What Review Should Check
- Command behavior remains read-only and does not mutate any task/working docs.
- Stop conditions are surfaced as explicit `stop_reason`/`blocking_reasons`, not hidden failures.
- JSON output fields are stable and consistent with evaluator contract.

## What Was Not Done
- `forge task next` implementation (`P8-T04`)
- `forge phase next`, `forge task prepare`, `forge workflow run` implementation
- Canonical workflow-spec updates

## Known Issues or Follow-ups
- Next CLI workflow commands should reuse the same evaluator result envelope for consistency.

## Files Changed
- `src/forge/cli/workflow.py` — workflow group + next command
- `src/forge/cli/__init__.py` — command registration
- `src/forge/services/workflow_service.py` — import-cycle-safe command-result creation
- `tests/test_workflow_next_cmd.py` — workflow next CLI tests
- `docs/working/backlog.md` — `P8-T03` status and `P8-T04` readiness updates, then close transition
- `docs/working/current_focus.md` — immediate-goal updates, then shifted to `P8-T04`
- `docs/working/current_task.md` — active packet pointer cleared at close
- `tasks/P8-T03-TASK-0063/task.md` — packet metadata/scope
- `tasks/P8-T03-TASK-0063/context.md` — packet context
- `tasks/P8-T03-TASK-0063/plan.md` — packet plan
- `tasks/P8-T03-TASK-0063/deliverable_spec.md` — packet deliverable contract
- `tasks/P8-T03-TASK-0063/results.md` — packet results
- `tasks/P8-T03-TASK-0063/handoff.md` — handoff

## Reviewer Notes
The command intentionally reports blocked/ambiguous workflow states with `workflow next: stopped` while still exiting successfully for machine consumption.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Implement `P8-T04` (`forge task next`) using the same evaluator-first output contract.
