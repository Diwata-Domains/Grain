# Handoff: TASK-0065

## Final State
`forge phase next` is implemented and packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0065
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added a phase-level next-action command with deterministic text/json outputs.

## What Was Built
- New `phase` CLI group with `phase next`.
- Mapping layer from evaluator outcomes to phase actions (`no_phase_action`, `phase_planning`, `phase_review_close`).
- Test coverage for all phase-action paths and JSON output payload.

## What Review Should Check
- Phase action mapping is deterministic and consistent with evaluator semantics.
- Command does not mutate working docs, backlog, or task packets.
- JSON payload includes all required automation fields.

## What Was Not Done
- `forge task prepare` implementation (`P8-T06`)
- `forge prompt show` implementation (`P8-T07`)
- `forge workflow run` implementation (`P8-T08`)

## Known Issues or Follow-ups
- Maintain consistent output envelope and terminology across all workflow-state commands.

## Files Changed
- `src/forge/cli/phase.py` — phase command group + next subcommand
- `src/forge/cli/__init__.py` — phase command registration
- `tests/test_phase_next_cmd.py` — phase-next CLI tests
- `docs/working/backlog.md` — `P8-T05`/`P8-T06` status-readiness updates, then close transition
- `docs/working/current_focus.md` — immediate-goal updates, then shifted to `P8-T06`
- `docs/working/current_task.md` — active task pointer cleared at close
- `tasks/P8-T05-TASK-0065/task.md` — packet metadata/scope
- `tasks/P8-T05-TASK-0065/context.md` — packet context
- `tasks/P8-T05-TASK-0065/plan.md` — packet plan
- `tasks/P8-T05-TASK-0065/deliverable_spec.md` — packet deliverable contract
- `tasks/P8-T05-TASK-0065/results.md` — packet results
- `tasks/P8-T05-TASK-0065/handoff.md` — handoff

## Reviewer Notes
This command is intentionally phase-focused and advisory; it does not perform phase transitions.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Implement `P8-T06` (`forge task prepare`) using the same evaluator-first machine-readable contract.
