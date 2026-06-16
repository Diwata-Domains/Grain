# Results — TASK-0206

## Summary

All 14 scaffold gaps from `docs/working/scaffold_audit.md` fixed. 1036 tests pass. `grain init --name/--type` and `grain upgrade --add-missing` are live.

## Deliverables

### New template files (`src/grain/data/runtime/`)
13 new files, 1 updated (`workflow_metrics.md`):
- `product_scope.md` → `docs/canonical/product_scope.md`
- `architecture.md` → `docs/canonical/architecture.md`
- `decisions.md` → `docs/canonical/decisions.md`
- `landscape_canonical.md` → `docs/canonical/landscape.md`
- `backlog.md` → `docs/working/backlog.md`
- `current_focus.md` → `docs/working/current_focus.md`
- `open_questions.md` → `docs/working/open_questions.md` (with Suggested Action field)
- `change_proposals.md` → `docs/working/change_proposals.md` (with Suggested Action field)
- `roadmap.md` → `docs/working/roadmap.md`
- `current_task_template.md` → `docs/working/current_task.md`
- `landscape_working.md` → `docs/working/landscape.md`
- `CHANGELOG.md` → `CHANGELOG.md`
- Updated `workflow_metrics.md` — replaced `# DRAFT` with real phase metrics structure

### `init_service.py`
- Added `docs/working/proposals` to `_REQUIRED_DIRS`
- Added all 13 new files to `_SEED_FILE_SOURCES`
- Added `project_name` and `project_type` parameters
- `--name` replaces `[Your Project Name]` in all seeded files; `--type` replaces manifest type placeholder

### `init.py` CLI
- Added `--name` and `--type` flags
- Post-init reminder if `--name` not passed

### `docs_manifest.yaml`
- Added `decisions` and `landscape` canonical entries
- Added `current_task`, `roadmap`, `landscape_working`, `proposals` working entries
- Fixed `tooling_notes` `read_when: never` → `["encountering_blockers", "logging_friction"]`

### `upgrade_service.py`
- Added `absent: list[str]` to `UpgradeResult`
- Added `_scan_absent_seeded_files()` — compares `_SEED_FILE_SOURCES` against workspace
- Added `add_missing` parameter — seeds absent files only, never overwrites

### `upgrade.py` CLI
- Added `--add-missing` flag
- Text output shows absent files section with `+  filename  (not present)`
- JSON output includes `absent` and `add_missing` keys

### Tests
- `test_init_service.py`: updated `EXPECTED_DIRS`, `EXPECTED_SEED_FILES`, canonical ID set; added 7 new tests (name substitution, type substitution, CHANGELOG skip-if-present, current_task template, proposals dir)
- `test_upgrade_cmd.py`: added 7 new tests (absent-file detection, add_missing service, add_missing dry_run, CLI text output, CLI add_missing flag, JSON contract)

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
