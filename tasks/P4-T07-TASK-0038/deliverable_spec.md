# Deliverable Spec: TASK-0038

## Required Deliverables

- [x] `src/forge/adapters/export.py` with markdown export writer
- [x] `forge context export` implemented in `src/forge/cli/context.py`
- [x] JSON output emits structured source metadata only
- [x] command tests in `tests/test_context_export_cmd.py`
- [x] no regressions in existing tests

## Acceptance Criteria

- [x] `forge context export --id TASK-####` writes one assembled markdown file with source metadata header
- [x] `forge context export --id TASK-#### --output <path>` writes to the requested path
- [x] `--format json` returns structured source metadata and does not emit full content body
- [x] unknown packet ID returns usage-style failure (exit code 2)
- [x] existing context build/show tests remain passing
