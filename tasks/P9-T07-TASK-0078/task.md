# Task: Add OrchestratorPlan validator and integration tests

## Metadata
- **ID:** TASK-0078
- **Status:** done
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Backlog:** P9-T07
- **Packet Path:** tasks/P9-T07-TASK-0078/
- **Dependencies:** TASK-0077
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add a validator for `OrchestratorPlan` artifacts and integration coverage across `grain orchestrate scope`, `grain orchestrate plan`, and `grain adapter list/show`.

## Why This Task Exists
Phase 9 needs contract-level checks for orchestration proposals before phase close, including verification that plan artifacts reference known adapters and required candidate metadata.

## Scope
- Add an OrchestratorPlan validator module in `src/grain/validators/`.
- Validate minimum contract rules: `plan_id`, `status`, `packet_candidates` required fields, and `active_adapters` resolvable to known adapters.
- Add unit tests for validator pass/fail paths.
- Add integration tests that run adapter and orchestrate commands and validate produced plan artifacts.

## Constraints
- Validator is read-only and must not mutate plan artifacts.
- Integration tests must exercise command surfaces, not internal-only shortcuts.

## Escalation Conditions
- If validation requirements exceed current canonical contract (`data_contracts.md §18.3`), stop and route via change proposal.
- If command output contracts are unstable for integration assertions, stop and capture required stabilization as follow-up.
