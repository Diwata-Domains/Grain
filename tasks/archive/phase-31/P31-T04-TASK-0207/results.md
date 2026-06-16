# Results — TASK-0207

## Summary

`grain docs audit` implemented with 18 checks across 6 document types. 1077 tests pass. Guard integration live.

## Deliverables

### `src/grain/services/docs_audit_service.py` (new)
18 checks implemented:
- `current_task`: stale_pointer, missing_packet, idle
- `backlog`: inprogress_no_packet, done_no_results, phase_status_drift, phase_closed_with_open_tasks
- `current_focus`: phase_mismatch, stale, priorities_done
- `open_questions`: blocking_accumulation, stale_open
- `tooling_notes`: high_severity_aging, overdue_triage
- `change_proposals`: proposal_aging
- `structural`: registered_doc_missing, registered_doc_empty, required_section_missing

All checks degrade gracefully (doc_missing → pass/skip, not crash). `AuditConfig` reads thresholds from `audit_thresholds` in docs_manifest.yaml; all defaults apply if block absent. `save_audit_cache()` writes `.grain/last_docs_audit.json`. `apply_fixes()` handles `current_task_stale_pointer` with prompt or `--no-confirm`.

### `src/grain/cli/docs.py` — `grain docs audit` command
`--doc`, `--severity`, `--fix`, `--no-confirm` flags. Text output: section per doc with ✓ ✗ ⚠ symbols. JSON output: `{run_at, summary, overall, findings}`.

### `src/grain/services/guard_service.py` — `--check-docs` stub replaced
`_check_docs_health()` calls `run_audit()` and maps error findings → guard violations, warning findings → guard warnings.

### `tests/test_docs_audit_cmd.py` (new)
41 tests — pass and fail condition per check, CLI text/JSON format, doc filter, severity filter, cache file.

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
