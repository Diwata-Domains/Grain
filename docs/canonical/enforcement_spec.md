# Grain Agent Enforcement Spec

**Status:** Canonical — locked in v0.4.0 planning (Phase 30, TASK-0197)

---

## 1. Purpose

This spec defines the agent enforcement model for Grain's packet-first discipline. The goal is that no agent — Claude Code, Codex, Gemini, custom tools, or a human operator — can execute work outside of an open task packet without actively fighting the tool.

Enforcement must not rely on agents choosing to follow prompt instructions. The same enforcement path must work for a human running `git commit` at the terminal.

---

## 2. Enforcement Layer Map

| Layer | Mechanism | Agent-agnostic? | Primary protection |
|-------|-----------|----------------|-------------------|
| 1 | `grain workflow next` state machine | Yes | Routes to `packet_required` instead of `task_execute` when no open packet |
| 2 | `grain workflow guard` command | Yes | Point-in-time check callable from any context |
| 3 | Git hooks (`grain hooks install`) | Yes | Pre-commit blocks implementation commits without open packet |
| 4 | `prompts/workflow.resume.md` | Agent-assisted | Session resume protocol; degradable |
| 5 | PROJECT_RULES.md hard rules | Agent-assisted | Hard constraint statement for agents that read it |
| 6 | AGENTS.md block | Agent-assisted (Claude-biased) | References `workflow.resume.md`; agent-readable |

Layers 1, 2, and 3 are primary enforcement — they work with zero AI involvement. Layers 4, 5, and 6 are supplementary — they guide agents toward correct behavior but are not the primary gate.

---

## 3. Layer 1 — Hardened Workflow State Machine

### 3.1 New stop reason: `packet_required`

Current behavior: `grain workflow next` routes to `task_execute` even when `current_task.md` is unset, which allows an agent to skip packet creation and proceed directly to implementation.

New behavior: if `current_task.md` is `unset` or `none` AND there are `ready` tasks in the active phase, `grain workflow next` routes to `packet_required`:

```json
{
  "stop_reason": "packet_required",
  "message": "No in-progress task packet. Create one before executing.",
  "ready_tasks": ["TASK-0197", "TASK-0198", "TASK-0199"],
  "commands": {
    "create_packet": "grain task create --id TASK-0197",
    "suggest": "grain suggest"
  }
}
```

The agent receives this output and must create a packet before proceeding. There is no path to `task_execute` from `packet_required` without opening a packet.

### 3.2 Done-task stale-pointer fix

Current behavior: if `current_task.md` points to a task with status `done`, `grain workflow next` incorrectly routes to `task_execute`. This is a known bug causing agents to re-execute completed tasks.

New behavior: if `current_task.md` points to a `done` task, route to `phase_boundary` (all tasks in this phase may be done) or `packet_required` (if other ready tasks exist), never `task_execute`.

### 3.3 `task_execute` route always includes packet reference

When routing to `task_execute`, the JSON output must always include:

```json
{
  "stop_reason": "task_execute",
  "task_id": "TASK-0197",
  "packet_path": "tasks/P30-T08-TASK-0197/",
  "task_title": "Spec agent enforcement model"
}
```

This ensures the agent holds the packet reference before acting, not after.

### 3.4 Warning: `no_execution_artifacts`

If `current_task.md` points to an `in_progress` task whose packet has no `results.md` or only a stub `results.md` (all template placeholders, no filled content), route to `task_execute` but include:

```json
{
  "stop_reason": "task_execute",
  "warnings": ["no_execution_artifacts"],
  "warning_messages": {
    "no_execution_artifacts": "Task is in_progress but results.md is empty or stub-only. Write execution results before closing."
  }
}
```

---

## 4. Layer 2 — `grain workflow guard`

A standalone, callable guard for any agent or human operator.

### 4.1 Checks performed

| Check ID | Description |
|----------|-------------|
| `packet_open` | Does an in_progress packet exist matching `current_task.md`? |
| `results_not_stub` | Does the in_progress packet have a non-stub results.md (for tasks past first commit)? |
| `phase_alignment` | Does `current_task.md` match the phase in `current_focus.md`? |
| `implementation_ahead_of_packet` | Are there committed implementation files outside `docs/` and `tasks/` that postdate the packet's last `in_progress` status update but predate any results.md write? |
| `dev_alignment` (optional) | Is the installed Grain version behind the source? (calls `grain doctor` when `--check-dev-alignment` is passed) |
| `docs_health` (optional) | Runs `grain docs audit --severity high` and includes findings (when `--check-docs` is passed) |

### 4.2 Command interface

```
grain workflow guard
grain workflow guard --strict          # treat warnings as violations
grain workflow guard --check-docs      # include docs audit findings
grain workflow guard --check-external  # check external workspace dependencies
grain --format json workflow guard
```

Output (ok state):
```
grain workflow guard

  ✓ packet_open         TASK-0197 is in_progress
  ✓ results_not_stub    results.md has content
  ✓ phase_alignment     current task matches current phase
  ✓ implementation_ahead_of_packet  no implementation files ahead of packet

Guard: OK
```

Output (violation state):
```
grain workflow guard

  ✗ packet_open         current_task.md is unset; no in_progress packet
    → grain task create --id TASK-0197

  ⚠ results_not_stub    results.md is stub-only
    → write execution results before closing

Guard: 1 violation, 1 warning
```

JSON output:
```json
{
  "status": "violation",
  "checks": [
    { "id": "packet_open", "result": "fail", "severity": "error", "message": "...", "remediation": "grain task create" },
    { "id": "results_not_stub", "result": "warn", "severity": "warning", "message": "...", "remediation": "..." }
  ]
}
```

---

## 5. Layer 3 — Git Hooks (`grain hooks install`)

