# Deliverable Spec: TASK-0019

## Required Output

### New File
- `src/ai_build_toolkit/domain/packets.py`
  - Contains `TASK_ID_PATTERN` regex constant
  - Contains `next_task_id(tasks_root: Path) -> str` function

### New Test File
- `tests/test_task_id.py`
  - 7 test cases (see task.md § Tests Required)
  - All passing

## Acceptance Checklist
- [ ] `domain/packets.py` exists
- [ ] `next_task_id` is importable from `ai_build_toolkit.domain.packets`
- [ ] Returns `"TASK-0001"` for empty or missing tasks directory
- [ ] Returns correct next ID when packets exist (max + 1, zero-padded)
- [ ] Handles both legacy `TASK-####` and `P<N>-T<NN>-TASK-####` directory names
- [ ] Non-packet directories are silently ignored
- [ ] All 7 tests passing
- [ ] Full test suite passing with no regressions

## Not Required
- No changes to CLI, services, adapters, or validators
- No changes to existing files
- No directory creation logic (that belongs to P3-T03)
- No `PacketRecord` dataclass (belongs to P3-T07 or later)
