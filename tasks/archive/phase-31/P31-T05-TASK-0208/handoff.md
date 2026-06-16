# Handoff — TASK-0208

## What Was Done

Archiving model fully implemented. Phase close snapshots run automatically. `grain archive` group is live.

## State Left For Next Task

- `grain archive milestone` does not auto-commit — the release commit includes the archive
- `docs/archive/` is not gitignored; users add the archive dir to their project's git history
- `move_working_proposals_to_archive()` is implemented but only called manually; full auto-trigger via `grain suggest --prune` is Phase 32
- Milestone archive errors if the version already exists — intentional (prevents accidental overwrite)
- `tasks_index.json` in milestone archives does not include packet file content — only metadata + has_results flag
