# Results: P3-T06-TASK-0026

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/task_service.py` — added `_find_packet_dir()`, `_ALL_PACKET_FILES`, `show_packet()`
- `src/ai_build_toolkit/cli/task.py` — wired `task_show` with `--id`, text and JSON output
- `tests/test_task_show_cmd.py` — new, 8 tests

## Summary
`show_packet(root, task_id)` finds the packet directory by scanning for a dir
containing `task_id` in its name, reads the PacketRecord, and builds a file
inventory dict for all 6 packet files (required + optional). Returns a 3-tuple
(CommandResult, PacketRecord | None, inventory). CLI renders key/value metadata
and per-file present/absent inventory in text mode; full structured data in JSON.
Unknown ID raises click.UsageError (exit 2).

## Test Results
8/8 new tests passing. 227/227 total passing (no regressions).

## Deliverable Checklist
- [x] `show_packet()` finds packet by TASK-#### in dir name
- [x] Returns file inventory for all 6 packet files
- [x] Unknown ID → exit 2
- [x] Missing `--id` → exit 2
- [x] Text output: id, status, phase, path, file inventory
- [x] JSON output: structured packet object with files dict
- [x] 8/8 tests passing, 227/227 total

## Blockers
None.
