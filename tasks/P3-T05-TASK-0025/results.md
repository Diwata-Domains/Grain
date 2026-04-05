# Results: P3-T05-TASK-0025

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/task_service.py` — added `list_packets(root)`; also fixed `create_packet_directory` to substitute real TASK-#### ID into task.md template
- `src/ai_build_toolkit/cli/task.py` — wired `task_list` command with text and JSON output
- `tests/test_task_list_cmd.py` — new, 8 tests

## Summary
Added `list_packets(root)` to `task_service.py` — scans `tasks/`, filters dirs by
`TASK_ID_PATTERN`, reads each `PacketRecord`, sorts by numeric ID, skips unreadable
packets with warnings. CLI outputs count line + one row per packet (ID, status,
directory name) in text mode; JSON mode adds a `packets` array.

One fix discovered: `create_packet_directory` was not substituting the actual
`TASK-####` ID into the task.md template. The template literal `TASK-####` was left
in place, causing `read_packet_record` to return `id: "TASK-####"`. Fixed by adding
`content.replace("TASK-####", task_id)` before writing task.md.

## Test Results
8/8 new tests passing. 219/219 total passing (no regressions).

## Deliverable Checklist
- [x] `list_packets()` scans tasks/, returns sorted PacketRecord list
- [x] Empty/missing tasks dir returns ok=True with empty list
- [x] Dirs without task.md produce warning, not error
- [x] `abt task list` text output: count line + per-packet rows
- [x] `abt task list --format json` includes packets array
- [x] `create_packet_directory` now substitutes real ID into task.md
- [x] 8/8 tests passing, 219/219 total

## Blockers
None.
