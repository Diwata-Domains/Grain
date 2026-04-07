# Plan: TASK-0035

## Steps

1. Add `ContextBundle` to `src/forge/domain/context.py` with packet files, selected canonical docs, optional working docs, and export metadata.
2. Add focused tests for required fields and optional metadata handling in `tests/test_context_bundle.py`.
3. Run the context-related tests and then the full suite if the targeted tests pass.