### 5.1 `grain hooks install`

Writes two hooks to `.git/hooks/`:

```
grain hooks install
grain hooks uninstall
grain hooks status
```

`grain hooks status` shows whether hooks are installed and whether they are current (matches the version Grain would write now).

### 5.2 Pre-commit hook

```sh
#!/bin/sh
# Written by grain hooks install. Do not edit manually.

# Allow GRAIN_SKIP_GUARD=1 as an emergency escape hatch
if [ "$GRAIN_SKIP_GUARD" = "1" ]; then
  echo "[grain] GRAIN_SKIP_GUARD=1: skipping workflow guard. This bypass is logged." >&2
  grain notes add --type workflow_friction --command "git commit" \
    --observation "GRAIN_SKIP_GUARD=1 used to bypass pre-commit guard" --severity medium
  exit 0
fi

# Skip for metadata-only commits (docs/working/ and tasks/ only)
CHANGED_FILES=$(git diff --cached --name-only)
NON_META=$(echo "$CHANGED_FILES" | grep -v '^docs/working/' | grep -v '^tasks/')
if [ -z "$NON_META" ]; then
  exit 0
fi

# Run the guard
RESULT=$(grain workflow guard --strict --format json 2>/dev/null)
STATUS=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

if [ "$STATUS" = "violation" ]; then
  echo "" >&2
  echo "✗ grain workflow guard: commit blocked" >&2
  grain workflow guard --strict >&2
  echo "" >&2
  echo "Fix the violations above, then commit again." >&2
  echo "Emergency bypass: GRAIN_SKIP_GUARD=1 git commit (logs to tooling_notes)" >&2
  exit 1
fi

exit 0
```

### 5.3 Post-checkout hook

```sh
#!/bin/sh
# Written by grain hooks install. Do not edit manually.

# Write current workflow state to .grain/last_workflow_state.json
# Agents can read this at session start instead of calling grain workflow next
grain --format json workflow next > .grain/last_workflow_state.json 2>/dev/null

# Warn if current_task.md points to a done task
TASK_STATUS=$(grain --format json workflow guard 2>/dev/null | \
  python3 -c "import sys, json; data = json.load(sys.stdin); [print(c['message']) for c in data.get('checks', []) if c['id'] == 'packet_open' and c['result'] == 'fail']" 2>/dev/null)

if [ -n "$TASK_STATUS" ]; then
  echo "[grain] ⚠ $TASK_STATUS" >&2
fi
```

The post-checkout hook writes `.grain/last_workflow_state.json` — agents that read this at session start get the workflow state without re-running `grain workflow next`.

---

## 6. Layer 4 — `prompts/workflow.resume.md`

Grain seeds `prompts/workflow.resume.md` in every workspace via `grain init`. This file defines the session resume protocol any agent should follow. It is not AGENTS.md — it is a Grain-owned file that agents load as context.

### Content requirements

The file must:
1. Instruct the agent to run `grain --format json workflow next` as the first action before reading user messages or touching files
2. Instruct the agent to read `current_task.md` and verify the packet is open and in_progress
3. Define what to do if the packet is missing: run `grain task create` (or `grain task create --simple`), set status in_progress, then proceed
4. Reference `.grain/last_workflow_state.json` as a faster alternative to calling `grain workflow next` when it exists
5. Be written in plain language with no assumption of which AI system is reading it — no "you are Claude", no tool-specific syntax
6. Define what degraded behavior looks like: if `grain workflow next` fails for any reason, fall back to reading `current_task.md` directly

AGENTS.md and CLAUDE.md in every Grain-scaffolded workspace should reference this file by path rather than duplicating its content:
```
See prompts/workflow.resume.md for the session start protocol.
```

---

## 7. Layer 5 — PROJECT_RULES.md Hard Rules

Two additions to the bundled `PROJECT_RULES.md` template:

### Hard rule section

```markdown
## Hard Rules — These Are Not Suggestions

1. No implementation files may be created or modified outside of an open task packet.
   "Open" means: a packet directory exists under `tasks/`, `current_task.md` points to it,
   and the packet's task.md has status `in_progress`.

2. The session start checklist must run before any other action:
   (a) Run: grain --format json workflow next
   (b) Verify: current_task.md points to an in_progress packet
   (c) If no open packet: run grain task create before proceeding

3. No commit may contain implementation files without an open packet at commit time.
   The pre-commit hook enforces this. GRAIN_SKIP_GUARD=1 is an emergency bypass that
   logs to tooling_notes and must be justified.
```

These rules are written without agent-specific keywords — they read as plain numbered steps callable from `grain prompt show --context resume`.

---

## 8. Layer 6 — AGENTS.md Block

The Grain-written block in AGENTS.md must be updated to:

1. Open with a hard constraint statement in the block header — not buried in a sub-section:
```markdown
## Grain Workflow — HARD CONSTRAINT

You MUST NOT create or modify implementation files without an open task packet.
See the session start protocol at: prompts/workflow.resume.md
```

2. Reference `workflow.resume.md` by path for the session start protocol — do not duplicate the content
3. Remain useful even if the host AI doesn't specifically understand AGENTS.md conventions — it reads coherently as plain instructions

---

## 9. Escape Hatches and Logging

| Escape | Trigger | Logged |
|--------|---------|--------|
| `GRAIN_SKIP_GUARD=1` | Pre-commit bypass | Yes — `grain notes add` writes to tooling_notes automatically |
| `--force` on `grain task create` | Create packet for non-ready task | Yes — packet metadata includes `force: true` |
| `GRAIN_WORKSPACE=<path>` | Override workspace resolution | No — not a bypass, a routing choice |

Silent bypass is never acceptable. Every escape hatch must produce a traceable artifact.
