# Plan: TASK-0037

## Steps

1. Implement `context show` command options and output formatting in `src/forge/cli/context.py`.
2. Reuse `build_context_bundle` to support display both after build and independently.
3. Add tests covering text output, JSON output, include-working behavior, and unknown-task failure.
4. Run targeted tests, then full test suite.
