# Grain Archiving Model Spec

**Status:** Working spec — v0.4.0 planning (Phase 30, TASK-0200)
**Implementation phase:** Phase 31 (DX Hardening)

---

## 1. Three Archive Surfaces

| Surface | Trigger | Operator action required? | Description |
|---------|---------|--------------------------|-------------|
| Working doc snapshot | `grain phase close` | No | Automatic snapshot of key working docs at phase close |
| Proposal pruning | `grain suggest --prune` or signal resolution | No | Expired/dismissed proposals moved out of working dir |
| Milestone archive | `grain suggest accept` or `grain archive milestone` | Yes | Full workspace snapshot at version boundary |
| Workspace idle archive | `grain suggest accept` | Yes | Final snapshot when workspace is fully complete |
| Point-in-time snapshot | `grain archive snapshot` | Yes (explicit command) | Ad-hoc working doc snapshot |

---

## 2. Archive Directory Layout

```
docs/archive/
  phases/
    phase-30/
      backlog.md           ← snapshot at phase-30 close
      current_focus.md
      open_questions.md
      tooling_notes.md
      metadata.json
    phase-31/
      ...
  milestones/
    v0.4.0/
      working/             ← snapshot of docs/working/ at v0.4.0
      canonical/           ← snapshot of docs/canonical/
      tasks_index.json     ← task list with final statuses (not packet content)
      metadata.json
  snapshots/
    20260611-pre-refactor/
      ...
  proposals/               ← archived (non-pending) proposals
    SUG-20260501-001.md
    SUG-20260501-002.md
```

All archive directories are additive — nothing is deleted from the active workspace.

`.gitignore` does NOT exclude `docs/archive/` — archives are part of the project history and should be committed.

---

## 3. Automatic — Working Doc Snapshots at Phase Close

When `grain phase close` runs:
1. Copies the following files to `docs/archive/phases/phase-N/`:
   - `docs/working/backlog.md`
   - `docs/working/current_focus.md`
   - `docs/working/open_questions.md`
   - `docs/working/tooling_notes.md`
2. Writes `docs/archive/phases/phase-N/metadata.json`:
   ```json
   {
     "phase": 30,
     "closed_at": "2026-06-11",
     "tasks_done": 14,
     "grain_version": "0.4.0"
   }
   ```
3. No flags required to enable this — it runs automatically with every `grain phase close`

The working docs themselves are not modified. Phase archive runs after the existing packet archive (`tasks/archive/phase-N/`) so the snapshot reflects the final state at close.

---

## 4. Automatic — Proposal Pruning

When `grain suggest` runs (any invocation), it checks each `pending` proposal for expired conditions:
- Proposal type `pick-up`: the referenced task is now `done` → status set to `expired`
- Proposal type `new-task`: the referenced OQ is now `resolved`, or a matching task was created → status set to `expired`
- Proposal status `dismissed` AND age > 30 days → eligible for pruning

When `grain suggest --prune` runs (or automatically at the end of `grain suggest`):
- Moves all `dismissed` proposals older than 30 days and all `expired` proposals to `docs/archive/proposals/`
- `docs/working/proposals/` should contain only `pending` proposals after pruning

`docs/archive/proposals/` is not pruned automatically. `grain archive prune --older-than 90d` removes archived proposals older than the given threshold.

---

## 5. Suggested — Milestone Archive via `grain suggest`

### Trigger conditions

`grain suggest` surfaces a `milestone-archive` suggestion when ALL are true:
- All tasks in the highest completed phase are `done`
- A version string in `pyproject.toml` (or `package.json`) matches a recognizable version tag format
- No `docs/archive/milestones/<version>/` directory exists for that version

### Suggestion output

```
SUGGESTION SUG-20260611-003
  Type:     milestone-archive
  Version:  v0.4.0
  Signal:   All Phase 35 tasks done; v0.4.0 declared in pyproject.toml; no milestone archive exists
  Action:   grain archive milestone v0.4.0
  → grain suggest accept SUG-20260611-003
  → grain suggest dismiss SUG-20260611-003
```

Accepting calls `grain archive milestone v0.4.0`.

---

## 6. Suggested — Workspace Idle Archive

### Trigger conditions

`grain suggest` surfaces a `workspace-archive` suggestion when ALL are true:
- All phases are closed (no tasks in `ready`, `in_progress`, `draft` status)
- No git commits in the past 90 days (configurable via `audit_thresholds.workspace_idle_days`)
- No previous `workspace-archive` suggestion has been accepted

### Suggestion output

```
SUGGESTION SUG-20260611-004
  Type:     workspace-archive
  Signal:   All phases closed; no commits in 94 days
  Action:   Mark workspace as archived + grain archive snapshot --label final
  → grain suggest accept SUG-20260611-004
  → grain suggest dismiss SUG-20260611-004
```

Accepting:
1. Runs `grain archive snapshot --label final`
2. Adds `archived: true` and `archived_at: <date>` to `docs_manifest.yaml`
3. `grain workflow next` on an archived workspace returns stop reason `workspace_archived`

This action is irreversible via Grain (the `archived: true` flag must be manually removed to reactivate). The operator is warned before accepting.

---

## 7. Explicit — `grain archive` Command Group

### `grain archive snapshot [--label <label>]`

Takes a point-in-time snapshot of `docs/working/` and writes to `docs/archive/snapshots/<YYYYMMDD>-<label>/`. The label is optional; if absent, a sequence number is used (`001`, `002`, etc.).

Any working file added after `grain init` is included. Template files are not excluded.

### `grain archive milestone <version>`

Creates `docs/archive/milestones/<version>/` containing:
- `working/` — full snapshot of `docs/working/`
- `canonical/` — full snapshot of `docs/canonical/`
- `tasks_index.json` — list of all tasks with their final statuses, packet paths, and results.md existence flag (not packet content — packet content is already in `tasks/archive/`)
- `metadata.json` — version, date, task count, phase count, Grain version

Does NOT automatically commit. The operator commits the milestone archive as part of the release commit.

```
grain archive milestone v0.4.0
grain archive milestone v0.4.0 --dry-run   # show what would be written
```

### `grain archive list`

Lists all archives: phases, milestones, snapshots — with dates and types.

```
grain archive list
grain archive list --type phase|milestone|snapshot
grain archive list --format json
```

### `grain archive show <target>`

Shows the contents of an archived snapshot.

```
grain archive show phase-30
grain archive show milestone-v0.4.0
grain archive show snapshot-20260611-001
```

Output: list of files, metadata.json summary.

### `grain archive prune --older-than <Nd>`

Removes archived proposals older than the given threshold. Does not remove phase archives, milestone archives, or point-in-time snapshots — only `docs/archive/proposals/`.

---

## 8. Consistency with Existing Archive Behavior

Grain's existing phase archive (`tasks/archive/phase-N/`) is unchanged. The new working doc snapshot and the packet archive run as parallel operations within `grain phase close`. Neither replaces the other.

`grain archive` is a new command group; it does not modify any existing command behavior.
