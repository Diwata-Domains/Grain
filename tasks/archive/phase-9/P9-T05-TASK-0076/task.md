# Task: Add adapter list and show commands

## Metadata
- **ID:** TASK-0076
- **Status:** done
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Backlog:** P9-T05
- **Packet Path:** tasks/P9-T05-TASK-0076/
- **Dependencies:** TASK-0073
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement `grain adapter list` and `grain adapter show --id <adapter-id>` commands that inspect adapter profiles from runtime config and emit text/JSON outputs.

## Why This Task Exists
Phase 9 orchestration workflows require explicit adapter inspection surfaces before `orchestrate` commands are exposed. This provides a stable operator-visible adapter capability entrypoint.

## Scope
- Add new `adapter` CLI group with `list` and `show`.
- Wire commands to `load_adapter_profiles(...)` runtime source.
- Add command tests for text/json outputs and unknown adapter ID behavior.

## Constraints
- Commands are read-only and must not mutate profile/runtime files.
- Output must remain machine-readable under `--format json`.

## Escalation Conditions
- If adapter profile runtime schema lacks required fields for display, stop with explicit config error.
- If command behavior would require canonical contract changes, route via change proposal.
