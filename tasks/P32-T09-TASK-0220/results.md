# Results — TASK-0220

## Summary

Shipped the two GitHub feedback surfaces for v0.4.0:

1. `grain report` — the canonical, token-free, browser-confirmed URL path from
   `feedback_spec.md`. Scans open Grain-related tooling notes, lists candidates,
   and for a selected `--id` builds a privacy-preserving pre-filled GitHub
   new-issue URL, opens the browser (or prints with `--no-browser`), and marks
   the row `reported`. Nothing is sent automatically.
2. `grain notes publish <id>` — token-based REST API path that files a logged
   note as an issue in `github.repo`, maps the note type to a label
   (bug→bug, friction/feature→enhancement), prints the created issue URL, and
   marks the note `published`. Headless; no browser.
3. `grain issue create --title --type` — standalone API path that files an issue
   directly without touching the notes log.

Token is read from `GRAIN_GITHUB_TOKEN` (env only, never written to workspace
files). Missing token / missing `github.repo` yield clear, non-crashing errors.
The HTTP layer is funneled through an injectable `http_post` (default stdlib
urllib wrapper `_urllib_post`) so tests never touch the network.

## Files

Created:
- `src/grain/services/github_service.py` — URL builder + REST issue client +
  type→label mapping; injectable HTTP poster.
- `src/grain/cli/report.py` — `grain report` command.
- `src/grain/cli/issue.py` — `grain issue create` command group.
- `tests/test_github_service.py`, `tests/test_report_cmd.py`,
  `tests/test_notes_publish.py`.

Modified:
- `src/grain/adapters/manifest.py` — `GithubConfig` + `load_github_config`
  (never raises).
- `src/grain/cli/notes.py` — added `notes publish <id>`.
- `src/grain/cli/__init__.py` — registered `report_cmd` and `issue_group`
  (import block + add_command).
- `src/grain/services/notes_service.py` — `set_note_status` + `NoteStatusResult`.
- `src/grain/domain/notes.py` — added `reported`/`published` to `NOTE_STATUSES`.
- `docs/runtime/docs_manifest.yaml` and
  `src/grain/data/runtime/docs_manifest.yaml` — seeded the `github:` block.

## Test Results

`uv run --with pytest python -m pytest -q` → 1320 passed, 1 xfailed.
New tests: 32 passing (URL encoding/labels/privacy, mocked API payload, missing
token/repo errors, report selection/--no-browser/JSON/row-marking, publish label
mapping and note-marking, standalone issue create).
