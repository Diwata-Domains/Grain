# Task: Spec the archiving model — automatic, suggested, and explicit archive surfaces

## Metadata
- **ID:** TASK-0200
- **Status:** done
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T11
- **Packet Path:** tasks/P30-T11-TASK-0200/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Design a coherent archiving model for Grain that covers three distinct archive surfaces: (1) automatic archiving that runs as a side-effect of existing commands with no operator decision; (2) suggested archiving surfaced by `grain suggest` at natural milestones; (3) explicit operator-initiated archiving via a `grain archive` command group. The model must be consistent with Grain's existing phase/packet archive behavior (`grain phase archive`) and must not break any existing archive paths.

## Why This Task Exists
Grain already archives task packets (`tasks/archive/`) when `grain phase close` runs. But three related archive needs are unaddressed:

1. **Working doc drift** — after 10+ phases, `backlog.md` and `current_focus.md` grow to thousands of lines and become hard to scan. There is no mechanism to snapshot their state at phase boundaries so you can look back at what the project looked like at Phase 15 vs. Phase 30.
2. **Proposal accumulation** — `docs/working/proposals/` grows indefinitely. Dismissed and expired suggestions from months ago pollute the active view.
3. **Milestone capture** — at version release boundaries (v0.3.0, v0.4.0), there is no canonical snapshot of the project state at that moment. Post-release, the working docs evolve and historical milestone context is lost.

## Scope

### Part 1 — Automatic: working doc snapshots at phase close

When `grain phase close` runs, it already archives packet directories. Extend it to also snapshot the key working docs at that moment into `docs/archive/phases/phase-N/`:

```
docs/archive/
  phases/
    phase-30/
      backlog.md         ← snapshot of docs/working/backlog.md at phase-30 close
      current_focus.md   ← snapshot at phase-30 close
      open_questions.md  ← snapshot at phase-30 close
      tooling_notes.md   ← snapshot at phase-30 close
      metadata.json      ← { phase: 30, closed_at: "2026-06-11", tasks_done: 10, ... }
```

- Snapshots are copies, not symlinks — the archive is immutable after creation
- The working docs themselves are not modified; archiving is purely additive
- `grain phase close` always runs this automatically; no flag required to enable it
- Existing `tasks/archive/phase-N/` behavior is unchanged — packet archive and doc archive are parallel

`grain archive show phase-30` — shows the archived working docs for Phase 30.

### Part 2 — Automatic: proposal pruning

Proposals in `docs/working/proposals/` that have reached terminal status (`dismissed`, `expired`, `accepted`) are moved to `docs/archive/proposals/` automatically when:
- A new `grain suggest` run detects proposals whose underlying signal has resolved (the referenced task is now `done`, the referenced OQ is now `resolved`, etc.)
- Or when `grain suggest --prune` is explicitly called

Pruning rules:
- `accepted` proposals: moved to archive after the referenced task closes
- `dismissed` proposals: moved to archive after 30 days (configurable)
- `expired` proposals: moved immediately when signal resolves

`docs/working/proposals/` should contain only `pending` proposals at any given time after a `grain suggest --prune` pass.

### Part 3 — Suggested: milestone archive via `grain suggest`

When the following conditions are all true:
- All tasks in the highest completed phase are `done`
- The current version tag matches a version milestone in `pyproject.toml` (or `package.json`, etc.)
- No `docs/archive/milestones/<version>/` directory exists yet

`grain suggest` surfaces a `milestone-archive` suggestion:

```
SUGGESTION SUG-20260611-003
  Type:     milestone-archive
  Version:  v0.4.0
  Signal:   All Phase 35 tasks done; v0.4.0 version tag present; no milestone archive exists
  Action:   Create docs/archive/milestones/v0.4.0/ with full workspace snapshot
  → grain suggest accept SUG-20260611-003
  → grain suggest dismiss SUG-20260611-003
```

Accepting runs `grain archive milestone v0.4.0`.

### Part 4 — Suggested: workspace idle archive

When a workspace has:
- All phases closed (no `in_progress`, `ready`, or `draft` tasks)
- No git commits in the past 90 days (configurable)
- No open `in_progress` task

`grain suggest` surfaces a `workspace-archive` suggestion:
```
SUGGESTION SUG-20260611-004
  Type:     workspace-archive
  Signal:   All phases closed; no activity for 94 days
  Action:   Tag workspace as archived; run grain archive snapshot for final state capture
  → grain suggest accept SUG-20260611-004
  → grain suggest dismiss SUG-20260611-004
```

Accepting adds `archived: true` to `docs_manifest.yaml` and runs a final snapshot. `grain workflow next` on an archived workspace returns `workspace_archived` stop reason rather than routing.

### Part 5 — Explicit: `grain archive` command group

```
grain archive snapshot [--label <label>]
```
Takes a point-in-time snapshot of all working docs and writes to `docs/archive/snapshots/<YYYYMMDD>-<label>/`. The snapshot is a flat copy of the current `docs/working/` directory. No phase close required. The operator calls this any time they want to freeze a moment.

```
grain archive milestone <version>
```
Creates `docs/archive/milestones/<version>/` containing:
- Full `docs/working/` snapshot
- Full `docs/canonical/` snapshot
- `tasks/` index (list of all tasks and their final statuses — not packet content, which is already in `tasks/archive/`)
- `metadata.json`: version, date, task count, phase count, test count (if readable from pyproject.toml)

This is the canonical release artifact for the Grain workspace. It does NOT commit to git automatically — the operator commits it as part of the release commit.

```
grain archive show [phase-N | milestone-<version> | snapshot-<YYYYMMDD>]
```
Shows the contents of an archived snapshot — list of files, metadata.json summary.

```
grain archive list
```
Lists all archives: phases, milestones, snapshots — with dates and types.

## Deliverable
`docs/working/archive_spec.md` — full spec covering all four parts and the `grain archive` command interface.

## Constraints
- All archive operations are additive — nothing is deleted or modified in the active workspace
- Proposal pruning is the only operation that moves files (from `docs/working/proposals/` to `docs/archive/proposals/`)
- Milestone archives do not trigger automatically — they require either `grain suggest accept` or explicit `grain archive milestone`
- Workspace idle archiving requires explicit `grain suggest accept` — Grain never silently marks a workspace as archived
- Archive directories must not grow without bound: `docs/archive/proposals/` is prunable with `grain archive prune --older-than 90d`
