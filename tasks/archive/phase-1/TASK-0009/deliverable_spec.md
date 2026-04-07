# Deliverable Spec: TASK-0009

## Definition of Done

This task is complete when all of the following are true:

1. `abt --version` exits 0 and prints the version from `pyproject.toml`
2. `abt --help` exits 0 and output lists all six command groups
3. `abt <unknown>` exits 2 (confirmed via subprocess)
4. `tests/test_smoke.py` exists with subprocess-level tests — all passing
5. Full test suite continues to pass (no regressions)
6. Phase 1 is declared complete: all P1-T01 through P1-T09 done

## Out of Scope
- Testing any command's actual behavior beyond help and version
- JSON output smoke testing (covered in TASK-0007)
- Any Phase 2 work
