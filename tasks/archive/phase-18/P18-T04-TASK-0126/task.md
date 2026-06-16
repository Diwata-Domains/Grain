# Task: Integrate data_adapter into context and scope selection

## Metadata
- **ID:** TASK-0126
- **Status:** done
- **Phase:** Phase 18 — Data Adapter
- **Backlog:** P18-T04
- **Packet Path:** tasks/P18-T04-TASK-0126/
- **Dependencies:** TASK-0124, TASK-0125
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none

## Objective
Wire the new `data_adapter` signals into context export and orchestration scope analysis so Phase 18 data workflows surface the right artifact summaries and adapter activations deterministically. This task should make the new extractor usable in context exports and prove that orchestration can recognize data-heavy scopes without changing proposal-only behavior.

## Why This Task Exists
Phase 18 now has a contract, a metadata extractor, and notebook ownership migration, but the broader context and scope surfaces still do not exercise those additions. This task closes that gap so the `data_adapter` becomes a real participant in user-facing context and orchestration flows.

## Scope
- route data-artifact source rendering through `DataArtifactExtractor`
- prove context export can include metadata-only summaries for data artifacts
- prove orchestration scope analysis can activate `data_adapter` signals in representative data-workflow scopes
- keep orchestration outputs proposal-only and backward-compatible

## Constraints
- do not change packet/workflow authority or advisory-only orchestration semantics
- do not widen into onboarding/scanner recommendation changes in this task
- preserve deterministic output when optional data readers are unavailable

## Escalation Conditions
- if activating `data_adapter` in orchestration requires changing adapter-capability contracts rather than wiring existing surfaces, stop and log the gap
- if context export would need to sample artifact contents instead of metadata summaries, do not widen scope
