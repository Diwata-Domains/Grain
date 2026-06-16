# Task: Codex and CLI integration guidance/helpers

## Metadata
- **ID:** TASK-0161
- **Status:** done
- **Phase:** Phase 24 — Desktop Integrations and Obsidian Support
- **Backlog:** P24-T02 — Codex and CLI integration guidance/helpers
- **Packet Path:** tasks/P24-T02-TASK-0161/
- **Dependencies:** TASK-0159
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add explicit Codex-facing guidance and any small helper surfaces needed for CLI-first usage in desktop or tool-execution environments while keeping the solution thin, local-first, and documentation-heavy unless a real helper command is justified.

## Why This Task Exists
The local MCP scaffold now covers Claude/Desktop-style invocation. Grain still needs a clear Codex-facing operating path so CLI-first desktop or tool-execution environments can use the product correctly without guessing how the workflow, prompts, and new MCP surface fit together.

## Scope
- document the Codex/CLI-first integration path clearly and add small helper surfaces only if they simplify real usage
- keep the task focused on operator guidance and thin integration helpers, not broader desktop orchestration

## Constraints
- CLI remains the canonical Grain command surface even when helpers are added
- do not broaden into Obsidian adapter work or hosted desktop execution in this task

## Escalation Conditions
- if the guidance implies a broader product boundary than the current CLI-first local model supports, stop and re-scope before implementation
