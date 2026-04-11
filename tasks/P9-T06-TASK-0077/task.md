# Task: Add orchestrate scope and plan commands

## Metadata
- **ID:** TASK-0077
- **Status:** done
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Backlog:** P9-T06
- **Packet Path:** tasks/P9-T06-TASK-0077/
- **Dependencies:** TASK-0074, TASK-0075, TASK-0076
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement `grain orchestrate scope --scope <text>` and `grain orchestrate plan --scope <text>` commands that surface adapter/domain signals and generate draft `OrchestratorPlan` proposal artifacts under `docs/working/proposals/`.

## Why This Task Exists
Phase 9 requires operator-facing orchestration command surfaces that consume the orchestration service and keep all outputs proposal-only.

## Scope
- Add new `orchestrate` CLI group with `scope` and `plan` commands.
- Add scope-analysis service function to expose adapter/domain signal output.
- Extend orchestration planning builders to support optional adapter filtering.
- Persist plan proposals as inspectable JSON artifacts in `docs/working/proposals/`.
- Add command and service tests for text/json output, proposal file creation, and adapter filter error paths.

## Constraints
- Commands are proposal-only and must not create task packets or mutate backlog/phase docs.
- `orchestrate plan` must write artifacts only to the working proposals layer.
- JSON output must remain stable and machine-readable.

## Escalation Conditions
- If OrchestratorPlan persistence format requires canonical contract change, stop and log a change proposal.
- If adapter profile config cannot be loaded or filtered cleanly, return explicit command failure.
