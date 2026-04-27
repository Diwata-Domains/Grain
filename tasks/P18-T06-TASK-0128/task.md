# Task: Phase 18 integration tests

## Metadata
- **ID:** TASK-0128
- **Status:** done
- **Phase:** Phase 18 — Data Adapter
- **Backlog:** P18-T06
- **Packet Path:** tasks/P18-T06-TASK-0128/
- **Dependencies:** TASK-0124, TASK-0125, TASK-0126, TASK-0127
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none

## Objective
Add end-to-end Phase 18 coverage for the new `data_adapter`. The suite should prove the full slice works together across context selection/export, metadata-only artifact summaries, orchestration scope activation, and onboarding/scanner detection for a representative data-science repo layout.

## Why This Task Exists
Phase 18 is nearly complete, but the work is still split across unit and focused integration tests. This task provides the final cross-surface proof needed to close the phase confidently.

## Scope
- add a new Phase 18 integration test module
- validate notebook + parquet behavior under `data_adapter`
- validate orchestration scope signals and onboarding/scanner outputs in the same repo shape
- use deterministic local fixtures and fakes only

## Constraints
- do not add live dependency requirements or networked providers
- keep the suite representative but fast
- preserve proposal-only orchestration semantics and metadata-only artifact handling

## Escalation Conditions
- if the integrated path reveals a contract mismatch between context, orchestration, and onboarding behavior, stop and log it instead of papering it over in tests
