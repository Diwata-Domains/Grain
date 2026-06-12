# Grain Suggest Spec

**Status:** Canonical — locked in v0.4.0 planning (Phase 30, TASK-0196)

---

## 1. Purpose

`grain suggest` proactively surfaces what to work on next. It reads the current workspace state, infers suggestions from defined signal inputs, and writes them as file-backed proposals for operator review. Nothing is acted on automatically — every suggestion requires explicit `grain suggest accept` or `grain suggest dismiss`.

This is not a replacement for `grain workflow next`. `grain workflow next` is the routing authority for the current open task. `grain suggest` is advisory: it answers "what should I open next?" when the operator is deciding what to prioritize.

---

## 2. Suggestion Types

### `pick-up`
Suggests an existing task in the backlog that is `ready` and meets the quality bar for surfacing. No new task is created. Accepting a pick-up suggestion sets the task's status to `in_progress` and opens it as the current packet.

Example prompt: "TASK-0197 (P30-T08) is ready and is in the active phase. Start it?"

### `new-task`
Suggests creating a net-new task not currently in the backlog. Grain derives the suggestion from workspace signals (open questions, tooling notes, git patterns) and provides a proposed objective + rationale. Accepting a new-task suggestion runs `grain task create` with the suggested objective pre-filled; the operator reviews and confirms before the packet is written.

Example prompt: "3 high-severity tooling_notes entries have been open >14 days with no linked backlog task. Create a DX triage task for Phase 31?"

---

## 3. Input Signals

Grain reads these signals to generate suggestions, in priority order:

| Priority | Signal | Source | Use |
|----------|--------|--------|-----|
| 1 | Ready tasks in active phase | `backlog.md` | Pick-up suggestions |
| 2 | Blocking open questions | `open_questions.md` (status: `blocking` or `decision_needed`) | New-task suggestions — unresolved OQ driving a new decision task |
| 3 | High-severity tooling notes | `tooling_notes.md` (severity: `high`, status: `open`) | New-task suggestions — friction with no linked backlog item |
| 4 | Recent git history | Last 3 commits (subject lines + files touched) | Infer what was just completed; avoid suggesting work already done |
| 5 | Active phase boundary | `current_focus.md` + backlog phase status | Suggest phase-close action when all tasks in active phase are done |

Signals are read locally — no network call, no LLM inference. Suggestion generation is deterministic from these inputs.

---

## 4. Suggestion Quality Bar

Suggestions that don't meet these criteria are filtered before reaching the operator:

**Pick-up type:**
- Task must be `ready` status
- Task must be in the active phase or the immediately next blocked phase
- Task must not be the currently `in_progress` task
- Task must not have been touched (via commit) in the last 3 commits

**New-task type:**
- Must cite a specific, traceable input signal (OQ ID, tooling_notes row date+command, or commit SHA)
- Must state a concrete objective naming a specific deliverable (not "improve X" — must be "write spec for X" or "fix Y in Z command")
- Must not duplicate an existing task title at ≥70% token similarity (simple token overlap check — no embeddings)

Any suggestion that cannot satisfy both criteria is silently filtered. The signal reference appears in the proposal file.

---

## 5. Command Interface

### `grain suggest`

Runs the full suggestion cycle: reads signals, generates suggestions, presents them for review.

```
grain suggest
grain suggest --type pick-up
grain suggest --type new-task
grain suggest --limit 3
grain suggest --format json
```

Output (text mode):
```
grain suggest — 2026-06-11

SUGGESTION SUG-20260611-001
  Type:     pick-up
  Task:     TASK-0197 (P30-T08) — Spec agent enforcement model
  Status:   ready
  Phase:    Phase 30 (active)
  Signal:   Ready task in active phase
  → grain suggest accept SUG-20260611-001
  → grain suggest dismiss SUG-20260611-001

SUGGESTION SUG-20260611-002
  Type:     new-task
  Objective: Create DX triage task for 3 high-severity tooling_notes open >14 days
  Signal:   tooling_notes 2026-04-21 (grain workflow next, grain workflow run)
  Rationale: No backlog task tracks these friction items; Phase 31 is the right phase
  → grain suggest accept SUG-20260611-002
  → grain suggest dismiss SUG-20260611-002

2 suggestions. Run 'grain suggest list' to see all active proposals.
```

`--format json` returns structured output for agent consumption.

### `grain suggest accept <id>`

