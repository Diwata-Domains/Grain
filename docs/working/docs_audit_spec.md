# Grain Docs Audit Spec

**Status:** Working spec — v0.4.0 planning (Phase 30, TASK-0199)
**Implementation phase:** Phase 31 (DX Hardening)

---

## 1. Purpose

`grain docs audit` is a broad working document health check. It complements `grain workflow reconcile` (packet-state focused) by scanning the entire working document layer for drift, staleness, and structural violations.

`grain docs audit` is read-only. It never modifies files. All checks must complete in <2 seconds.

---

## 2. Check Definitions

### current_task.md checks

| Check ID | Description | Severity | Fail condition |
|----------|-------------|----------|----------------|
| `current_task_stale_pointer` | `current_task.md` points to a task with status `done` | error | Task status in packet is `done` |
| `current_task_missing_packet` | `current_task.md` references a packet directory that doesn't exist | error | Packet directory absent |
| `current_task_idle` | No active task for >N days | warning | `current_task.md` says `unset` and last commit >N days ago (default N=14) |

### backlog.md checks

| Check ID | Description | Severity | Fail condition |
|----------|-------------|----------|----------------|
| `backlog_inprogress_no_packet` | A backlog entry is `in_progress` but has no open packet | error | `in_progress` in backlog, no matching packet with `in_progress` status |
| `backlog_done_no_results` | A `done` task has no `results.md` in its packet | warning | `done` status in backlog, packet exists, no `results.md` |
| `backlog_phase_status_drift` | A phase is marked `in_progress` but all its tasks are `done` | warning | All tasks in phase are `done`; phase not closed |
| `backlog_phase_closed_with_open_tasks` | A phase is marked `CLOSED` but has tasks not in `done` | error | Phase has `CLOSED` label but non-done tasks |

### current_focus.md checks

| Check ID | Description | Severity | Fail condition |
|----------|-------------|----------|----------------|
| `current_focus_phase_mismatch` | "Current Phase" heading doesn't match any phase in `backlog.md` | warning | Phase name not found in backlog |
| `current_focus_stale` | File last modified more than N days ago (default N=30) | warning | mtime > N days |
| `current_focus_priorities_done` | "Immediate Priorities" list items reference tasks/phases that are all done | warning | All referenced tasks have `done` status |
| `phase_status_consistency` | A phase is described as both active and closed, or the "Current Phase" value appears in the closed-phase ledger | error | A phase number is marked both active and closed in the file, OR the Current Phase value appears as a closed-phase ledger row |

### open_questions.md checks

| Check ID | Description | Severity | Fail condition |
|----------|-------------|----------|----------------|
| `oq_blocking_accumulation` | More than N `blocking` or `decision_needed` questions (default N=3) | warning | Count > N |
| `oq_stale_open` | A question has been `open` for >N days without status change (default N=60) | warning | Age > N days |

### tooling_notes.md checks

| Check ID | Description | Severity | Fail condition |
|----------|-------------|----------|----------------|
| `tooling_notes_high_severity_aging` | A `high`-severity entry has been `open` for >N days (default N=14) | warning | Age > N days |
| `tooling_notes_overdue_triage` | More than N `open` entries of any severity (default N=5) | warning | Count > N |

### change_proposals.md checks

| Check ID | Description | Severity | Fail condition |
|----------|-------------|----------|----------------|
| `proposal_aging` | A proposal has been in `proposed` status for >N days with no outcome (default N=30) | warning | Age > N days |

### Structural checks (all registered docs)

| Check ID | Description | Severity | Fail condition |
|----------|-------------|----------|----------------|
| `registered_doc_missing` | A doc registered in `docs_manifest.yaml` is absent from disk | error | File not found |
| `registered_doc_empty` | A registered doc has no content beyond the template headings | warning | File contains only heading lines (lines starting with `#`) |
| `required_section_missing` | A doc is missing a required section heading (if declared in manifest) | warning | Required heading absent |

---

## 3. Command Interface

