# Task: Implement grain suggest engine (proposals, signals, accept/dismiss/prune)

## Metadata
- **ID:** TASK-0213
- **Status:** done
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T02
- **Packet Path:** tasks/P32-T02-TASK-0213/
- **Dependencies:** TASK-0212
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Implement `grain suggest` per `docs/canonical/suggest_spec.md`: a deterministic, file-backed, proposal-only engine that reads local workspace signals and emits ranked candidate suggestions. Nothing is written to the backlog or activated without explicit operator approval.

## Why This Task Exists
`grain suggest` is the foundation of the v0.4.0 Proactive Assistance release and the dependency for recipe-suggest, signal ingestion, and the engine-contract suggest tools in later milestones.

## Scope / Implementation Steps
1. **Domain model + proposal I/O** — `src/grain/domain/suggest.py`: `SuggestionProposal` dataclass (`id` `SUG-YYYYMMDD-NNN`, `kind` `pick-up|new-task`, `title`, `rationale`, `signals: list`, `status` `pending|accepted|dismissed`, `created_at`, `expires_at`). Read/write proposal files in `docs/working/proposals/`; next-ID allocation per day.
2. **Signal readers (deterministic)** — `src/grain/services/suggest_service.py`: reuse existing parsers (do not reimplement) — backlog ready tasks (`workflow_service` phase/backlog readers), blocking/decision_needed open questions and aging high-severity tooling notes (`docs_audit_service` parsers), last 3 git commits, phase-boundary state. Apply a stable quality bar / ranking.
3. **Generate / list / show** — `suggest_service.generate(root)` returns ranked proposals and persists `pending` ones; `list_proposals(root, status=...)`; `show_proposal(root, id)`.
4. **Accept / dismiss with approval gates** — `accept(root, id)`: for `pick-up`, activate the existing ready task via the `workflow_run` activation path (`_write_current_task`, backlog status); for `new-task`, create a packet via `task_service.create_packet_directory` — only on explicit accept (no silent create). `dismiss(root, id)` sets status.
5. **Expiry + prune** — proposals expire per spec; `--prune` moves expired/dismissed proposals out of the working dir (reuse `archive_service.prune_archived_proposals` / `move_working_proposals_to_archive`).
6. **CLI** — `src/grain/cli/suggest.py`: `grain suggest` (generate + list), `grain suggest show <id>`, `grain suggest accept <id>`, `grain suggest dismiss <id>`, `grain suggest --prune`; `--format json` on all. Register in `cli/__init__.py` (import + `add_command`).

## Acceptance Criteria
- `grain suggest` writes `pending` `SUG-*` proposal files to `docs/working/proposals/` and prints a ranked list.
- `grain suggest accept <id>` for `pick-up` activates the existing ready task; for `new-task` creates a packet — only on accept.
- `grain suggest dismiss <id>` and `grain suggest --prune` manage proposal lifecycle.
- `grain --format json suggest` returns stable structured output (proposals array).
- Engine is deterministic (same workspace state → same suggestions) and writes nothing without an explicit accept.
- No regression: full suite green.

## Tests
- `tests/test_suggest_service.py` — generate, each signal reader, ranking, accept pick-up, accept new-task, dismiss, prune, expiry.
- `tests/test_suggest_cmd.py` — CLI text + `--format json` for each subcommand.

## Constraints
- File-backed and local-first only; no network, no hidden state.
- Proposal-only: never mutate backlog/packets except on explicit `accept`.
- Services return data; CLI does all I/O. Repo-relative paths in output.

## Escalation Conditions
- Spec ambiguity on ranking or activation semantics — return to suggest_spec.md, do not improvise.
