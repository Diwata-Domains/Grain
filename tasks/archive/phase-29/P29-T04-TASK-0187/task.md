# Task: Add operator-facing workflow diagnostics

## Metadata
- **ID:** TASK-0187
- **Status:** done
- **Phase:** Phase 29 — Workflow Compliance Hardening
- **Backlog:** P29-T04
- **Packet Path:** tasks/P29-T04-TASK-0187/
- **Dependencies:** TASK-0185
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Add a thin operator-facing diagnostic surface that explains why Grain is blocked or what the next workflow move should be, using the existing workflow evaluator rather than new hidden state or background services.

## Why This Task Exists
The Phase 29 hardening goal is to reduce manual redirection during long agent sessions. The previous slices added stronger blockers and drift detection, but operators still have to interpret raw stop reasons manually. This task turns the existing workflow state into a more actionable explanation layer.

## Scope
- Add a `grain workflow explain` surface over the existing evaluator.
- Map common stop reasons and next-action states to concrete file-backed operator guidance.
- Add focused command coverage for text and JSON outputs.

## Constraints
- Keep the implementation file-backed and read-only; no daemon, no database, no hidden state.
- Reuse the existing workflow evaluator instead of duplicating workflow decision logic.

## Escalation Conditions
- Stop if the diagnostic surface requires a second workflow engine instead of translating existing evaluator output.
