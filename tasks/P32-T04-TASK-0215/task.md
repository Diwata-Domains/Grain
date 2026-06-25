# Task: Extend grain archive show to surface task packet list

## Metadata
- **ID:** TASK-0215
- **Status:** ready
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T04
- **Packet Path:** tasks/P32-T04-TASK-0215/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Extend `grain archive show --phase N` to also list the task packets archived under `tasks/archive/phase-{N}/` (from the `tasks_archive` field in `metadata.json`), showing each packet's task ID and title. Degrade gracefully for phases closed before v0.4.0 (no task archive).

## Why This Task Exists
Pairs with P32-T03: once packets are archived on phase close, the archive viewer should surface them so a closed phase is fully inspectable from one command.

## Scope / Implementation Steps
1. Extend `show_archive` in `src/grain/services/archive_service.py` to read `tasks_archive` from metadata and enumerate packet dirs, parsing `task.md` for ID + title.
2. Update `src/grain/cli/archive.py` `archive show` output: phase metadata, doc snapshot files, packet list (ID + title); `--format json` includes a `packets` array.
3. When no task archive exists for the phase, surface a metadata note instead of erroring.

## Acceptance Criteria
- `grain archive show --phase N` lists archived packets with ID + title.
- `grain --format json archive show --phase N` includes a `packets` array.
- Pre-v0.4.0 phases (no task archive) show a graceful note, no crash.
- No regression: full suite green.

## Tests
- `tests/test_archive_show_packets.py` — packet list rendered, JSON shape, graceful no-archive case.

## Constraints
- Read-only; never mutates the archive.
- Repo-relative paths in output.

## Escalation Conditions
- metadata.json missing or malformed — surface a clear error, do not crash.
