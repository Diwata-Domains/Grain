# Results — TASK-0213

## Summary
Implemented the `grain suggest` engine per `docs/canonical/suggest_spec.md`: a deterministic,
file-backed, proposal-only suggestion system. It reads local workspace signals (ready backlog
tasks in the active / next-blocked phase, blocking/decision_needed open questions, aging
high-severity open tooling notes, last 3 git commits, phase boundary), applies the section-4
quality bar, and emits ranked `pick-up` and `new-task` proposals persisted as
`docs/working/proposals/SUG-YYYYMMDD-NNN.md`. Nothing is acted on without an explicit
`accept`/`dismiss`; `new-task` accept always re-prompts before any packet is created (D4).
Generation is fully deterministic — no network, no LLM. Lifecycle (expiry, prune) and
`--format json` are supported on every subcommand.

## Deliverables
- `src/grain/domain/suggest.py` — `SuggestionProposal` dataclass, id pattern/parse, kind/status constants.
- `src/grain/services/suggest_service.py` — engine + proposal I/O:
  - proposal render/parse round-trip, `allocate_proposal_id`, `set_proposal_status`, read/write/list.
  - signal readers reusing `docs_audit_service._parse_backlog_phases`, OQ + high-severity tooling parsers,
    and `workflow_service._read_current_phase`/`_read_current_task`; `read_recent_commits` via `git log -3`.
  - quality bar (ready + active/next-blocked phase, not in_progress, not recently committed; new-task
    traceable signal ref + concrete objective + ≥70% token-overlap dedupe).
  - `generate` (expire → build → suppress-already-surfaced → persist → auto-prune), `list_proposals`,
    `show_proposal`, `accept` (pick-up via workflow_run activation path; new-task via task_service with
    D4 confirm gate; expired-signal guard), `dismiss`, `prune`, and read-only `top_suggestion`.
- `src/grain/cli/suggest.py` — `grain suggest` (generate, `--type`, `--limit`, `--prune`),
  `suggest list/show/accept/dismiss`; text + JSON; registered in `cli/__init__.py` (both places).
- Hardened `archive_service.move_working_proposals_to_archive` to key off the parsed `**Status:**`
  field (expired always eligible; dismissed eligible only >30d) instead of substring matching.
- Added the `proposals` directory entry to the live `docs/runtime/docs_manifest.yaml`
  (already present in the bundled `src/grain/data/runtime/docs_manifest.yaml`) and created
  `docs/working/proposals/.gitkeep`.

## Test Results
- `tests/test_suggest_service.py` — 19 tests (id allocation, md round-trip, status preservation,
  pick-up/new-task quality bar, recently-committed exclusion, OQ/tooling signals, token-similarity
  dedupe, offline/no-git, determinism/idempotency, expiry, accept pick-up/new-task confirm,
  expired-signal no-op, dismiss suppression, prune, surface-only top_suggestion).
- `tests/test_suggest_cmd.py` — 12 tests (generate text/json, empty, list/show + status filter,
  unknown id error, accept pick-up, new-task confirm (D4) text + json, dismiss suppression, prune,
  group registration).
- `tests/test_command_groups.py` — extended with the `suggest` group + subcommands.
- Full suite: 1234 passed, 1 xfailed (baseline was 1192 passed, 1 xfailed).

## User Review
- **State:** approved

## Verification Review
- **State:** passed

## Closure Decision
- **Decision:** closed
- **Reason:** All acceptance criteria met; deterministic proposal-only engine with accept/dismiss/prune and JSON; full suite green.

### Closure Blockers
- None
