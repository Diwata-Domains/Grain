# Handoff: TASK-0097

## Final State
P13-T04 existing-project onboarding prompt is implemented and ready for task review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0097
- **Phase:** Phase 13 — Existing Project Adoption
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Review Decision:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added `workflow.onboard.existing` prompt with mandatory CLI steps and prompt-surface test coverage.

## What Was Built
- New prompt entrypoint: `prompts/workflow.onboard.existing.md`.
- Mandatory CLI sequence for additive scaffold + validation + workflow check.
- Required behavior/output contract for clarifying questions, assumptions, and unresolved-gap recording.
- Prompt-surface tests for stage metadata and required command strings.

## What Review Should Check
- Mandatory CLI sequence is complete, ordered, and executable.
- Prompt language preserves draft-first and human-review authority boundaries.

## What Was Not Done
- Phase 13 integration suite (`P13-T05`) implementation.
- Canonical doc changes.

## Known Issues or Follow-ups
- None.

## Files Changed
- `prompts/workflow.onboard.existing.md` — existing-project onboarding prompt
- `tests/test_workflow_onboard_existing_prompt.py` — prompt contract tests
- `tasks/P13-T04-TASK-0097/task.md` — packet metadata/scope
- `tasks/P13-T04-TASK-0097/context.md` — packet context contract
- `tasks/P13-T04-TASK-0097/plan.md` — execute plan
- `tasks/P13-T04-TASK-0097/deliverable_spec.md` — acceptance contract
- `tasks/P13-T04-TASK-0097/results.md` — execution results
- `tasks/P13-T04-TASK-0097/handoff.md` — review handoff
- `docs/working/backlog.md` — status sequence update
- `docs/working/current_focus.md` — immediate goals update
- `docs/working/current_task.md` — active task pointer/status

## Reviewer Notes
Prompt intentionally avoids introducing new command surfaces; it uses currently available CLI behavior and keeps scanner/doc-gen outputs as draft artifacts.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Execute `P13-T05` integration tests after `TASK-0097` acceptance.