Accepts a suggestion:
- For `pick-up`: sets the target task's status to `in_progress` in `backlog.md`, updates `current_task.md`, creates the packet if it doesn't exist
- For `new-task`: pre-fills `grain task create` with the suggested objective and signal reference; does NOT silently create the task — opens an interactive confirm step first (or `--no-confirm` for agent use)

### `grain suggest dismiss <id>`

Dismisses a suggestion. The proposal file is updated with `status: dismissed`. The dismissed suggestion is not surfaced again for the same signal (same OQ ID, same tooling_notes row) unless the signal changes materially.

### `grain suggest list`

Lists all active proposals (status: `pending` or `accepted_pending_confirm`). `--status dismissed` shows dismissed ones. `--format json` for machine use.

### `grain suggest show <id>`

Shows full proposal detail: suggestion text, source signals, proposed task objective (for new-task), timestamp, status.

---

## 6. Proposal Persistence

Each suggestion is written as a file in `docs/working/proposals/` when it is generated:

```
docs/working/proposals/
  SUG-20260611-001.md
  SUG-20260611-002.md
```

### Proposal file format

```markdown
# Suggestion SUG-20260611-001

**Type:** pick-up
**Status:** pending
**Generated:** 2026-06-11
**Signal:** Ready task in active phase

## Suggested Action
Open TASK-0197 (P30-T08 — Spec agent enforcement model) as the current task.
Task is `ready` in Phase 30 (active phase).

## Source Signals
- backlog.md: P30-T08 status = ready, phase = Phase 30 (active)

## Accept Command
grain suggest accept SUG-20260611-001

## Dismiss Command
grain suggest dismiss SUG-20260611-001
```

Proposal files are committed to version control — they are part of the planning record.

### Proposal ID format

`SUG-YYYYMMDD-NNN` — date of generation + 3-digit sequence number within that day. IDs are globally unique within a workspace.

### Proposal lifecycle

```
pending → accepted  → (task opened or task create initiated)
       → dismissed  → (not surfaced again for same signal)
       → expired    → (set automatically when the underlying signal changes: task becomes done, OQ is resolved, etc.)
```

Proposals are not deleted after acceptance or dismissal — they remain as historical records.

---

## 7. Relationship to `grain workflow next`

`grain workflow next` routes the current in-progress task: execute → review → close. It does not select which task to open.

`grain suggest` answers the question before `grain workflow next` is relevant: "which task should I open?"

The typical sequence:
```
grain suggest                     → surfaces ready tasks and new-task proposals
grain suggest accept SUG-...      → opens the selected task
grain workflow next                → now routes to task_execute for the opened task
```

`grain suggest` does not override `grain workflow next`. If a task is already `in_progress`, `grain suggest` surfaces it as a reminder rather than proposing something else.

---

## 8. Design Decisions

### D1: Why not embed suggestions into `grain workflow next`?

`grain workflow next` is a deterministic state machine routing authority. Embedding suggestion logic would make it non-deterministic and harder to test. Keeping them separate preserves `grain workflow next` as a reliable gate and makes `grain suggest` independently testable.

### D2: Why file-backed proposals instead of in-memory output?

Agents need to reference proposals across invocations — a session that generates a suggestion, then loses context, can pick up `SUG-20260611-001.md` on resume. File-backed proposals are inspectable, committable, and don't require re-running the signal analysis.

### D3: Why no LLM inference in the suggestion engine?

All signal reads and quality-bar checks are deterministic string/structure operations. LLM inference would add: latency, non-determinism, dependency on an agent being present. `grain suggest` must work from the terminal without an agent running. The LLM's role is to read the rendered proposal and decide whether to accept or dismiss — not to generate the suggestion.

### D4: `new-task` accept always prompts — no silent task creation

Even with `--no-confirm`, `grain suggest accept` for a `new-task` suggestion outputs the proposed task.md content and asks the operator to confirm before writing. This is intentional: new-task suggestions propose something not in the backlog, which means the operator hasn't reviewed the scope. Silent task creation is a workflow violation (T08 enforcement spec).

---

## 9. Integration with `grain docs audit`

`grain docs audit` (T10 spec) surfaces aging open questions and un-triaged tooling notes as audit findings. `grain suggest` reads those same signals and converts them into actionable proposals. The two commands are complementary:

- `grain docs audit` says "these things look unhealthy"
- `grain suggest` says "here's a concrete task you could open to address them"

`grain suggest --from-audit` is a planned v0.4.0 convenience: runs `grain docs audit --format json`, filters its findings, and generates new-task suggestions from high-severity findings that have no linked backlog task.
