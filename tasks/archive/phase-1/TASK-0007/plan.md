# Plan: TASK-0007

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Mechanical task — defining a formatting dataclass and a small output function. No design ambiguity beyond Q6, which is resolved by defaulting to text-first. `reviewer_model` should verify field names match `cli_spec.md` Section 10 and that the formatter is not placed in services or domain.

## Steps

1. Create `src/ai_build_toolkit/cli/output.py`:
   - Define `CommandResult` dataclass with fields from `cli_spec.md` Section 10: `ok`, `command`, `files_created`, `files_updated`, `files_skipped`, `files_blocked`, `errors`, `warnings`
   - Implement `print_result(result: CommandResult, fmt: str = "text") -> None`
     - `text`: print status line, then lists of files and errors in a readable format
     - `json`: serialise `CommandResult` to JSON and print

2. Update `src/ai_build_toolkit/cli/init.py`:
   - Replace direct `click.echo` calls with a `CommandResult` returned from `init_service`
   - Pass `--format` option through to `print_result`

3. Add `--format` option to `main` Click group (or per-command — apply to `init` for now)

4. Write tests in `tests/test_output_formatter.py`:
   - text output contains expected fields
   - JSON output is valid JSON with expected keys
   - empty result prints cleanly

## Patch Strategy
- New file: `src/ai_build_toolkit/cli/output.py`
- Update: `src/ai_build_toolkit/cli/init.py`
- New file: `tests/test_output_formatter.py`
- No changes to services, domain, adapters, or validators
