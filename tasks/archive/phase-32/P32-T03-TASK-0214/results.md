# Results — TASK-0214

## Summary

`grain phase close` now auto-archives a phase's task packets into
`tasks/archive/phase-{N}/` after the working-doc snapshot, and records
`tasks_done` + `tasks_archive` on the phase `metadata.json`. A new
`--keep-tasks` flag skips the move when a packet is carried forward.

## What Shipped

- `move_phase_packets(root, phase, *, keep_tasks=False, dry_run=False)` in
  `src/grain/services/archive_service.py` — moves (never copies) `tasks/P{N}-*`
  dirs to `tasks/archive/phase-{N}/`, updates the phase `metadata.json` in place
  with `tasks_done` (count) + `tasks_archive` (repo-relative path). Idempotent
  (re-running is a no-op; already-archived packets still count toward
  `tasks_done`), graceful on no-match, and refuses to clobber an existing
  archive entry so a packet is never lost. Returns `PhasePacketsResult`.
- Wired into `close_phase` (`phase_close_service.py`) after `archive_phase_docs`;
  threads a keyword-only `keep_tasks` flag and surfaces `packets_archived` +
  `packets_archive_path` on `PhaseCloseResult`. Dry-run reports the planned move
  without touching the filesystem.
- Added `--keep-tasks` to `grain phase close` (`src/grain/cli/phase.py`); text +
  `--format json` output now include the moved-packet summary.

## Files

- src/grain/services/archive_service.py (move_phase_packets + helpers + result dataclass)
- src/grain/services/phase_close_service.py (wiring + result fields + keep_tasks)
- src/grain/cli/phase.py (--keep-tasks flag, output)

## Tests

- tests/test_phase_close_archives_packets.py — 12 tests: service move/metadata/
  keep-tasks/no-match/idempotent/dry-run, plus CLI close integration
  (archives, --keep-tasks, no-packets graceful, dry-run, JSON shape).

## Test Results

Full suite green: 1252 passed, 1 xfailed.
