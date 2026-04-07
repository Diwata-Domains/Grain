# Results: P3-T10-TASK-0028

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/task_service.py` — added `validate_one_packet()`, `validate_all_packets()`
- `src/ai_build_toolkit/cli/task.py` — wired `task_validate` with `--id` / `--all`
- `tests/test_task_validate_cmd.py` — new, 10 tests

## Summary
`validate_one_packet()` delegates to `validate_packet()` after finding the dir.
`validate_all_packets()` iterates all packet dirs, prefixes each error with the
dir name. CLI: `--id` and `--all` are mutually exclusive; no flag defaults to
`--all`. Not-found → exit 2 (click.UsageError). Validation failure → exit 3
(ValidationError via cli() wrapper, tested via subprocess).

## Test Results
10/10 new tests passing. 246/246 total passing (no regressions).

## Deliverable Checklist
- [x] `validate_one_packet()` and `validate_all_packets()` in task_service
- [x] `--id` validates one, `--all` validates all, no flag defaults to all
- [x] `--id` + `--all` together exits 2
- [x] Unknown packet exits 2
- [x] Invalid packet exits 3 (subprocess)
- [x] Valid packet exits 0
- [x] JSON output includes errors list
- [x] 10/10 tests passing, 246/246 total

## Blockers
None.
