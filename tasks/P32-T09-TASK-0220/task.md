# Task: GitHub feedback — grain report (URL) + grain notes publish (API)

## Metadata
- **ID:** TASK-0220
- **Status:** ready
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T09
- **Packet Path:** tasks/P32-T09-TASK-0220/
- **Dependencies:** TASK-0217
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Provide two GitHub feedback surfaces. (1) `grain report` — the canonical, URL-based, browser-confirmed upstream path from `feedback_spec.md` (no token; user reviews and submits). (2) `grain notes publish <id>` — a token-based REST API path that files a note as an issue in the workspace's own repo with no browser and no human click (works headless for agent/familiar-driven use).

## Why This Task Exists
`grain report` lets users send friction to Grain's maintainer with full transparency and no auth. `grain notes publish` turns the local friction log into tracked issues in the user's own repo and is the only path that works when an agent (a 'familiar') drives Grain with no browser. Both are needed for the v0.4.0 feedback story.

## Scope / Implementation Steps
1. Create `src/grain/services/github_service.py`: (a) pre-filled issue **URL builder** per `feedback_spec.md` (title/body/labels, URL-encoded, privacy-preserving); (b) **REST API client** that POSTs an issue using `GRAIN_GITHUB_TOKEN` to `github.repo` from `docs_manifest.yaml`.
2. `grain report` (new `src/grain/cli/report.py`): scan `tooling_notes.md` open Grain-related rows, select, build URL, open browser or `--no-browser` print, `--format json`; mark row `reported`. Never send file contents/paths/PII.
3. `grain notes publish <id>` (extend `src/grain/cli/notes.py`): create the issue via the API client, map type→label (`bug`→`bug`, `friction`/`feature`→`enhancement`), print the created issue URL, mark the note `published`. Token via env only — never written to workspace files.
4. `grain issue create --title --type bug|feature|friction` (standalone API path that skips the notes log).
5. Add `github.repo` to the manifest schema/loader; document `GRAIN_GITHUB_TOKEN`.

## Acceptance Criteria
- `grain report` builds a correct pre-filled issue URL, opens browser (or prints with `--no-browser`), marks the row `reported`, and never includes file contents/paths/PII.
- `grain notes publish <id>` creates a real issue via the API (mocked in tests), applies the right label, prints the URL, and marks the note `published`.
- `grain issue create` files an issue directly without touching the notes log.
- Token is read from `GRAIN_GITHUB_TOKEN` only; absent token yields a clear, non-crashing error.
- No regression: full suite green.

## Tests
- `tests/test_github_service.py` — URL construction (encoding, labels, privacy), API payload with a mocked HTTP client.
- `tests/test_report_cmd.py` — selection, `--no-browser`, JSON, row marked reported.
- `tests/test_notes_publish.py` — publish with mocked API, label mapping, missing-token error, note marked published.

## Constraints
- `grain report` sends nothing automatically — browser-confirmed, no token.
- `grain notes publish` never stores the token in workspace files.
- No network calls in tests — mock the HTTP client.

## Escalation Conditions
- GitHub API contract or auth differs from assumption — stop and confirm before shipping the API path; the URL path must remain fully functional independently.
