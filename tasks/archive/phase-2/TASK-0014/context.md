# Context: TASK-0014

## Required Documents

### Canonical
- `docs/canonical/data_contracts.md` — Section 6.2 (`authority` allowed values, `editable_by_agents` boolean rule)
- `docs/canonical/architecture.md` — Section 6.5 (`validators/` responsibility)

### Working
- `docs/working/implementation_plan.md` — Phase 2: authority-order validation

### Runtime
- `docs/runtime/PROJECT_RULES.md` — Section 3 (authority hierarchy and canonical change rules)

## Prior Work
- TASK-0012 (`done`): `domain/documents.py` — `DocumentRegistry` and `DocumentRecord` available
- TASK-0011 (`done`): `validators/manifest_validator.py` — sibling validator for pattern reference

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/domain/documents.py`
- `src/ai_build_toolkit/validators/__init__.py`
