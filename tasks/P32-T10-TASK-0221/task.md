# Task: Docs hygiene — phase_status_consistency audit check + current_focus rewrite

## Metadata
- **ID:** TASK-0221
- **Status:** ready
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T10
- **Packet Path:** tasks/P32-T10-TASK-0221/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** docs

## Objective
Fix the self-contradiction and bloat in `docs/working/current_focus.md` (it declared "Phase 31 ACTIVE" at the top while logging "Phase 31 closed" at the bottom, across ~377 lines of stale per-phase prose), and add a `phase_status_consistency` check to `grain docs audit` so this class of drift is caught automatically going forward.

## Why This Task Exists
`current_focus.md` is the operator's and every agent's entry point for "what is active now." A self-contradicting focus file silently routes work onto stale state. This is founder-requested hygiene and a precondition for clean v0.4.0 planning.

## Scope / Implementation Steps
1. Rewrite `docs/working/current_focus.md` to a single Current Phase block + a one-line-per-phase Closed-Phase Ledger (mirrors how `backlog.md` collapses closed phases); task state stays in `backlog.md`/archives. (Done in the planning commit.)
2. Add `_check_phase_status_consistency(text)` to `src/grain/services/docs_audit_service.py` and call it from `_check_current_focus` before its return. Add `_ACTIVE_RE` / `_CLOSED_LINE_RE` regexes. Reuse `AuditFinding`, `_CURRENT_FOCUS_PATH`, `_extract_current_phase`. Error severity; not auto-fixable.
3. Document the check in `docs/working/docs_audit_spec.md` (current_focus.md checks table + note in the auto-fix section that it is not auto-fixable).
4. Bump any "18 checks" narrative if present.

## Acceptance Criteria
- `grain docs audit --doc current_focus` reports `phase_status_consistency` (pass on the rewritten file).
- A phase marked both ACTIVE and closed in the file → severity `error`; a Current Phase that appears in the closed ledger → `error`.
- `--format json` finding has `check_id=phase_status_consistency`, `doc=docs/working/current_focus.md`.
- Rewritten `current_focus.md` has no phase both active and closed, and is well under 80 lines.
- No regression: full suite green.

## Tests
- `tests/test_docs_audit_cmd.py` — pass case (Phase 32 active + Phase 31 in ledger), fail case A (same phase active+closed), fail case B (Current Phase in ledger).

## Constraints
- Read-only check; the rewrite is a docs change, not auto-applied by the check.
- Same-file contradiction detection (no backlog cross-read required).

## Escalation Conditions
- Rewrite would drop information not captured in backlog/archives — preserve it before trimming.
