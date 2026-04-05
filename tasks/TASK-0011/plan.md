# Plan: TASK-0011

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Requires careful mapping of `data_contracts.md` schema rules to validation logic across multiple nested sections. Low risk of explosing scope but requires precise rule encoding.

## Steps

1. Create `src/ai_build_toolkit/validators/manifest_validator.py`:
   - Define `REQUIRED_TOP_LEVEL` = `["version", "project", "canonical", "working", "runtime", "tasks", "rules"]`
   - Define `REQUIRED_DOC_ENTRY_FIELDS` = `["id", "path", "purpose", "authority", "editable_by_agents", "read_when"]`
   - Define `REQUIRED_TASKS_FIELDS` = `["root", "packet_files", "patch_dir", "status_values", "id_format"]`
   - Define `REQUIRED_RULES_SUBKEYS` = `["authority_order", "canonical_change_policy", "context_policy", "execution_policy", "completion_policy"]`
   - Define required fields per rules sub-key
   - Implement `validate_manifest_schema(manifest: dict) -> list[str]`

2. Write tests in `tests/test_manifest_validator.py`:
   - Valid manifest returns empty list
   - Missing top-level section returns error
   - Missing doc entry field returns error
   - Missing tasks sub-key returns error
   - Missing rules sub-key returns error
   - `editable_by_agents` non-boolean returns error
   - `read_when` empty list returns error

## Patch Strategy
- New file: `src/ai_build_toolkit/validators/manifest_validator.py`
- New file: `tests/test_manifest_validator.py`
- No other files touched
