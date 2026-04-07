# Plan: TASK-0008

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Mechanical task — defining exception classes and a mapping table. The exit codes are fully specified in `cli_spec.md` Section 5. `reviewer_model` should verify all seven codes are present and exception placement matches `architecture.md` module boundaries.

## Steps

1. Create `src/ai_build_toolkit/domain/errors.py`:
   - `AbtError` — base exception with `message` and optional `detail`
   - `GeneralError(AbtError)` → exit code 1
   - `UsageError(AbtError)` → exit code 2
   - `ValidationError(AbtError)` → exit code 3
   - `MissingPathError(AbtError)` → exit code 4
   - `InvalidTransitionError(AbtError)` → exit code 5
   - `ConfigError(AbtError)` → exit code 6
   - `AdapterError(AbtError)` → exit code 7

2. Create `src/ai_build_toolkit/cli/error_handler.py`:
   - `EXIT_CODES: dict[type, int]` mapping each exception type to its code
   - `handle_error(exc: AbtError) -> int` — prints the error message and returns the exit code

3. Update `src/ai_build_toolkit/cli/__init__.py`:
   - Wrap `main()` invocation to catch `AbtError`, call `handle_error()`, and `sys.exit()` with the returned code

4. Update `src/ai_build_toolkit/cli/init.py`:
   - Replace any bare `click.echo` error paths with raises of the appropriate `AbtError` subclass

5. Write tests in `tests/test_error_handler.py`:
   - Each exception type maps to the correct exit code
   - Error message is printed to output
   - Unknown exception does not suppress the error

## Patch Strategy
- New file: `src/ai_build_toolkit/domain/errors.py`
- New file: `src/ai_build_toolkit/cli/error_handler.py`
- Update: `src/ai_build_toolkit/cli/__init__.py`
- Update: `src/ai_build_toolkit/cli/init.py`
- New file: `tests/test_error_handler.py`
