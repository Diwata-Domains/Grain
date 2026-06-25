# Task: grain notes full implementation (queryable friction inbox)

## Metadata
- **ID:** TASK-0217
- **Status:** ready
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T06
- **Packet Path:** tasks/P32-T06-TASK-0217/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Graduate `grain notes` from a write-only stub to a queryable, actionable friction inbox backed by structured rows in `docs/working/tooling_notes.md`.

## Why This Task Exists
Every Grain session accumulates friction. Today it can only be appended, never queried or resolved. A real inbox makes friction actionable and feeds both `grain docs audit` and the GitHub feedback path (P32-T09).

## Scope / Implementation Steps
1. Create `src/grain/services/notes_service.py`: parse/write structured rows (`id`, `type`, `status`, `created_at`, `body`); auto-assign incremental ID + timestamp; default status `open`.
2. Extend `src/grain/cli/notes.py`: `grain notes add` (auto id/timestamp/open), `grain notes list --type --status --format json`, `grain notes show <id>`, `grain notes resolve <id>` (optional resolution note).
3. Extend `src/grain/services/docs_audit_service.py`: open notes of type `bug`/`friction` surface as `low`-severity findings.
4. Keep `tooling_notes.md` human-readable (table rows).

## Acceptance Criteria
- `grain notes add` writes a structured row with auto ID, timestamp, and `open` status.
- `grain notes list` filters by `--type`/`--status`; `--format json` returns a notes array.
- `grain notes show <id>` and `grain notes resolve <id>` work; resolve records optional note + flips status.
- Open `bug`/`friction` notes appear as low-severity `grain docs audit` findings.
- No regression: full suite green.

## Tests
- `tests/test_notes_service.py` — add/list/show/resolve, ID allocation, filters.
- `tests/test_notes_cmd.py` — CLI text + JSON.
- docs-audit test — open bug/friction note surfaces as a finding.

## Constraints
- `tooling_notes.md` stays the single file-backed source; no DB.
- Backward-compatible with existing rows where feasible.

## Escalation Conditions
- Existing tooling_notes rows are unparseable under the new schema — add a migration/normalization step, do not drop data.
