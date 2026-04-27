# Plan: P2-T09-TASK-0017

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Mechanical work — write YAML files and pytest fixtures, then swap setup helpers in two test files. No structural decisions required.

## Steps

1. Create `tests/fixtures/` directory and four YAML fixture files:
   - `valid_manifest.yaml` — complete valid manifest (all required sections + fields)
   - `manifest_missing_section.yaml` — same but with `rules:` section removed
   - `manifest_bad_authority.yaml` — canonical entry with `authority: "super_high"`
   - `manifest_editable_canonical.yaml` — canonical entry with `editable_by_agents: true`

2. Create `tests/conftest.py`:
   - `valid_manifest_dict` fixture — loads `valid_manifest.yaml` via `yaml.safe_load`
   - `valid_repo` fixture (uses `tmp_path`) — writes `valid_manifest.yaml` to
     `docs/runtime/docs_manifest.yaml` and creates all declared file paths

3. Refactor `tests/test_docs_validate_cmd.py`:
   - Replace `_minimal_valid_manifest()` helper with `valid_repo` fixture
   - Keep all existing assertions unchanged

4. Refactor `tests/test_docs_show_cmd.py`:
   - Replace `_setup_repo()` helper with `valid_repo` fixture
   - Keep all existing assertions unchanged

## Patch Strategy
- New directory: `tests/fixtures/`
- New files: 4 YAML fixture files
- New file: `tests/conftest.py`
- Update: `tests/test_docs_validate_cmd.py`
- Update: `tests/test_docs_show_cmd.py`
