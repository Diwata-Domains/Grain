# Results: P3-T08-TASK-0027

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/task_service.py` — added `update_packet_status()`
- `src/ai_build_toolkit/cli/task.py` — wired `task_status` with `--id`, `--status`; custom text output showing transition arrow
- `tests/test_task_status_cmd.py` — new, 9 tests

## Summary
`update_packet_status()` finds the packet, reads current status, validates the
transition via `validate_status_transition()`, applies it via `write_packet_status()`.
CLI distinguishes not-found (exit 2 via click.UsageError) from invalid transition
(exit 5 via InvalidTransitionError through cli() wrapper). Text output shows
`TASK-#### -> new_status` arrow. Exit 5 tested via subprocess.

One fix: `print_result` doesn't render `result.status`, so the CLI renders text
output manually instead.

## Test Results
9/9 new tests passing. 236/236 total passing (no regressions).

## Deliverable Checklist
- [x] `update_packet_status()` validates transition and writes task.md
- [x] `abt task status --id X --status Y` exits 0 on valid transition
- [x] task.md status field updated on disk
- [x] Output shows transition arrow and updated file
- [x] Unknown packet exits 2
- [x] Invalid transition exits 5 (subprocess test)
- [x] Sequential transitions work correctly
- [x] 9/9 tests passing, 236/236 total

## Blockers
None.
