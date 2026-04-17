# Handoff: TASK-0064

## Final State
`forge task next` is implemented and packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0064
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added a task-selection CLI surface that reports next candidate or planning-required state in text/json.

## What Was Built
- New `task next` command in `src/forge/cli/task.py`.
- JSON output payload for automation (`next_task`, `next_action`, `planning_required`, stop/blocking details).
- Command tests for success, planning-required, and JSON contract paths.

## What Review Should Check
- Command does not mutate workflow/task docs.
- Selection behavior is deterministic and only returns a next task when evaluator returns `task_execute`.
- Planning-required and stopped cases expose explicit reasons instead of generic failures.

## What Was Not Done
- `forge phase next` implementation (`P8-T05`)
- `forge task prepare` implementation (`P8-T06`)
- runner execution command (`forge workflow run`)

## Known Issues or Follow-ups
- Task selection output should remain schema-consistent with `workflow next` and future phase/task workflow commands.

## Files Changed
- `src/forge/cli/task.py` — added `task next`
- `tests/test_task_next_cmd.py` — command tests
- `docs/working/backlog.md` — status/readiness updates for `P8-T04` and `P8-T05`
- `docs/working/current_focus.md` — immediate-goal updates
- `docs/working/current_task.md` — active task pointer
- `tasks/P8-T04-TASK-0064/task.md` — packet metadata/scope
- `tasks/P8-T04-TASK-0064/context.md` — packet context
- `tasks/P8-T04-TASK-0064/plan.md` — packet plan
- `tasks/P8-T04-TASK-0064/deliverable_spec.md` — packet deliverable contract
- `tasks/P8-T04-TASK-0064/results.md` — packet results
- `tasks/P8-T04-TASK-0064/handoff.md` — handoff

## Reviewer Notes
This packet keeps the workflow runner narrow by exposing task-selection state only; no runner-step execution behavior is introduced.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Implement `P8-T05` (`forge phase next`) using the same evaluator-first machine-readable pattern.
