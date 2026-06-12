# Task: Spec the `grain suggest` command group

## Metadata
- **ID:** TASK-0196
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T07
- **Packet Path:** tasks/P30-T07-TASK-0196/
- **Dependencies:** TASK-0190, TASK-0191
- **Primary Adapter:** docs

## Objective
Write the full spec for `grain suggest` — a command that analyzes the current project state and surfaces a ranked, actionable list of what to work on next. Each suggestion is either a `pick-up` (an existing backlog task that should move to `ready` now) or a `new-task` (net-new work the backlog hasn't captured yet). Suggestions require explicit human approval before they create task packets or change task status; the coder or manager reviews and accepts or dismisses each one.

## Why This Task Exists
`grain workflow next` answers "what is the next legal workflow step given current state." It is purely mechanical — it follows the workflow state machine. What operators actually need is a layer above that: "given everything I know about this project, what *should* I be working on?" That requires analyzing signal sources that `workflow next` ignores — unresolved open questions, accumulated tooling friction, stale backlog items whose dependencies have since been met, areas of recent code churn, and gaps between what docs describe and what code implements.

This is a core v0.4.0 deliverable per the milestone contract (TASK-0190). The toolkit contract (TASK-0191) defines the boundary for how `grain suggest` can incorporate signals from sibling tools (Assay verification failures, etc.).

## Scope

### Command surface

`grain suggest`
- Analyzes project state and outputs a prioritized suggestion list
- Persists suggestions to `docs/working/proposals/suggestions_YYYYMMDD.md` (human-reviewable, audit trail)
- Prints a human-readable summary by default; `--format json` for agent consumption
- `--limit N` — return at most N suggestions (default: 10)
- `--type pick-up|new-task|all` — filter by suggestion type (default: all)

`grain suggest list`
- Show pending suggestions from the most recent run (reads the latest suggestions file)
- Same `--format json` support

`grain suggest accept <id>`
- For `pick-up` suggestions: sets the target task's status to `ready`
- For `new-task` suggestions: runs `grain task create --simple` with the suggested title and scope pre-filled
- Marks the suggestion as `accepted` in the suggestions file
- Prints the created task ID or updated task status

`grain suggest dismiss <id> [--reason "..."]`
- Marks suggestion as `dismissed` with optional reason
- Dismissed suggestions are excluded from future `grain suggest` runs (stored in a `.grain/dismissed_suggestions.json` or similar)

### Suggestion types

**`pick-up`** — An existing task in the backlog that should be prioritized now:
- Task is `draft` or `blocked` but its dependencies are now met
- Task is `ready` but has been sitting untouched while lower-priority work happened
- Task was previously dismissed but blocking circumstances have changed
- Output includes: task ID, current status, reason it should be picked up now

**`new-task`** — A proposed net-new task not in the backlog:
- Derived from an `open_questions.md` item that has been unresolved for more than N commits
- Derived from a `tooling_notes.md` item with `medium` or `high` severity and `open` status
- Derived from a detected gap: a canonical doc references a feature that has no corresponding backlog task
- Derived from recent git activity: a file area with multiple recent fix commits and no test coverage task
- Output includes: suggested title, suggested scope (1–2 sentences), signal source (what triggered the suggestion), confidence level

### Signal inputs
The suggest engine reads (in priority order):
1. `docs/working/open_questions.md` — unresolved questions as new-task candidates
2. `docs/working/tooling_notes.md` — open medium/high severity friction as new-task candidates
3. `docs/working/backlog.md` + task packet statuses — pick-up candidates with met dependencies
4. `docs/working/current_focus.md` — active phase context for relevance scoring
5. `docs/canonical/product_scope.md` — scope boundary enforcement (filter out-of-scope suggestions)
6. Git log (last 30 commits) — churn signals for new-task candidates
7. (Optional, if toolkit contract is available) Assay verification failure reports as new-task candidates

### Approval and lifecycle
- Suggestions are proposals only — `grain suggest` never creates tasks or changes status without `grain suggest accept`
- The suggestions file (`docs/working/proposals/suggestions_YYYYMMDD.md`) is the audit trail — it persists even after accept/dismiss
- Dismissed suggestion IDs are stored locally (`.grain/dismissed_suggestions.json`) and excluded from future runs
- `grain suggest accept` produces the same output as the equivalent manual `grain task create` or `grain task status` call — no hidden state

### Relationship to existing commands
- `grain workflow next` — unchanged; remains the mechanical workflow state router. `grain suggest` is the intelligence layer that runs *before* you decide what to pick up; `grain workflow next` runs *after* you've picked it up.
- `grain orchestrate plan` — remains for scope-based orchestration planning. `grain suggest` is for ongoing project-state-based suggestions, not one-off planning sprints.
- `grain recipe` — a recipe can be suggested by `grain suggest` as a new-task candidate ("run the meeting-notes recipe for the outstanding retro notes")

### Design decisions to lock in the spec
1. **Persistence format** — suggestions file in `docs/working/proposals/` (human-readable, fits file-backed philosophy) vs. in-memory only (simpler, no audit trail). Recommendation: file-backed, one file per day with a stable suggestion ID scheme (`SUG-YYYYMMDD-NNN`).
2. **Dismissed suggestion storage** — `.grain/` local state dir vs. a `docs/working/dismissed_suggestions.md`. Recommendation: `.grain/dismissed_suggestions.json` (local, not committed; dismissals are personal preference).
3. **Confidence scoring** — binary (suggest or not) vs. continuous score. Recommendation: three tiers (`high` / `medium` / `speculative`) with a `--min-confidence` filter flag.
4. **Frequency** — should `grain suggest` run automatically at workflow boundaries, or always be explicitly invoked? Recommendation: explicit only in v0.4.0; auto-surface as a TUI panel post-v0.4.0.

## Deliverable
`docs/canonical/suggest_spec.md` — full spec for the `grain suggest` command group, covering command surface, suggestion types, signal inputs, approval lifecycle, persistence model, and the four design decisions above resolved.

## Constraints
- `grain suggest` must never create tasks or change task status without explicit `grain suggest accept` — the human gate is mandatory
- Signal inputs are read-only — the suggest engine must not modify any project files during analysis
- `--format json` output must be stable and machine-readable — it is the primary interface for agent-driven suggestion review
- Local-first: no network calls during suggestion generation (Assay signal is file-based, not a live API call)
- The command must degrade gracefully when signal files are missing — fewer suggestions, not an error
