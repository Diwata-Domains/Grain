# Task: Implement Task ID Generator

## Metadata
- **ID:** TASK-0019
- **Status:** done
- **Phase:** Phase 3 — Task Packet System
- **Backlog:** P3-T01
- **Dependencies:** none

## Objective
Implement `next_task_id(tasks_root: Path) -> str` in `domain/packets.py`. The function scans the `tasks/` directory for existing packet directories, extracts the numeric component from each `TASK-####` segment, and returns the next available ID in `TASK-####` format with zero-padding.

## Why This Task Exists
All Phase 3 packet creation depends on a stable, deterministic ID generator. `abt task create` (P3-T04) needs this function. The ID contract (`TASK-####`) is defined in `data_contracts.md` Section 13.3 and the manifest `id_format` field.

## Source Documents
- `docs/canonical/data_contracts.md` — Section 7 (packet directory naming), Section 13.3 (TASK-#### format)
- `docs/runtime/docs_manifest.yaml` — `tasks.id_format`
- `docs/canonical/architecture.md` — Section 6.3 (`domain/` responsibility: packet identity)

## Constraints
- Must live in `src/ai_build_toolkit/domain/packets.py`
- ID format is `TASK-####` (four zero-padded digits)
- Discovery scans directory names under `tasks_root` — does not read file contents
- Extracts TASK-#### from full `P<N>-T<NN>-TASK-####` names (CP-001 convention) as well as bare `TASK-####` names (Phase 1 legacy)
- If no existing packets, returns `TASK-0001`
- Does not create any directories or files
- Does not raise on empty or missing tasks directory — returns `TASK-0001`

## Files Likely to Change
- `src/ai_build_toolkit/domain/packets.py` (new)
- `tests/test_task_id.py` (new)

## Implementation Steps
1. Create `src/ai_build_toolkit/domain/packets.py`
2. Define `TASK_ID_PATTERN = re.compile(r"TASK-(\d{4})")` to match the TASK-#### segment in any directory name
3. Implement `next_task_id(tasks_root: Path) -> str`:
   - If `tasks_root` does not exist or is empty, return `"TASK-0001"`
   - Iterate subdirectory names under `tasks_root`
   - Apply `TASK_ID_PATTERN` to each name; collect matched integers
   - If no matches, return `"TASK-0001"`
   - Return `f"TASK-{max(numbers) + 1:04d}"`
4. Write tests covering: empty dir, missing dir, single existing packet, multiple packets, gap in numbering (max wins), legacy bare `TASK-####` name alongside new `P<N>-T<NN>-TASK-####` names

## Acceptance Criteria
- `next_task_id` returns `"TASK-0001"` when `tasks/` is empty or absent
- Returns the correct next ID when packets exist (e.g., max is 0018 → returns `"TASK-0019"`)
- Handles both `TASK-0001` (legacy) and `P3-T01-TASK-0019` (CP-001) directory names correctly
- Returns zero-padded four-digit string in all cases
- Does not touch the filesystem beyond reading directory names

## Tests Required
- `test_next_id_empty_dir` — tasks_root exists but is empty → `TASK-0001`
- `test_next_id_missing_dir` — tasks_root does not exist → `TASK-0001`
- `test_next_id_single_packet` — one `TASK-0005` dir → `TASK-0006`
- `test_next_id_multiple_packets` — several dirs, max is `TASK-0018` → `TASK-0019`
- `test_next_id_with_gap` — dirs are `TASK-0001`, `TASK-0003` (gap) → `TASK-0004` (max + 1)
- `test_next_id_legacy_and_new_mixed` — mix of `TASK-0001` and `P3-T01-TASK-0019` → correct next
- `test_next_id_ignores_non_packet_dirs` — directories without TASK-#### are ignored

## Documentation Updates Required
- `docs/working/current_task.md` — update after packet generation
- `docs/working/backlog.md` — P3-T01 status → `in_progress` when execution begins

## Recommended Model
- Primary: open_model
- Reason: Mechanical, narrow, low-risk. Pattern match + integer arithmetic. No design ambiguity.

## Escalation Conditions
- If `data_contracts.md` is found to define a different ID format than `TASK-####` for the canonical ID portion, stop and record the conflict
- If the `tasks/` root location is inconsistent between manifest and filesystem conventions, record the ambiguity before proceeding
