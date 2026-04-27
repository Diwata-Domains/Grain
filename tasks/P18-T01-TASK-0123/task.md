# Task: Define data_adapter contract and extraction boundaries

## Metadata
- **ID:** TASK-0123
- **Status:** done
- **Phase:** Phase 18 — Data Adapter
- **Backlog:** P18-T01
- **Packet Path:** tasks/P18-T01-TASK-0123/
- **Dependencies:** TASK-0122
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Define the Phase 18 `data_adapter` contract before any extractor or context wiring lands. This slice establishes the metadata-only extraction policy for dataset and ML artifact files, documents the adapter's initial file-pattern ownership, and updates the runtime adapter profile inventory so later implementation tasks have a stable contract to build against.

## Why This Task Exists
Phase 18 is blocked without an explicit adapter contract and extraction boundary. The backlog now resolves that boundary through Q18, and the runtime adapter profile document needs to reflect the new `data_adapter` so later tasks can add extractors, notebook ownership migration, and context/orchestration integration without changing scope mid-phase.

## Scope
- add `data_adapter` to the supported adapter inventory and profile list in `docs/runtime/adapter_profiles.md`
- document that Phase 18 data files and model artifacts are metadata-only context sources
- document that `.ipynb` migration into `data_adapter` is planned for a later Phase 18 task rather than this slice
- add parser-level coverage proving the adapter profile contract can represent the new adapter cleanly

## Constraints
- do not change packet lifecycle semantics, workflow routing rules, or canonical authority ordering
- do not implement real data extraction, notebook ownership migration, or context-service wiring in this task
- keep the contract deterministic, local-first, and safe for large or binary artifacts

## Escalation Conditions
- if Phase 18 requires content sampling rather than metadata-only extraction for data files, stop and re-open the scope decision
- if the existing adapter-profile schema cannot express the required contract without a parser/domain change, log the gap before widening implementation scope
