# Task: Desktop and Obsidian smoke tests, docs, and closeout

## Metadata
- **ID:** TASK-0164
- **Status:** done
- **Phase:** Phase 24 — Desktop Integrations and Obsidian Support
- **Backlog:** P24-T05 — Desktop and Obsidian smoke tests, docs, and closeout
- **Packet Path:** tasks/P24-T05-TASK-0164/
- **Dependencies:** TASK-0159, TASK-0163
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add the final smoke coverage and operator guidance for the first desktop integration and Obsidian slices so Grain clearly documents the CLI-first boundary, the local MCP wrapper path, and the dedicated Obsidian adapter usage before Phase 24 closes.

## Why This Task Exists
Phase 24 now has the local MCP wrapper scaffold and the first dedicated Obsidian context behavior, but the phase is not complete until those surfaces are documented together and covered by a combined release/smoke slice. This task closes the loop and makes the operator story explicit.

## Scope
- add operator docs that explain how desktop invocation and Obsidian vault work fit the existing CLI-first Grain model
- add focused smoke/release coverage that locks those documented expectations in place

## Constraints
- keep the CLI canonical and treat the MCP wrapper as a local adapter surface, not a second workflow engine
- do not add new desktop capabilities or Obsidian mutation behavior in this closeout task

## Escalation Conditions
- if the docs or smoke coverage imply broader desktop control-plane behavior or deeper Obsidian semantics than the phase actually implements, stop and narrow the scope before landing changes
