# Task: Token-efficiency and context-budget reporting

## Metadata
- **ID:** TASK-0177
- **Status:** done
- **Phase:** Phase 27 — Recipe Layer and Operator Ergonomics
- **Backlog:** P27-T02
- **Packet Path:** tasks/P27-T02-TASK-0177/
- **Dependencies:** TASK-0175
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Add task-scoped context-cost reporting that exposes source counts, byte and token proxies, warning thresholds, and trim hints through the existing context commands.

## Why This Task Exists
Phase 27 needs a concrete token-efficiency surface before the TUI can explain context cost or before operators can reliably trim overly broad bundles during aggressive multi-agent work.

## Scope
- Add context-budget metadata to the context bundle export surface.
- Surface the budget in `grain context build` and `grain context export`.
- Add focused tests for JSON and text budget reporting.

## Constraints
- Keep the budget heuristic file-backed and deterministic.
- Use proxies only; do not depend on provider-specific token APIs.

## Escalation Conditions
- Stop if the design requires hidden runtime accounting or model-provider callbacks.
