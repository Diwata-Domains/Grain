# Results — TASK-0208

## Summary

Full archiving model implemented. 1108 tests pass. `grain phase close` now writes a working doc snapshot automatically. `grain archive` command group is live.

## Deliverables

### `src/grain/services/archive_service.py` (new)
- `archive_phase_docs()` — copies 4 working docs + writes metadata.json to `docs/archive/phases/phase-{N}/`
- `snapshot_working_docs()` — copies all of `docs/working/` to `docs/archive/snapshots/{YYYYMMDD}-{label}/`; auto-increments sequence if no label
- `archive_milestone()` — creates `docs/archive/milestones/{version}/` with working/, canonical/, tasks_index.json, metadata.json; errors if already exists
- `list_archives()` — returns `ArchiveEntry` list sorted by date, with optional type filter
- `show_archive()` — resolves by name across phases/milestones/snapshots, returns files + metadata
- `prune_archived_proposals()` — removes files from `docs/archive/proposals/` older than N days
- `move_working_proposals_to_archive()` — moves dismissed/expired proposals from working to archive

### `src/grain/cli/archive.py` (new)
`grain archive snapshot`, `milestone`, `list`, `show`, `prune` — all with `--format json` support.

### `src/grain/services/phase_close_service.py`
- `PhaseCloseResult` gains `archive_path` field
- After writing the closed marker, calls `archive_phase_docs()` automatically

### `src/grain/cli/__init__.py`
Registered `archive_group`.

### `tests/test_archive_cmd.py` (new)
31 tests covering phase close snapshot, snapshot creation, milestone creation, tasks_index, list/show/prune, CLI text/JSON output, dry-run mode.

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
