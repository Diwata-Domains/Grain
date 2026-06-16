# Task: Implement archiving model — phase close snapshots and `grain archive` command group

## Metadata
- **ID:** TASK-0208
- **Status:** done
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T05
- **Packet Path:** tasks/P31-T05-TASK-0208/
- **Dependencies:** none
- **Primary Adapter:** code

## Objective
Implement the archiving model from `docs/working/archive_spec.md`. Covers automatic phase-close doc snapshots, proposal pruning, and the full `grain archive` command group.

## Implementation Steps

### Automatic — phase close working doc snapshots
File: `src/grain/services/phase_service.py`
Extend `grain phase close` to:
1. After packet archive, copy key working docs to `docs/archive/phases/phase-N/`
2. Write `metadata.json` with phase number, closed_at, tasks_done, grain_version
3. Files to snapshot: `backlog.md`, `current_focus.md`, `open_questions.md`, `tooling_notes.md`

### Automatic — proposal pruning
File: `src/grain/services/archive_service.py` (new)
- `prune_proposals()`: moves dismissed proposals older than threshold and expired proposals to `docs/archive/proposals/`
- Called by `grain suggest --prune` (stub the suggest command hook for now)

### `grain archive` command group
Files: `src/grain/services/archive_service.py` (new), `src/grain/cli/archive.py` (new)
Commands:
- `grain archive snapshot [--label <label>]` — copies `docs/working/` to `docs/archive/snapshots/<YYYYMMDD>-<label>/`
- `grain archive milestone <version>` — creates `docs/archive/milestones/<version>/` with working/, canonical/, tasks_index.json, metadata.json; `--dry-run` flag
- `grain archive list [--type phase|milestone|snapshot] [--format json]`
- `grain archive show <target>` — lists files and shows metadata.json
- `grain archive prune --older-than <Nd>` — removes archived proposals only

### `grain suggest accept` stub for workspace-idle-archive suggestion
This can be stubbed in this task: `grain archive` should not crash if called in response to a `grain suggest accept workspace-archive` call. The full `grain suggest` implementation is Phase 32.

## Deliverable
- `grain phase close` writes working doc snapshot
- `grain archive` command group fully working
- Tests: phase close produces snapshot, `grain archive snapshot` creates correct files, `grain archive list` returns entries, `grain archive prune` removes old proposals only

## Constraints
- Archive operations are additive — nothing deleted from active workspace
- `docs/archive/` is NOT gitignored — archives are part of project history
- `grain archive milestone` does not auto-commit
- `grain archive prune` removes only `docs/archive/proposals/` entries, never phase or milestone archives
