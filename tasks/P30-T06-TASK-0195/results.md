# Results — TASK-0195

## Status
done — 2026-06-11

## Deliverable
`docs/working/scaffold_audit.md` — gap inventory (14 gaps) + all template content + manifest change list + `grain upgrade` absent-file behavior spec + Phase 31 implementation checklist.

## Key Decisions

**14 gaps found:** Missing canonical docs (product_scope, architecture, decisions, landscape), missing working docs (backlog, current_focus, open_questions, change_proposals, roadmap, current_task), missing root file (CHANGELOG.md), missing directory (proposals/), broken manifest (tooling_notes `read_when: never`), no `--name`/`--type` init flags.

**`grain upgrade --add-missing`:** New flag. Scans workspace against `_SEED_FILE_SOURCES`, reports absent files, seeds them on request. Existing files are never touched. This is the upgrade path for pre-v0.4.0 workspaces to gain the new doc types.

**Additive model clarified:** `grain upgrade` alone only reports; `--add-missing` seeds; `--diff` shows stale-file diffs. No flag silently overwrites existing content.

**Implementation is code work in Phase 31** — this task (planning phase) produced the spec. Template content is written out in `scaffold_audit.md §3` for direct use in Phase 31.

## Files Changed
- `docs/working/scaffold_audit.md` — created
- `tasks/P30-T06-TASK-0195/task.md` — status set to done
