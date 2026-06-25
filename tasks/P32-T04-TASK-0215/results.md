# Results — TASK-0215

## Summary

`grain archive show --phase N` (i.e. `grain archive show phase-N`) now also
lists the task packets archived under `tasks/archive/phase-{N}/`, showing each
packet's task ID and title parsed from `task.md`. `--format json` includes a
`packets` array. Phases closed before v0.4.0 (no `tasks_archive` in metadata)
surface a graceful note instead of erroring.

## What Shipped

- Extended `show_archive` (`src/grain/services/archive_service.py`): for phase
  archives it reads `tasks_archive` from `metadata.json`, enumerates the packet
  dirs, and parses `# Task: <title>` + the TASK-#### id from each `task.md`.
  Returns `ArchivedPacket` entries plus a `packets_note` for the graceful cases
  (no `tasks_archive` field, or the directory is absent). Read-only; never
  mutates the archive. Paths are repo-relative.
- Updated `grain archive show` (`src/grain/cli/archive.py`): text output renders
  a packet list (ID + title), and `--format json` adds a `packets` array and
  `packets_note`.

## Files

- src/grain/services/archive_service.py (show_archive + _read_archived_packets
  + _read_task_title + ArchivedPacket dataclass + packets fields on ArchiveShowResult)
- src/grain/cli/archive.py (archive show packet list, JSON packets array)

## Tests

- tests/test_archive_show_packets.py — 6 tests: service packet listing,
  graceful no-task-archive note, missing-dir note; CLI text packet list, JSON
  packets array, and the no-archive note in text + JSON.

## Test Results

Full suite green: 1252 passed, 1 xfailed.
