# Task: Spec agent enforcement model — packet-first discipline and session resume protocol

## Metadata
- **ID:** TASK-0197
- **Status:** done
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T08
- **Packet Path:** tasks/P30-T08-TASK-0197/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Design a system that enforces packet-first discipline on any agent driving a Grain workflow — not just Claude Code, but GPT-4, Gemini, Codex, custom agents, or any tool that can invoke a CLI and read files. The enforcement must not rely on the agent choosing to follow prompt instructions; it must be enforced through Grain's own CLI gates, state machine, and hooks so that an agent *cannot* execute work without a packet without actively fighting the tool.

## Why This Task Exists
Across 4 active workspaces, the same failure mode appears repeatedly: agents skip `grain task create` and write implementation files directly. The root causes are consistent:

1. **Prompts degrade under session pressure.** AGENTS.md and PROJECT_RULES say "use packets" but an agent under task pressure treats them as suggestions, not constraints.
2. **Session resume is unsafe.** When a context window resets, an agent restarts cold. There is no resume protocol that forces the agent back into Grain state before acting. The agent reads the last user message and starts executing, skipping all workflow setup.
3. **No hard gate.** Nothing currently prevents a commit without an open in_progress packet. The workflow rules are enforced by convention, not by the tool.
4. **The enforcement is agent-specific.** AGENTS.md has Claude-specific syntax; other agents (GPT, Codex, Gemini) don't read it. Any enforcement that lives only in AGENTS.md is invisible to half the agents that might use Grain.

The fix must be **agent-agnostic**: enforced through the CLI's own state machine, file-backed state, and git hooks — not through agent-specific config files.

## Scope

### Part 1 — Harden the workflow state machine as the primary enforcement layer

The core principle: **`grain workflow next` is the single routing authority**. Any agent that uses Grain correctly calls `grain workflow next` before acting. If the state machine refuses to route to `task_execute` without a valid in_progress packet, no agent can bypass it regardless of which AI is driving.

Design changes to `grain workflow next`:
- If `current_task.md` is `unset` or `none` AND there are `ready` tasks in the active phase, route to a new stop reason: `packet_required` — do not route to `task_execute`. Output includes the list of ready task IDs and the exact commands to run.
- If `current_task.md` points to a task with status `done`, route to `phase_boundary` — not `task_execute`. (Currently routes to `task_execute` — this is a known bug in the Assay workspace.)
- If `current_task.md` points to a task with status `in_progress` but the packet has no results.md or only a stub results.md (all template placeholders), allow routing to `task_execute` but include a `warning: no_execution_artifacts` in the output — the agent is reminded to write results.

Design changes to the `task_execute` route output:
- Always include the packet path and the task ID in the JSON output at `task_execute` routing — so the agent is holding the packet reference before it starts, not after.

### Part 2 — `grain workflow guard` command

A standalone guard command that any agent or human can run at any point:

`grain workflow guard`
- Checks: does an in_progress packet exist that matches `current_task.md`?
- Checks: does that packet have a non-stub results.md (for in_progress tasks that have been executing for > 0 commits)?
- Checks: does `current_task.md` match the phase in `current_focus.md`?
- Checks: are there committed files outside `docs/` and `tasks/` that postdate the last `in_progress` status update but predate any results.md write?
- Output: `ok` or a structured list of violations with remediation commands
- `--format json` for agent consumption
- `--strict` flag: treat any warning as a violation

`grain workflow guard` is callable by any agent, any CI runner, any pre-commit hook — no agent-specific knowledge required.

### Part 3 — Git hooks

Spec a `grain hooks install` command that writes two hooks:

**`pre-commit` hook:**
- Runs `grain workflow guard --strict --format json`
- If violations are found, prints them and exits non-zero — blocks the commit
- Skips if the commit only touches `docs/working/` or `tasks/` (metadata-only commits are always allowed)
- Skips if `GRAIN_SKIP_GUARD=1` env var is set (emergency escape hatch, logged)

**`post-checkout` hook (session resume trigger):**
- Runs `grain workflow next --format json` and writes the output to `.grain/last_workflow_state.json`
- This gives any agent that reads `.grain/last_workflow_state.json` on session start the current workflow state without needing to run CLI commands itself
- If the checkout is onto a branch with a stale `current_task.md` (task status `done`), prints a warning

`grain hooks uninstall` removes them.

### Part 4 — Session resume protocol (agent-agnostic)

Spec a `prompts/workflow.resume.md` prompt file that Grain seeds into every workspace. This prompt is not AGENTS.md — it is a Grain-owned file readable by any agent through Grain's context loading. Its job is to define the session resume protocol any agent must follow.

Content of `workflow.resume.md` must:
- Instruct the agent to run `grain workflow next --format json` as the first action in any new session, before reading user messages or touching files
- Instruct the agent to read `current_task.md` and verify the packet is open and in_progress before proceeding
- Define what to do if the packet is missing: run `grain task create` (or `--simple` for direct tasks), set status to `in_progress`, then proceed
- Be written in plain language with no assumption of which AI system is reading it — no "you are Claude", no tool-specific syntax

AGENTS.md and CLAUDE.md should reference `workflow.resume.md` by path rather than duplicating its content — so updates to the resume protocol propagate automatically without requiring both files to be updated.

### Part 5 — Audit and strengthen PROJECT_RULES.md

The current bundled `PROJECT_RULES.md` says "use task packets" in soft language. It needs two additions:

1. A **hard rule section** that states: *"No implementation files may be created or modified outside of an open task packet. 'Open' means: a packet directory exists under `tasks/`, `current_task.md` points to it, and the packet's task.md has status `in_progress`."*

2. A **session start checklist** (3 steps, not prose): run `grain workflow next`, verify packet is open, then act.

These rules must be written without assuming any specific agent's instruction-following format — numbered steps, no agent-specific keywords, callable from a `grain prompt show --context resume` output.

### Part 6 — AGENTS.md block improvements

Grain's `write_agents_md` service writes a Grain-specific block into the repo's AGENTS.md. This block must be updated to:
- Reference `workflow.resume.md` by path for the session start protocol
- Include a hard constraint statement in the block header (not buried in a sub-section)
- Remain useful even if the host AI doesn't specifically understand AGENTS.md conventions — i.e., it reads coherently as plain instructions

Note: AGENTS.md is one enforcement surface among several, not the primary one. The primary enforcement is the state machine (Part 1) and the git hook (Part 3). AGENTS.md supplements them for agents that read it at session start.

## Deliverable
`docs/canonical/enforcement_spec.md` — full spec covering:
- The 6 enforcement layers above and their rationale
- Which layers are agent-agnostic (Parts 1, 2, 3) vs agent-assisted (Parts 4, 5, 6)
- The exact `grain workflow next` state machine changes required
- The `grain workflow guard` command interface and check definitions
- The `grain hooks install` hook specs
- The `workflow.resume.md` content outline
- The `PROJECT_RULES.md` hard rule additions

## Constraints
- All primary enforcement (state machine, guard, hooks) must work with zero AI involvement — a human running git commit must hit the same gates
- No enforcement mechanism may assume a specific AI provider or agent runtime
- The escape hatch (`GRAIN_SKIP_GUARD=1`) must be logged — silent bypass is not acceptable
- The resume protocol must degrade gracefully: if `grain workflow next` fails for any reason, the agent must fall back to reading `current_task.md` directly rather than blocking
- Do not design a server or daemon — all enforcement is CLI and file-based
