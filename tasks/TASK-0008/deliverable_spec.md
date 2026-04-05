# Deliverable Spec: TASK-0008

## Definition of Done

This task is complete when all of the following are true:

1. `src/ai_build_toolkit/domain/errors.py` defines `AbtError` and one subclass per exit code:

| Exception | Exit Code | Meaning |
|---|---|---|
| `GeneralError` | 1 | general command failure |
| `UsageError` | 2 | invalid arguments or usage |
| `ValidationError` | 3 | validation failure |
| `MissingPathError` | 4 | missing required file or path |
| `InvalidTransitionError` | 5 | state transition not allowed |
| `ConfigError` | 6 | configuration or manifest error |
| `AdapterError` | 7 | external adapter/integration error |

2. `src/ai_build_toolkit/cli/error_handler.py` maps exceptions to exit codes and formats error output
3. `main()` catches `AbtError` and exits with the correct code
4. Error messages state what failed, where, and what artifact caused the failure
5. Exception classes live in `domain/errors.py`, not in `cli/`
6. Tests cover all seven exit code mappings — all passing

## Out of Scope
- Applying typed exceptions to commands beyond `abt init`
- Structured JSON error output (follows from TASK-0007)
- Any service, adapter, or validator changes
