# Grain CLI Ergonomics Spec

**Status:** Working spec — v0.4.0 planning (Phase 30, TASK-0201)
**Implementation phase:** Phase 31 (DX Hardening)

---

## 1. Two Audiences, One Output Contract

Grain's CLI output serves two distinct audiences with different needs:

**Agent use (machine-readable):** The agent calls `grain <command> --format json` and parses structured output. It needs stable key names, consistent stop reason vocabulary, and no prose mixed into the JSON stream.

**Human terminal use (visual quality):** The operator runs `grain <command>` and needs to scan the output quickly — what's the state, what should I do next, what does that warning mean.

Both are supported without trading off against each other. They are different output modes controlled by `--format json`. Text output may be rich and styled; JSON output must be machine-stable.

---

## 2. JSON Output Contract — Commands That Must Get `--format json`

The following commands currently lack a stable `--format json` surface. All must have one by the end of Phase 31:

| Command | Priority | Notes |
|---------|----------|-------|
| `grain docs audit` | High | Returns findings array |
| `grain suggest` | High | Returns proposals array |
| `grain suggest list` | High | Returns proposals array |
| `grain archive list` | Medium | Returns archives array |
| `grain doctor` | Medium | Returns health check object |
| `grain workspace list` | Medium | Returns workspaces array |
| `grain recipe list` | Medium | Returns recipes array |
| `grain status` | High | Returns workspace state object |
| `grain notes list` | Medium | Returns tooling notes array |

### JSON stability contract

For all `--format json` outputs:
- Top-level keys do not change within a minor version
- New keys may be added without a version bump
- No key is removed without a major version bump
- The `status` (or `stop_reason`) key is always present and always a canonical string from the documented vocabulary

JSON output goes to stdout only. Progress lines, banners, and warnings go to stderr when `--format json` is active — they must not pollute the JSON stream.

---

## 3. Stop Reason Vocabulary (Canonical)

`grain workflow next` stop reasons are canonical once published. No stop reason may be renamed without a major version bump.

| Stop Reason | Meaning | Primary recommended action |
|-------------|---------|---------------------------|
| `task_execute` | Open in_progress packet; execute the task | Run the rendered prompt in agent |
| `task_review` | Execution artifacts exist; review gate reached | `grain task review` |
| `task_close` | Review passed; ready to close | `grain task close` |
| `packet_required` | No in_progress packet; ready tasks exist | `grain task create` or `grain suggest` |
| `phase_boundary` | All tasks in active phase are done | `grain phase close` |
| `phase_complete` | Phase closed; next phase has ready tasks | Advance to next phase |
| `project_complete` | All phases done; no pending work | `grain archive` or plan next phase |
| `workspace_archived` | Workspace marked `archived: true` | No workflow action available |
| `blocked` | No actionable path; human decision required | Review blockers in `open_questions.md` |
| `no_phases` | No phases defined | Set up `backlog.md` and run `grain task create` |
| `upgrade_required` | Installed version below workspace `min_version` | `grain upgrade` |

Stop reasons must appear verbatim in `--format json` output under a top-level `stop_reason` key. Text output uses the same vocabulary in prose form.

---

## 4. Text Output Style Guide

### Symbols (no emoji)

| Symbol | Meaning |
|--------|---------|
| `✓` | Pass / done / ok |
| `✗` | Fail / error / violation |
| `⚠` | Warning |
| `→` | Recommended next action |
| `+` | New / added / present when expected to be absent |
| `~` | Changed / stale |
| `·` | Informational / neutral detail |

### Structure rules

- Section headers: plain text, no colon, followed by a blank line
- Key-value pairs: left-aligned key, right-padded to column 20, then value
- Tables: consistent pipe-separated formatting with header row
- Command hints: always on a `→` line; always include the full command with all required flags
- Error messages: always end with a `→ <remediation command>` line

### Progress output

For operations taking >0.5s: print a single `Checking...` line to stderr before output begins. When `--format json` is active, progress lines go to stderr only — they never appear on stdout.

### Verbose vs. default

Default text output shows actionable information only. `--verbose` adds context, signal sources, and explanation. `--quiet` shows only the status line and recommended action.

---

## 5. `grain status` Command

A single command that shows the complete workspace state in one scan. Replaces the need to call `grain workflow next` + `grain task prepare` + `grain docs audit` separately.

```
grain status
grain status --verbose
grain status --format json
```

### Text output

```
Grain Status — 2026-06-11

Phase:     Phase 30 — v0.4.0 Planning  (in_progress)
Tasks:     14 total · 10 done · 4 ready · 0 in_progress · 0 blocked

Current:   no active task
Workflow:  packet_required — 4 ready tasks in Phase 30

Health:    ⚠ 1 high-severity audit finding
Install:   grain 0.4.0 (editable)  ✓ aligned

→ grain workflow next
```

`--verbose` appends: full audit findings, linked workspaces, recent git summary (last 3 commits), active proposals count.

### JSON output

```json
{
  "run_at": "2026-06-11T14:30:00",
  "phase": { "number": 30, "name": "v0.4.0 Planning", "status": "in_progress" },
  "tasks": { "total": 14, "done": 10, "ready": 4, "in_progress": 0, "blocked": 0 },
  "current_task": null,
  "workflow": { "stop_reason": "packet_required", "ready_tasks": ["TASK-0201", "TASK-0202", "TASK-0203", "TASK-0203"] },
  "health": { "overall": "warning", "error_count": 0, "warning_count": 1 },
  "install": { "version": "0.4.0", "mode": "editable", "aligned": true },
  "pending_proposals": 0
}
```

### Performance constraint

`grain status` must complete in <1 second. It reads cached/pre-computed state where possible:
- Reads `.grain/last_workflow_state.json` if it exists and is <5 minutes old (set by post-checkout hook)
- Reads `.grain/last_docs_audit.json` if it exists and is <10 minutes old
- Falls back to live computation if cached files are absent or stale

---

## 6. Schema Documentation in `cli_spec.md`

As part of Phase 31, `docs/canonical/cli_spec.md` must be updated with:
- A "JSON Output Schemas" section documenting the top-level keys and value types for every command that has `--format json`
- The canonical stop reason vocabulary table (identical to §3 of this spec)
- The `grain status` JSON schema

This section becomes the machine-readable contract that agent authors reference when building integrations.
