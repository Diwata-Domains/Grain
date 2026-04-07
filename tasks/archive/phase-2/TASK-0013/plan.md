# Plan: TASK-0013

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Mechanical path existence check against a registry. No structural ambiguity.

## Steps

1. Create `src/ai_build_toolkit/validators/doc_existence_validator.py`:
   - `validate_doc_existence(registry: DocumentRegistry, root: Path) -> list[str]`
   - Iterate `registry.all()`
   - For each record: check `(root / record.path).exists()`
   - Treat empty `path` as missing
   - Append error string with record `id` and expected path for each missing entry

2. Write tests in `tests/test_doc_existence_validator.py`:
   - All paths present returns empty list
   - Missing file returns error with record id
   - Missing directory returns error
   - Empty path string returns error
   - Empty registry returns empty list

## Patch Strategy
- New file: `src/ai_build_toolkit/validators/doc_existence_validator.py`
- New file: `tests/test_doc_existence_validator.py`
- No other files touched
