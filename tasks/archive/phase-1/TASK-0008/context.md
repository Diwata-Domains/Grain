# Context: TASK-0008

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 4.6 (error rule: what failed, where, what artifact), Section 5 (exit code conventions: 0–7)
- `docs/canonical/architecture.md` — Section 6.3 (`domain/` for core models and pure logic), Section 6.1 (`cli/` for dispatch and formatting)

### Working
- `docs/working/implementation_plan.md` — Phase 1: exit code and error handling conventions
- `docs/working/current_focus.md` — confirms P1-T08 is remaining Phase 1 work

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0001 (`done`): `src/ai_build_toolkit/domain/__init__.py` exists
- TASK-0002 (`done`): `main()` Click group exists
- TASK-0007 (`draft`): `CommandResult` and `print_result()` — error fields available once implemented

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/domain/__init__.py`
- `src/ai_build_toolkit/cli/__init__.py`
- `src/ai_build_toolkit/cli/init.py`
