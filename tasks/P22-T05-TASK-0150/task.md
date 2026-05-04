# Task: Prompt preview, context inspection, and blocker detail

## Metadata
- **ID:** TASK-0150
- **Status:** review
- **Phase:** Phase 22 — TUI Foundation and Workflow Surfaces
- **Backlog:** P22-T05 — Prompt preview, context inspection, and blocker detail
- **Packet Path:** tasks/P22-T05-TASK-0150/
- **Dependencies:** TASK-0146, TASK-0147, TASK-0148, TASK-0149
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add read-only prompt preview, compact context inspection, and explicit blocker-detail views so operators can see the recommended prompt shape, context composition, and workflow blockers without leaving the TUI.

## Why This Task Exists
The TUI can now show status, inspectors, and actions, but operators still cannot inspect the prompt recommendation and context shape that drive Grain execution. This task closes that gap before the final Phase 22 test/doc pass.

## Scope
- add snapshot support for prompt preview lines, context summary data, and affected-artifact detail
- render dedicated TUI panels for prompt preview, context preview, and blocker detail
- add focused tests for the new preview and detail panels

## Constraints
- keep previews summary-level and deterministic; do not render full prompt bodies or full context exports
- derive all data from existing Grain prompt/context/workflow services rather than inventing new inspection state

## Escalation Conditions
- if useful preview/detail requires full-document rendering or expensive background recomputation, stop and re-scope
