# Plan: TASK-0065

## Approach

1. Add `bootstrapped_task_id: str = ""` to `InitResult`.
2. Add `bootstrap: bool = False` parameter to `init_repo()`.
3. After adapter selection, call `_run_bootstrap(root, result, dry_run)` if bootstrap is True.
4. `_run_bootstrap`: in non-dry_run mode, call `create_packet_directory(root, 1, 1, "Starter Task")`, record created files, patch task.md adapter if primary_adapter set, write current_task.md. In dry_run mode, predict task ID and report without writing.
5. `_patch_task_adapter`: find the packet dir, replace `**Primary Adapter:** none` with the validated adapter ID.
6. Add `bootstrapped_task_id: str = ""` to `CommandResult`; print in text output.
7. Add `--bootstrap` flag to `init_cmd`; pass through; surface in CommandResult.
8. Add 6 service tests + 2 CLI tests.

## File Changes
- `src/forge/services/init_service.py` — InitResult field, init_repo signature, _run_bootstrap, _patch_task_adapter
- `src/forge/cli/init.py` — --bootstrap option, pass-through, CommandResult field
- `src/forge/cli/output.py` — bootstrapped_task_id field, text print
- `tests/test_init_service.py` — 6 new bootstrap tests
- `tests/test_task_create_cmd.py` — 2 new CLI bootstrap tests

## Risks
- None. All changes are additive. Existing tests unaffected when bootstrap is not passed.
