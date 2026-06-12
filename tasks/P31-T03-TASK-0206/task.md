# Task: Implement scaffold seeding fixes and `grain upgrade --add-missing`

## Metadata
- **ID:** TASK-0206
- **Status:** ready
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T03
- **Packet Path:** tasks/P31-T03-TASK-0206/
- **Dependencies:** none
- **Primary Adapter:** code

## Objective
Implement all 14 gaps identified in `docs/working/scaffold_audit.md`. After this task, `grain init` on a fresh directory produces a workspace that `grain workflow next` can operate on immediately.

## Implementation Steps

See `docs/working/scaffold_audit.md` §3 for full template content to write.

1. Write 14 template files under `src/grain/data/runtime/` (canonical + working + root):
   - `docs/canonical/product_scope.md`
   - `docs/canonical/architecture.md`
   - `docs/canonical/decisions.md`
   - `docs/canonical/landscape.md`
   - `docs/working/backlog.md`
   - `docs/working/current_focus.md`
   - `docs/working/open_questions.md`
   - `docs/working/change_proposals.md`
   - `docs/working/roadmap.md`
   - `docs/working/current_task.md`
   - `docs/working/landscape.md`
   - `CHANGELOG.md` (Keep a Changelog format)
   - (update) `docs/working/workflow_metrics.md` — real structure replacing `# DRAFT`
   - `docs/working/proposals/` — `.gitkeep`

2. Add all new files to `_SEED_FILE_SOURCES` in `src/grain/services/init_service.py`
3. Add `docs/working/proposals/` to `_REQUIRED_DIRS`
4. Add `--name` and `--type` flags to `src/grain/cli/init.py`; thread through `init_service.py` with `{{project_name}}` placeholder substitution
5. Fix `tooling_notes` `read_when: never` → `["encountering_blockers", "logging_friction"]` in `src/grain/data/runtime/docs_manifest.yaml`
6. Add manifest entries for: `decisions`, `landscape`, `roadmap`, `current_task`, `proposals/`

**`grain upgrade --add-missing`:**
7. Add absent-file detection to `upgrade_service.py`: compare `_SEED_FILE_SOURCES` against workspace files
8. Report absent files in `grain upgrade` output
9. Implement `--add-missing` flag: seeds absent files only, no overwrites

## Deliverable
- All templates written and seeded
- `--name`/`--type` flags working
- `grain upgrade --add-missing` surfaces absent files and seeds them
- Tests: new files seeded, `--name` substitution, `--type` substitution, existing files not overwritten, CHANGELOG.md skip-if-present, `grain upgrade` output lists absent docs

## Constraints
- Template content is minimal (headings + placeholders, no prose)
- `grain init --no-templates` must still work
- `CHANGELOG.md` skips if present
- `grain upgrade --add-missing` never overwrites existing files
