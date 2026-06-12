# Results — TASK-0200

## Status
done — 2026-06-11

## Deliverable
`docs/working/archive_spec.md` — full archiving model spec.

## Key Decisions

**Three surfaces, clear triggers:** Automatic (phase close → doc snapshot; proposal pruning on signal resolution), Suggested (`grain suggest` surfaces milestone-archive and workspace-idle-archive), Explicit (`grain archive snapshot/milestone/list/show/prune`).

**Archive layout:** `docs/archive/phases/`, `milestones/`, `snapshots/`, `proposals/` — all in version control. Nothing is gitignored.

**Workspace idle archive:** Irreversible via Grain (manual `archived: true` removal required). `grain workflow next` returns `workspace_archived` stop reason. Requires explicit `grain suggest accept`.

**Milestone archive:** Does not auto-commit. Operator commits as part of release commit. `--dry-run` available.

**Proposal pruning:** 30-day age for dismissed, immediate for expired. `docs/archive/proposals/` prunable with `grain archive prune --older-than Nd`.

## Files Changed
- `docs/working/archive_spec.md` — created
- `tasks/P30-T11-TASK-0200/task.md` — status set to done
