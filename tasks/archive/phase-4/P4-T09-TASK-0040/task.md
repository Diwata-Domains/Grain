# Task: Implement model selection logic

## Metadata
- **ID:** TASK-0040
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T09
- **Packet Path:** tasks/P4-T09-TASK-0040/
- **Dependencies:** TASK-0039 (P4-T08, done)

## Objective
Implement selection logic that returns the appropriate model class for a workflow stage or task role, using runtime model profile definitions and escalation-oriented routing behavior.

## Why This Task Exists
Phase 4 requires model routing support. P4-T09 provides the routing decision layer that P4-T11 (`forge model select`) and P4-T12 (`forge model escalate`) will call.

## Scope
- Add stage/role routing logic to `src/forge/domain/routing.py`.
- Add model selection service in `src/forge/services/model_service.py`.
- Add unit tests for routing and service behavior in `tests/test_model_service.py`.
- Keep this task scoped to selection logic only; no CLI behavior changes.

## Constraints
- Routing must remain provider-agnostic and class-based.
- Logic should mirror runtime profile guidance and escalation intent, not hardcoded vendor mappings.
- Do not implement `forge model show`, `forge model select`, or `forge model escalate` command wiring in this task.

## Escalation Conditions
- If stage/role contract is too ambiguous for deterministic routing, stop and record proposal-level clarification instead of inventing hidden rules.
- If implementation requires changing canonical workflow stage definitions, stop and raise a proposal.
