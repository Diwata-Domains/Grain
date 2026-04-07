# Plan: TASK-0005

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** First command to exercise the services layer and perform real filesystem writes. Involves coordination across CLI, services, adapters, and templates. Canonical protection and dry-run logic require careful reasoning. `reviewer_model` should verify canonical protection and transparency rules from `cli_spec.md` Sections 7.2 and 7.3 are met.

## Steps

1. Create `src/ai_build_toolkit/services/init_service.py`
   - Define the list of required directories from `architecture.md` Section 5
   - Implement `init_repo(root: Path, force: bool, dry_run: bool) -> InitResult`
   - `InitResult` holds: `created`, `skipped`, `blocked` file/dir lists
   - Create missing directories
   - Write seed files only where absent (or if `--force`)
   - Never overwrite files listed as canonical (`docs/canonical/`) without `--force`
   - In dry-run mode: compute and return intended actions without writing

2. Update `src/ai_build_toolkit/cli/init.py`
   - Add `--force` and `--dry-run` options
   - Resolve target directory: use `--repo` if set on context, else `Path.cwd()`
   - Call `init_service.init_repo()`
   - Print created / skipped / blocked clearly

3. Write tests in `tests/test_init_service.py`:
   - Fresh directory is scaffolded correctly
   - Existing files are skipped without `--force`
   - Existing canonical files are blocked even with content mismatch
   - `--dry-run` reports actions without writing
   - `--force` overwrites non-canonical files

## Required Directories (from `architecture.md` Section 5)
```
docs/canonical/
docs/working/
docs/runtime/
tasks/
templates/docs/
templates/tasks/
templates/prompts/
src/
tests/
```

## Patch Strategy
- New file: `src/ai_build_toolkit/services/init_service.py`
- Update: `src/ai_build_toolkit/cli/init.py`
- New file: `tests/test_init_service.py`
- No changes to other modules
