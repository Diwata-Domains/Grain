# Results: P3-T01-TASK-0019

## Status
done

## Files Changed
- `src/ai_build_toolkit/domain/packets.py` — new file, `TASK_ID_PATTERN` + `next_task_id()`
- `tests/test_task_id.py` — new file, 7 tests

## Summary
Implemented `next_task_id(tasks_root: Path) -> str` in `domain/packets.py`. Scans
subdirectory names under `tasks_root`, extracts the 4-digit integer from any
`TASK-####` segment (handles both legacy bare names and CP-001 `P<N>-T<NN>-TASK-####`
names), returns `TASK-{max+1:04d}`. Returns `TASK-0001` for missing or empty
directories. Non-matching directories are silently ignored.

## Test Results
7/7 new tests passing. 161/161 total passing (no regressions).

## Deliverable Checklist
- [x] `domain/packets.py` exists
- [x] `next_task_id` importable from `ai_build_toolkit.domain.packets`
- [x] Returns `TASK-0001` for empty or missing tasks directory
- [x] Returns correct next ID from max existing (max + 1, zero-padded)
- [x] Handles legacy and CP-001 directory names
- [x] Non-packet directories ignored
- [x] 7/7 tests passing
- [x] Full suite passing (161/161)

## Blockers
None.
