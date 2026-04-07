# Results: P3-T03-TASK-0022

## Status
done

## Files Changed
- `src/ai_build_toolkit/services/task_service.py` — new, `create_packet_directory(root, phase, task_num)`
- `tests/conftest.py` — added `_TEMPLATES_DIR` constant and `packet_repo` fixture
- `tests/test_task_create_dir.py` — new, 11 tests

## Summary
`create_packet_directory` allocates the next TASK-#### ID via `next_task_id()`,
constructs the `P<N>-T<NN>-TASK-####` directory name, creates the directory under
`tasks/`, and populates it with the four required template files by reading from
`templates/tasks/` via `get_template()`. Returns a `CommandResult` with `task_id`
set and `files_created` listing the directory and all four files (5 entries total).

Added `packet_repo` fixture to conftest.py — provides a tmp_path with the repo
marker, templates directory (copied from real templates), and an empty tasks/
directory. All future task service tests will use this fixture.

## Test Results
11/11 new tests passing. 189/189 total passing (no regressions).

## Deliverable Checklist
- [x] `task_service.py` exists with `create_packet_directory()`
- [x] Allocates next TASK-#### via `next_task_id()`
- [x] Directory named `P<N>-T<NN>-TASK-####`
- [x] Creates all 4 required template files in new directory
- [x] Returns CommandResult with task_id and files_created
- [x] `packet_repo` fixture added to conftest.py
- [x] 11/11 tests passing
- [x] Full suite passing (189/189)

## Blockers
None.
