# Plan: TASK-0010

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Mechanical task — reading a YAML file and returning parsed content. Error types are already defined. `reviewer_model` should verify the manifest path matches `data_contracts.md` Section 5 exactly and that loader placement is in `adapters/`, not `services/`.

## Steps

1. Add `PyYAML` to `pyproject.toml` dependencies
2. Create `src/ai_build_toolkit/adapters/manifest.py`:
   - `MANIFEST_PATH = "docs/runtime/docs_manifest.yaml"`
   - `load_manifest(root: Path) -> dict` — reads and parses the manifest YAML
   - Raises `MissingPathError` if file does not exist
   - Raises `ConfigError` if file exists but is not valid YAML
3. Write tests in `tests/test_manifest_loader.py`:
   - Valid manifest loads and returns a dict
   - Missing manifest raises `MissingPathError`
   - Malformed YAML raises `ConfigError`
   - Parsed content contains expected top-level keys

## Patch Strategy
- Update: `pyproject.toml` — add `PyYAML>=6.0`
- New file: `src/ai_build_toolkit/adapters/manifest.py`
- New file: `tests/test_manifest_loader.py`
- No changes to other modules
