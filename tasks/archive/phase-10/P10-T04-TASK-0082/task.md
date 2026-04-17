# Task: Wire graph into orchestration adapter capabilities

## Metadata
- **ID:** TASK-0082
- **Status:** done
- **Phase:** Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph
- **Backlog:** P10-T04
- **Packet Path:** tasks/P10-T04-TASK-0082/
- **Dependencies:** TASK-0081
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Connect Layer 3 graph outputs to adapter capability methods used by orchestration (`detect_scope`, `analyze_impact`) so graph-derived signals are consumed when available, with static fallback when unavailable.

## Why This Task Exists
Phase 10 requires orchestration capability signals to become graph-aware before full structural-intelligence integration coverage can be completed.

## Scope
- Add graph-aware adapter capability implementation.
- Register capabilities during adapter profile loading.
- Consume graph-backed `detect_scope` and `analyze_impact` signals in orchestration scoring/scope analysis.
- Add tests validating capability behavior and orchestration payload integration.

## Constraints
- Keep capability outputs deterministic and local-only.
- Preserve graceful degradation when graph construction is unavailable.
- Do not mutate workflow state from capability methods.

## Escalation Conditions
- If capability contract changes are required beyond current protocol fields, stop and route via proposal.
- If graph-backed signals cause nondeterministic adapter ranking, stop and record blocker details.
