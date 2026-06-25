# Results — TASK-0216

## Summary
Integrated `grain suggest` into `grain workflow next` as a surface-only hint. When the workflow
evaluation ends in a no-obvious-next-task stop reason (`task_planning_required`,
`phase_has_no_tasks`, `phase_boundary_review_close_required`), the CLI layer calls the read-only
`suggest_service.top_suggestion(root)` helper and renders the top candidate inline (text) and as a
`suggestion` field (JSON). Surfacing writes nothing — `top_suggestion` builds candidates in memory
and never persists or mutates state, so an `accept` later has nothing to undo. Per design decision
D1, `evaluate_workflow_state` is untouched and gains no dependency on the suggest engine; the
integration lives entirely in `cli/workflow.py`, and suggest errors degrade gracefully to the plain
stop reason (helper returns `None`).

## Deliverables
- `src/grain/services/suggest_service.py` — read-only `top_suggestion(root)` (added under TASK-0213).
- `src/grain/cli/workflow.py`:
  - `_NO_NEXT_TASK_STOP_REASONS` frozenset and `_surface_top_suggestion(root, evaluation)` helper.
  - `workflow_next` now attaches `suggestion` to the JSON payload and prints an inline `suggestion`
    block in text mode for no-next-task states; output is unchanged when a ready task exists.

## Test Results
- `tests/test_workflow_next_suggestion.py` — 6 tests: suggestion surfaced (new-task on empty phase,
  pick-up from next-blocked phase), absent when a ready task exists (text + JSON null), JSON
  `suggestion` field shape, and a surface-only no-writes assertion (backlog/current_task unchanged,
  no SUG-*.md persisted).
- Full suite: 1234 passed, 1 xfailed.

## User Review
- **State:** approved

## Verification Review
- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Surface-only suggestion shown on no-next-task states in text and JSON; no writes; existing outputs unchanged; full suite green.

### Closure Blockers
- None
