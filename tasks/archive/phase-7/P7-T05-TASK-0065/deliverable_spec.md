# Deliverable Spec: TASK-0065

## Acceptance Criteria

1. `forge init --bootstrap` creates `tasks/P1-T01-TASK-0001/` with required template files.
2. `forge init --bootstrap` writes `docs/working/current_task.md` with `Status: ready`.
3. `forge init --bootstrap --primary-adapter code_adapter` sets `**Primary Adapter:** code_adapter` in the starter task.md.
4. `forge init --bootstrap` without adapter leaves `**Primary Adapter:** none` in the starter task.md.
5. `forge init --bootstrap --dry-run` reports intended actions without writing anything.
6. `forge init` without `--bootstrap` produces no bootstrap output and no `bootstrapped_task_id` (adapter-neutral, existing behavior unchanged).
7. JSON output includes `bootstrapped_task_id` field.
8. 6 new service tests pass.
9. 2 new CLI tests pass.
10. Full test suite passes (417 tests).
