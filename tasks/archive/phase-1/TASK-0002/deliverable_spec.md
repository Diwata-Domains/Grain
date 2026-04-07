# Deliverable Spec: TASK-0002

## Definition of Done

This task is complete when all of the following are true:

1. `abt` is registered as a script entrypoint in `pyproject.toml`
2. `abt --help` runs without error and exits with code `0`
3. `abt <unknown-group>` returns a clear error message and exits with code `2`
4. Top-level dispatch is in place and routes to group handlers (stubs acceptable)
5. CLI layer contains no business logic, no service calls, no packet or manifest logic
6. Smoke test exists and passes: entrypoint callable, `--help` exits `0`, unknown group exits `2`

## Out of Scope
- Implementing any command group logic (TASK-0003)
- Full output formatting and `--format` flag (P1-T07)
- Shared error types and full exit code mapping (P1-T08)
- Any service, domain, adapter, or validator wiring
