# Results — TASK-0217

## Summary
Graduated `grain notes` from a write-only stub to a queryable, actionable
friction inbox backed by structured rows in `docs/working/tooling_notes.md`.
Notes now carry an auto-incremented ID, a timestamp, a type, and a default
`open` status. The inbox is queryable (`list`, `show`), resolvable
(`resolve`), and open `bug`/`friction` notes surface as findings in
`grain docs audit`. Backward compatibility with pre-existing (un-IDed,
six-column) rows is preserved — they are normalized on read and never dropped.

## Deliverables
- `grain notes add <message>` — appends a structured row (auto ID, timestamp,
  `open` status); `--type`, `--command`, `--severity` options.
- `grain notes list` — filters by `--type` / `--status` (default: open);
  `--format json` returns a notes array.
- `grain notes show <id>` — single note by ID (exit 2 if not found).
- `grain notes resolve <id> [resolution]` — flips status to `resolved` and
  appends an optional resolution note in-place.
- `grain docs audit` — new `tooling_notes_open_friction` check: each open
  `bug`/`friction` note is a low-severity (warning) finding with a
  `grain notes resolve <id>` remediation.
- Canonical table schema gains a leading `ID` column:
  `| ID | Date | Type | Command | Observation | Severity | Status |`.

## Files Changed
- `src/grain/domain/notes.py` (new) — `Note` dataclass, table-schema
  constants, enum frozensets, and a dual-format (7-col + legacy 6-col)
  row parser.
- `src/grain/services/notes_service.py` (new) — `add_note`, `list_notes`,
  `show_note`, `resolve_note`, ID allocation, legacy normalization,
  in-place table rewrite.
- `src/grain/cli/notes.py` — full implementation (add/list/show/resolve) over
  the service; text + JSON output. (already registered in `cli/__init__.py`)
- `src/grain/services/docs_audit_service.py` — `tooling_notes_open_friction`
  finding + `_open_actionable_notes` helper.
- `src/grain/data/runtime/tooling_notes.md` (seed) — header updated to the
  canonical `ID` schema so new repos start structured.
- `tests/test_notes_service.py` (new), `tests/test_notes_cmd.py` (new),
  `tests/test_docs_audit_cmd.py` (+3 friction-finding tests),
  `tests/test_cli_ergonomics.py` (2 JSON-shape assertions updated to the
  new contract).

## Test Results
Full suite: `uv run --with pytest python -m pytest -q` → 1288 passed, 1 xfailed.
New/changed tests pass; ruff clean on all changed source and test files.
Verified backward compat against the live `docs/working/tooling_notes.md`:
all 6 legacy rows parse with synthesized IDs, no data dropped, no false
audit findings (legacy types are not exactly `bug`/`friction`).
