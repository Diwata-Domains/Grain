# Results — TASK-0201

## Status
done — 2026-06-11

## Deliverable
`docs/working/cli_ergonomics_spec.md` — CLI ergonomics spec.

## Key Decisions

**11 commands need `--format json`:** Prioritized. All high-priority ones (docs audit, suggest, status) land in Phase 31.

**Stop reason vocabulary:** 11 canonical stop reasons. Never renamed without major version bump. Always in `stop_reason` key in JSON output.

**Text output style:** Consistent symbol set (✓ ✗ ⚠ → + ~). Key-value pad to col 20. Command hints always on `→` lines. Progress to stderr only when JSON active.

**`grain status`:** Single command for full workspace state. <1 second via cached state files (`.grain/last_workflow_state.json`, `.grain/last_docs_audit.json`). Falls back to live computation. Added `upgrade_required` stop reason.

**`cli_spec.md` update:** Phase 31 must add "JSON Output Schemas" section documenting all `--format json` outputs as the machine-readable integration contract.

## Files Changed
- `docs/working/cli_ergonomics_spec.md` — created
- `tasks/P30-T12-TASK-0201/task.md` — status set to done
