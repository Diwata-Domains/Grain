# Task: Implement `grain docs audit`

## Metadata
- **ID:** TASK-0207
- **Status:** done
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T04
- **Packet Path:** tasks/P31-T04-TASK-0207/
- **Dependencies:** TASK-0204
- **Primary Adapter:** code

## Objective
Implement `grain docs audit` as specified in `docs/working/docs_audit_spec.md`. A read-only, <2s workspace health check across 6 document types.

## Implementation Steps

1. Create `src/grain/services/docs_audit_service.py` with:
   - 21 check functions (see `docs_audit_spec.md` §2 check definitions table)
   - Check runner that collects findings as structured dicts: `{doc, check_id, severity, message, remediation}`
   - `audit_thresholds` config reading from `docs_manifest.yaml` (defaults apply if absent)
   - `--doc` filter to run checks on a single document
   - `--severity` filter

2. Create/extend `src/grain/cli/docs.py`:
   - `grain docs audit` command with `--doc`, `--severity`, `--format`, `--fix`, `--fix --no-confirm` flags
   - Text output: section per doc, symbols (✓ ✗ ⚠), remediation hints on `→` lines
   - JSON output: `{run_at, summary, overall, findings: [...]}`

3. Write `.grain/last_docs_audit.json` at end of every audit run (for `grain status` caching)

4. Integrate with `grain workflow guard`:
   - `grain workflow guard --check-docs` calls `docs_audit_service` and includes error findings as violations, warning findings as guard warnings

5. Auto-fixable check implementations:
   - `current_task_stale_pointer` → clears `current_task.md` to unset (after prompt, or `--no-confirm`)
   - Other auto-fixes are hints only (no code change)

## Deliverable
- `grain docs audit` command fully working
- All 21 checks implemented
- `grain --format json docs audit` returns stable structured output
- `grain workflow guard --check-docs` integration working
- Tests: one test per check covering pass and fail conditions

## Constraints
- All checks are read-only (except `--fix`)
- <2s on a typical workspace (no large file scans — use line-count heuristics, not full parse)
- All checks degrade gracefully when target doc is missing (`doc_missing` finding, not crash)
- `--format json` output goes to stdout only; progress/banners go to stderr
