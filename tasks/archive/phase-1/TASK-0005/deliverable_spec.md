# Deliverable Spec: TASK-0005

## Definition of Done

This task is complete when all of the following are true:

1. `abt init` creates the required directory structure in a fresh target directory
2. `abt init` skips files and directories that already exist (without `--force`)
3. `abt init` reports files created, skipped, and blocked clearly
4. `abt init --dry-run` reports intended actions without writing any files
5. `abt init --force` overwrites non-canonical files
6. Canonical docs (`docs/canonical/`) are never silently overwritten — blocked without `--force`, reported as blocked with `--force` if content differs
7. Init logic lives in `services/init_service.py`, not in `cli/`
8. `resolve_repo_root()` or `Path.cwd()` is used for path resolution — no hardcoded paths
9. Tests cover: fresh init, skip-existing, dry-run, force, canonical protection — all passing

## Required Directories Created by `abt init`
- `docs/canonical/`
- `docs/working/`
- `docs/runtime/`
- `tasks/`
- `templates/docs/`
- `templates/tasks/`
- `templates/prompts/`
- `src/`
- `tests/`

## Out of Scope
- Populating templates with real content (P1-T06)
- `--format json` output (P1-T07)
- Full shared error types (P1-T08)
- Manifest generation (Phase 2)
