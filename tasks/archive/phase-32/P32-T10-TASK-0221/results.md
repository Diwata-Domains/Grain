# Results — TASK-0221 docs-audit hygiene

## What shipped

1. **New check `phase_status_consistency`** (error severity, scoped to
   `current_focus.md`, not auto-fixable). Added `_check_phase_status_consistency(text)`
   to `docs_audit_service.py` and wired it into `_check_current_focus` (appended via
   `findings.extend(...)` before the return). Fires when a phase number is described as
   both active and closed in the same file, or when the declared Current Phase appears
   in the closed-phase ledger. Emits a single `pass` finding when clean. Added
   module-level `_ACTIVE_RE` and `_CLOSED_LINE_RE` regexes next to the existing
   `_TASK_REF_RE`/`_DATE_RE`.

2. **Bug fix — `current_focus_phase_mismatch`.** The backlog-heading regex was
   `##\s+\d+\.\s+Phase\s+N\s+—`, which never matched the real heading format
   `## Phase N — Title` (no leading `N.`), so every phase false-positived as a warning.
   Changed to `##\s+(?:\d+\.\s+)?Phase\s+{num}\b` (optional leading `N.`). Verified it
   now PASSES against the live backlog for Phase 32.

3. **Spec.** Documented `phase_status_consistency` in `docs_audit_spec.md`
   (current_focus.md checks table) and added a not-auto-fixable note to the
   Auto-Fixable Checks section. No "18 checks" narrative existed to bump (the only
   stale count lives in the immutable Phase-31 archive backlog, left untouched).

`current_focus.md` was NOT rewritten — it was already rewritten in the planning commit.

## Files

- `src/grain/services/docs_audit_service.py` — new check + regexes + bug fix
- `docs/working/docs_audit_spec.md` — check row + not-auto-fixable note
- `tests/test_docs_audit_cmd.py` — 3 phase_status_consistency tests + 1 regression test
- `tasks/P32-T10-TASK-0221/task.md` — status → done
- `tasks/P32-T10-TASK-0221/results.md` — this file

## Tests

- `test_phase_status_consistency_pass_when_distinct`
- `test_phase_status_consistency_error_when_same_phase_active_and_closed`
- `test_phase_status_consistency_error_when_current_phase_in_ledger`
- `test_current_focus_phase_mismatch_pass_for_unnumbered_heading` (regression for the
  `## Phase N —` backlog format)

Full suite: 1369 passed, 1 xfailed. `grain docs audit --doc current_focus` is clean
(4 pass, 0 warning, 0 error) on the live workspace.
