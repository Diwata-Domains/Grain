# Task: Spec working document consistency auditing — `grain docs audit`

## Metadata
- **ID:** TASK-0199
- **Status:** done
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T10
- **Packet Path:** tasks/P30-T10-TASK-0199/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Design a dedicated audit command that checks the consistency of all Grain working documents — not just the active task packet — and reports drift, staleness, and structural violations. This is the counterpart to `grain workflow guard` (which focuses on packet-state enforcement): `grain docs audit` focuses on the health of the entire working doc layer.

## Why This Task Exists
`grain workflow reconcile` (Phase 15) checks packet/state drift: does `current_task.md` match the packet, is the backlog consistent with packet statuses, etc. But it doesn't check:
- Is `current_focus.md` pointing to a phase that closed months ago?
- Are there working docs that haven't been touched since before the last phase closed, suggesting they're stale?
- Is `open_questions.md` accumulating unresolved questions that are silently blocking design decisions?
- Is `tooling_notes.md` full of `open` entries that were never escalated?
- Does `backlog.md` have tasks that are `in_progress` but have no corresponding open packet?

These are soft consistency failures — they don't crash Grain, but they cause agent sessions to work from stale context and miss decisions that were never recorded.

## Scope

### The audit surface: `grain docs audit`

```
grain docs audit
grain docs audit --doc backlog
grain docs audit --doc current_focus
grain docs audit --format json
grain docs audit --severity high
```

Checks to run:

**current_task.md:**
- Does it point to a packet that exists and has status `in_progress`?
- If it points to a `done` packet, flag as `stale_pointer` (already covered by workflow guard but should appear here too)
- If it says `unset` for more than N days (configurable), warn: "no active task — is the project paused or stalled?"

**backlog.md:**
- Do all `in_progress` entries have a corresponding open task packet?
- Are there task entries in `done` that have no `results.md` in their packet?
- Is the active phase's status section consistent with the phase closure state?
- Are there phases marked `in_progress` where all tasks are `done` (phase should be closed)?

**current_focus.md:**
- Does the "Current Phase" heading reference a phase that exists in `backlog.md`?
- Was the file last modified more than 30 days before today? (staleness warning)
- Do the "Immediate Priorities" still reference tasks/phases that are not yet done?

**open_questions.md:**
- Count questions by status; warn if >3 are `blocking` or `decision_needed`
- Warn if any question has been `open` for >60 days without status change

**tooling_notes.md:**
- Count `open` entries by severity
- Warn if any `high` severity entry has been `open` for >14 days
- Warn if there are >5 `open` entries of any severity (suggests overdue triage)

**change_proposals.md:**
- Warn if any proposal has been in `proposed` status for >30 days with no `approved_by` or `rejected` outcome

**Structural checks (all docs):**
- Are all registered manifest docs present on disk?
- Do all registered docs have their required section headings?
- Are any registered docs empty (no content beyond the template headings)?

### Output format

Text mode:
```
grain docs audit — 2026-06-11

current_task.md
  ✓  points to in_progress packet TASK-0199

backlog.md
  ✗  [high] 2 in_progress tasks have no open packet (TASK-0071, TASK-0088)
  ⚠  [medium] Phase 22 marked in_progress but all 6 tasks are done — phase needs closing

open_questions.md
  ⚠  [medium] Q7 has been 'blocking' for 47 days without resolution

tooling_notes.md
  ⚠  [high] 3 high-severity entries open >14 days

Checks: 7 pass, 3 warnings, 1 error
Run 'grain docs audit --format json' for machine-readable output.
```

JSON mode returns structured findings with doc, check_id, severity, message, and remediation_hint per finding.

### Integration with `grain workflow reconcile`

`grain docs audit` is a broader surface; `grain workflow reconcile` remains the deep packet-consistency check. They should be complementary:
- `grain workflow reconcile` — focused on the active task packet and its relationship to current_task.md
- `grain docs audit` — full working doc layer health check

Running `grain workflow guard` can optionally call `grain docs audit --severity high` and include its findings in the guard output when `--check-docs` flag is passed.

### Scheduled auditing

Grain's `post-checkout` hook (from T08 enforcement spec) should optionally run `grain docs audit --severity high --format json` and write the output to `.grain/last_docs_audit.json`. This gives agents a fresh audit state at session start without re-running the audit from scratch.

## Deliverable
`docs/working/docs_audit_spec.md` — full spec covering:
- All check definitions (check ID, description, threshold, severity, remediation hint)
- Command interface and output formats
- Integration with `grain workflow guard` and `grain workflow reconcile`
- Scheduled audit model (post-checkout hook)
- Which checks are warnings vs. errors

## Constraints
- Audit must complete in <2 seconds on a typical workspace (no large file scans)
- No check may modify files — audit is read-only
- All checks must degrade gracefully if the target doc is missing (report `doc_missing` rather than crashing)
- Thresholds (days open, count limits) must be configurable in `docs_manifest.yaml` or `grain.toml`
