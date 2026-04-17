# Task: Define workflow loop configuration surface and loader

## Metadata
- **ID:** TASK-0090
- **Status:** done
- **Phase:** Phase 12 — Automated Workflow Loop
- **Backlog:** P12-T01
- **Packet Path:** tasks/P12-T01-TASK-0090/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Define and implement the runtime configuration surface for workflow-loop agent/model selection and supervision level controls.

## Why This Task Exists
Phase 12 needs a stable configuration contract before implementing the loop command so execution behavior and invocation wiring are deterministic.

## Scope
- Add workflow-loop config domain models.
- Add a configuration service to load and validate `docs/runtime/workflow_loop.yaml`.
- Add runtime config file with default values and schema shape.
- Add tests for parsing, validation, and override behavior.

## Constraints
- Keep scope to configuration/domain/service only.
- Do not implement the `grain workflow loop` command in this task.

## Escalation Conditions
- If config requirements imply CLI surface changes, defer to `P12-T02` and log follow-up.
