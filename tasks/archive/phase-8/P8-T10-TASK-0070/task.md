# Task: Define Forge-Side Verification Bridge Contract for Sentinel Handoff

## Metadata
- **ID:** TASK-0070
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T10
- **Packet Path:** tasks/P8-T10-TASK-0070/
- **Dependencies:** P8-T01 (done)
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective

Define the minimal Forge-side command contract so Sentinel can plug into the workflow runner when it exists. This is a contract-definition task, not a Sentinel implementation task. Deliverables: (1) define the `forge verify` command group in `cli_spec.md` as a deferred surface with three subcommands — `submit`, `status`, `ingest`; (2) define the minimal Sentinel result payload schema Forge expects to receive; (3) define where verification results land in the runner stop-condition logic; (4) record the complete Sentinel bridge contract in `v2_plan.md §11`.

## Why This Task Exists

The Phase 8 workflow runner can stop at a verification gate, but there is no canonical contract for what commands trigger that gate, what Sentinel sends back, or what Forge does with the result. Without this contract, FR-006 (Sentinel Integration Layer) has no surface to implement against. This task produces the paper contract — defined now so Sentinel implementation has a stable target later.

## Scope
- Add `forge verify` command group to `cli_spec.md` §6.9 as a deferred surface (three commands: submit, status, ingest)
- Update `cli_spec.md` §12 Command Coverage Summary to include the verify commands
- Add `v2_plan.md §11` Sentinel Bridge Contract section with: command surface reference, result payload schema, verification gate stop condition, and bridge contract terms
- Update `docs/working/open_questions.md` if any questions arise from the contract definition
- Update `docs/working/backlog.md` P8-T10 status → in_progress

## Constraints
- No Sentinel implementation — this task produces a specification only
- Do not alter any existing cli_spec.md sections; only add the new §6.9 section and update §12
- Do not implement `forge verify` commands — they must be registered as deferred stubs per §5.1 (placeholder command behavior)
- Do not modify other canonical docs (product_scope.md, architecture.md, workflow_spec.md, data_contracts.md)
- Keep the payload schema minimal — only fields needed for the runner stop condition and Forge workflow integration

## Escalation Conditions
- If the bridge contract requires changes to existing cli_spec.md sections (not just additions), stop and raise a change proposal
- If the payload schema definition conflicts with architecture.md §4.14 Orchestration Service or §4.12 Review/Gate Layer, stop and record the conflict

## Closure Requirements

Before the packet can move to review, the task artifacts must include:

- `results.md` with current task status, review readiness, recommended next status, files changed, summary, test results, efficiency metrics, review notes, deliverable checklist, and blockers
- `handoff.md` with packet identity, phase, status, review readiness, recommended next status, summary, what was built, what review should check, known issues or follow-ups, files changed, reviewer notes, and closeout intake

Before the packet can move from review to done, the review artifacts must include:

- explicit `open_questions_to_log`
- explicit `proposal_candidates_to_log`
- explicit `followups_to_log`

Use `None` when a category has no items.

## Reviewer Focus
- Verify the `forge verify` command surface is correctly scoped as deferred (not implemented) per §5.1
- Verify the payload schema is minimal and only contains fields Forge actually needs for runner gate logic
- Verify §11 in v2_plan.md is coherent with §10 (runner stop conditions) and with architecture.md §4.12 (Review/Gate Layer)
- Confirm no existing cli_spec.md sections were altered — only additions
