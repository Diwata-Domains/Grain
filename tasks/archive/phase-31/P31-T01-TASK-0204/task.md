# Task: Fix active DX bugs — workflow routing, packet ID reuse, phase close flag, flag order

## Metadata
- **ID:** TASK-0204
- **Status:** done
- **Phase:** Phase 31 — DX Hardening and v0.4.0 Foundation
- **Backlog:** P31-T01
- **Packet Path:** tasks/P31-T01-TASK-0204/
- **Dependencies:** none
- **Primary Adapter:** code

## Objective
Fix 3 active DX bugs logged in tooling_notes, plus correct the `--format` flag order issue surfaced during Phase 30.

## Bugs to Fix

### Bug 1 — `grain workflow next` routes to `task_execute` when review should be next
**Source:** tooling_notes 2026-04-21
**File:** `src/grain/services/workflow_service.py`
**Fix:** When active task has execution artifacts (non-stub `results.md` exists), route to `task_review` not `task_execute`. Check for `results.md` presence and non-stub content (not all placeholder lines) before routing.

### Bug 2 — Packet ID reuse after archiving
**Source:** tooling_notes 2026-04-21
**File:** `src/grain/services/task_service.py` — `next_task_id()` function
**Fix:** Scan both `tasks/` (active) AND `tasks/archive/*/` (archived) when computing the next task ID. The highest existing ID across both locations + 1 is the next safe ID.

### Bug 3 — `grain phase close --phase <N>` flag does not exist
**Source:** tooling_notes (Diwata-Infra)
**File:** `src/grain/cli/phase.py`
**Fix:** Add `--phase` / `-p` option to `grain phase close`. When provided, validate that the specified phase number matches the current active phase (or allow force-close with `--force` for non-active phases). Without the flag, behavior is unchanged (closes the current active phase).

### Bug 4 — `--format` flag order in spec docs
**Source:** tooling_notes 2026-06-11
**Files:** Multiple spec docs that reference `grain workflow next --format json` (wrong) vs `grain --format json workflow next` (correct).
**Fix:** Grep all spec docs for `grain workflow next --format json` and update to `grain --format json workflow next`. Same for all other commands that use the wrong flag order. Also add a note to `docs/canonical/cli_spec.md` about global flag placement.

## Deliverable
- Fixed `workflow_service.py` routing logic (Bug 1)
- Fixed `next_task_id()` scan (Bug 2)
- `grain phase close --phase <N>` working (Bug 3)
- All spec docs with correct `--format` flag order (Bug 4)
- Tests for all four fixes

## Constraints
- Bug 1 fix must not break the `task_execute` path for tasks that genuinely have no results yet
- Bug 2 fix must scan archive dirs without adding significant startup latency
- Bug 3 flag must validate that the specified phase is the active phase (no silent wrong-phase close)
- Bug 4 is docs-only — no behavior change
