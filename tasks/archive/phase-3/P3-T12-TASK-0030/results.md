# Results: P3-T12-TASK-0030

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/task_service.py` — added `close_packet()`
- `src/ai_build_toolkit/cli/task.py` — wired `task_close` with `--id`
- `tests/test_task_close_cmd.py` — new, 8 tests

## Summary
`close_packet()` finds the packet, runs `validate_closure()`, and on success calls
`write_packet_status(packet_dir, "done")`. CLI mirrors the status command pattern:
not-found → exit 2 (click.UsageError); closure validation failure → exit 3
(ValidationError via cli() wrapper). Exit 3 cases tested via subprocess. Confirmed
closure is not idempotent — a second close attempt on an already-done packet fails
with exit 3 because status is no longer 'review'.

## Test Results
8/8 new tests passing. 262/262 total passing (no regressions).

## Deliverable Checklist
- [x] `close_packet()` runs validate_closure() before writing done
- [x] `abt task close --id X` exits 0 on success
- [x] task.md status set to 'done' on disk
- [x] Output shows transition arrow to done
- [x] Unknown packet exits 2
- [x] Not-in-review status exits 3 (subprocess)
- [x] Missing results.md exits 3 (subprocess)
- [x] Already-done packet exits 3 on re-close attempt
- [x] 8/8 tests passing, 262/262 total

## Blockers
None.
