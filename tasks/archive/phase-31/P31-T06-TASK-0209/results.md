# Results — TASK-0209

## Summary

All CLI ergonomics improvements implemented. 1129 tests pass.

## Deliverables

### Stop reason constants (`workflow_service.py`)
17 constants defined (`STOP_REQUIRED_DOCS_MISSING`, `STOP_PACKET_REQUIRED`, etc.) with one-line descriptions. All inline `stop_reason="..."` string literals replaced with constants throughout the service.

### `grain --version` install mode
`grain, version 0.3.0 (editable)` — `detect_install_mode()` reads `direct_url.json` from dist-info; falls back to source-path detection for dev installs.

### `grain doctor` (`doctor_service.py` + `doctor.py`)
5 checks: version_match, mtime_ok, install_mode_ok, workspace_resolved. JSON output with `overall: "ok" | "drift_detected"`. Text output with ✓/✗ per check.

### `grain status` (`status.py`)
Reads `.grain/last_workflow_state.json` (<5 min) and `.grain/last_docs_audit.json` (<10 min) as caches; computes live on miss. JSON output: `{run_at, phase, tasks, current_task, workflow, health, install}`. Task counts from backlog by active phase.

### `grain notes` stub (`notes.py`)
`grain notes add <message>` appends a correctly-formatted table row to `docs/working/tooling_notes.md`. `grain notes list` reads and filters rows. Both support `--format json`.

### Tests (`test_cli_ergonomics.py`)
21 tests: stop reason constants, --version mode, doctor text/JSON, status JSON contract, cache reading, notes add/list.

## User Review

- **State:** approved

## Verification Review

- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
