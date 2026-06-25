# Task: Extend grain phase close to auto-archive task packets

## Metadata
- **ID:** TASK-0214
- **Status:** ready
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T03
- **Packet Path:** tasks/P32-T03-TASK-0214/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
When a phase is closed, automatically move its task packet directories (`tasks/P{N}-*`) into `tasks/archive/phase-{N}/`, alongside the doc snapshot that `grain phase close` already produces. Add a `--keep-tasks` flag to skip the move when a packet is carried forward.

## Why This Task Exists
v0.3.1 archives phase *docs* on close but leaves task packets in the active `tasks/` directory, which accumulates and clutters `grain task list`. Sealing a phase should fully retire its packets.

## Scope / Implementation Steps
1. Add `move_phase_packets(root, phase, *, keep_tasks=False, dry_run=False)` to `src/grain/services/archive_service.py`: detect `tasks/P{N}-*` dirs, create `tasks/archive/phase-{N}/`, move packets, return a structured result (moved list, errors).
2. Update `docs/archive/phases/phase-{N}/metadata.json` with `tasks_done` (count) and `tasks_archive` (path).
3. Wire into `src/grain/services/phase_service.py` close flow so packet archiving runs after the doc snapshot.
4. Add `--keep-tasks` to `grain phase close` in `src/grain/cli/phase.py`; surface moved-packet summary in text + `--format json`.

## Acceptance Criteria
- `grain phase close` moves all `tasks/P{N}-*` packets to `tasks/archive/phase-{N}/` and records `tasks_done`/`tasks_archive` in metadata.
- `--keep-tasks` leaves packets in place.
- Operation is idempotent and degrades gracefully when no packets match.
- No regression: full suite green.

## Tests
- `tests/test_phase_close_archives_packets.py` — packets moved, metadata updated, `--keep-tasks` skips, no-match graceful, idempotent.

## Constraints
- Move (not copy) packets; active `tasks/` stays clean.
- Never lose a packet — fail loudly on partial moves.

## Escalation Conditions
- A packet matches the phase prefix but is referenced as the current task — stop and surface rather than archiving an active packet.