```
grain docs audit
grain docs audit --doc current_task       Run only current_task.md checks
grain docs audit --doc backlog            Run only backlog.md checks
grain docs audit --severity high          Show only error-level findings
grain docs audit --severity medium        Show warnings and errors
grain docs audit --format json
grain docs audit --fix                    Run auto-fixable remediation (dry run by default with --dry-run)
```

### Text output

```
grain docs audit — 2026-06-11

current_task.md
  ✓  current_task_stale_pointer     no stale pointer
  ✓  current_task_missing_packet    packet TASK-0199 exists

backlog.md
  ✗  backlog_inprogress_no_packet   TASK-0071 is in_progress in backlog but has no open packet
     → grain task create --id TASK-0071
  ⚠  backlog_phase_status_drift     Phase 22 in_progress but all 6 tasks are done
     → grain phase close (when ready)

open_questions.md
  ⚠  oq_stale_open                  Q7 has been 'blocking' for 47 days

tooling_notes.md
  ⚠  tooling_notes_high_severity_aging  2 high-severity entries open >14 days
     → grain report (to file upstream issues)

Structural
  ✓  registered_doc_missing         all 14 registered docs present
  ⚠  registered_doc_empty           docs/canonical/decisions.md has no content beyond headings

Checks: 8 pass, 4 warnings, 1 error
Run 'grain docs audit --format json' for machine-readable output.
```

### JSON output

```json
{
  "run_at": "2026-06-11T14:30:00",
  "summary": { "pass": 8, "warning": 4, "error": 1 },
  "overall": "error",
  "findings": [
    {
      "doc": "backlog.md",
      "check_id": "backlog_inprogress_no_packet",
      "severity": "error",
      "message": "TASK-0071 is in_progress in backlog but has no open packet",
      "remediation": "grain task create --id TASK-0071"
    }
  ]
}
```

---

## 4. Threshold Configuration

All day/count thresholds are configurable in `docs_manifest.yaml` under an `audit_thresholds` block:

```yaml
audit_thresholds:
  current_task_idle_days: 14
  current_focus_stale_days: 30
  oq_blocking_max: 3
  oq_stale_open_days: 60
  tooling_notes_high_severity_aging_days: 14
  tooling_notes_overdue_triage_max: 5
  proposal_aging_days: 30
```

If the block is absent, defaults apply. Thresholds can be set to `0` to disable a specific check.

---

## 5. Integration Points

### `grain workflow guard --check-docs`

When `--check-docs` is passed to `grain workflow guard`, it runs `grain docs audit --severity high --format json` internally and includes error-severity findings in the guard output as additional violations. Warning-level findings are included as guard warnings.

This allows the pre-commit hook to optionally surface critical doc health issues before a commit:
```sh
grain workflow guard --strict --check-docs --format json
```

### Post-checkout hook

The post-checkout hook (from T08 enforcement spec) optionally runs `grain docs audit --severity high --format json` and writes the result to `.grain/last_docs_audit.json`. Agents can read this at session start for a pre-computed audit state.

### `grain suggest --from-audit`

`grain suggest` reads `grain docs audit --format json` when `--from-audit` is passed and generates new-task suggestions for error/warning findings that have no linked backlog task.

---

## 6. Auto-Fixable Checks

Some checks are safely auto-fixable by `grain docs audit --fix`:

| Check ID | Auto-fix action |
|----------|----------------|
| `backlog_phase_status_drift` | Does not auto-close — suggests `grain phase close` |
| `current_task_stale_pointer` | Clears `current_task.md` to `unset` (after prompt) |
| `registered_doc_missing` | Does not auto-create — suggests `grain upgrade --add-missing` |

No check silently modifies files without `--fix`. With `--fix`, Grain prompts per finding before applying. `--fix --no-confirm` applies all safe fixes without prompting — intended for agent use only.

`phase_status_consistency` is **not** auto-fixable: resolving an active/closed contradiction requires a human (or agent) to author the correct active phase and the correct closed-phase ledger, so the check only reports the drift.
