# Task: Review bundle and validator pipeline for office artifacts

## Metadata
- **ID:** TASK-0155
- **Status:** done
- **Phase:** Phase 23 — Writable Office Artifacts
- **Backlog:** P23-T04 — Review bundle and validator pipeline for office artifacts
- **Packet Path:** tasks/P23-T04-TASK-0155/
- **Dependencies:** TASK-0153, TASK-0154
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Wire the shared review-bundle and validator pipeline across the `.docx` and spreadsheet write workflows so office artifact mutations emit one consistent review surface with structure, reference, and policy validation results plus residual-risk handling.

## Why This Task Exists
Phase 23 now has both artifact-specific write paths, but they still stop at raw artifact summaries. This task is the bridge that makes those writes look like real Grain review artifacts instead of one-off service outputs.

## Scope
- build a shared office-artifact review-bundle assembly path over the `.docx` and spreadsheet write results
- add the first validator layer for structure, reference, and policy checks with residual-risk behavior for partial validation

## Constraints
- keep the review surface file-backed and packet-first with no hidden state or background validation services
- do not introduce CLI mutation commands yet; this task is limited to shared review and validation plumbing for the service layer

## Escalation Conditions
- if the validator model requires changing the shared contract from `TASK-0152`, stop and re-scope before implementation
