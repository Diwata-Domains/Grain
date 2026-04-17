# Handoff: TASK-0076

## Final State
Adapter inspection command surfaces are implemented and packet is ready for review.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0076
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Review Decision:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added `grain adapter list` and `grain adapter show` with text/json output and command tests. Trivial fix applied during review: Recommended Next Status corrected from `review` to `done`.

## What Was Built
- New `adapter` command group with:
  - `adapter list`
  - `adapter show --id <adapter-id>`
- JSON output contracts for both commands.
- Test coverage for text/json success and unknown adapter ID behavior.

## What Review Should Check
- Commands are read-only and only inspect runtime adapter profiles.
- Output fields include required adapter contract sections.
- Command-group registration and help output remain consistent with the active CLI surface.

## What Was Not Done
- `grain orchestrate scope` and `grain orchestrate plan` (`P9-T06`)
- OrchestratorPlan validator/integration suite (`P9-T07`)

## Known Issues or Follow-ups
- `adapter show` currently reports profile fields only; capabilities are runtime objects and intentionally not serialized.

## Files Changed
- `src/grain/cli/adapter.py` — new adapter commands
- `src/grain/cli/__init__.py` — adapter group registration
- `tests/test_adapter_cmd.py` — adapter command tests
- `tests/test_command_groups.py` — CLI help coverage updates
- `docs/working/backlog.md` — `P9-T05` review and `P9-T06` ready
- `docs/working/current_focus.md` — immediate-goal updates
- `docs/working/current_task.md` — active task pointer
- `tasks/P9-T05-TASK-0076/task.md` — packet metadata/scope
- `tasks/P9-T05-TASK-0076/context.md` — packet context
- `tasks/P9-T05-TASK-0076/plan.md` — packet plan
- `tasks/P9-T05-TASK-0076/deliverable_spec.md` — packet deliverable contract
- `tasks/P9-T05-TASK-0076/results.md` — packet results
- `tasks/P9-T05-TASK-0076/handoff.md` — handoff

## Reviewer Notes
Adapter command surfaces now match canonical Phase 9 command direction and are available for orchestration CLI follow-up work.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Execute `P9-T06` next to expose `orchestrate scope/plan` CLI commands.
