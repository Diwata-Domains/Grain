# Task: Implement metadata extractor for data and model artifacts

## Metadata
- **ID:** TASK-0124
- **Status:** done
- **Phase:** Phase 18 — Data Adapter
- **Backlog:** P18-T02
- **Packet Path:** tasks/P18-T02-TASK-0124/
- **Dependencies:** TASK-0123
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none

## Objective
Implement a deterministic metadata extractor for Phase 18 dataset and model artifact file types. The extractor must report stable file metadata for supported binary artifacts and add lightweight schema hints only when an optional local reader is available, without ever sampling or inlining artifact contents.

## Why This Task Exists
Phase 18 now has a documented `data_adapter` contract, but there is no extractor behind it. This task provides the first executable surface for that contract so later context and orchestration tasks can use artifact metadata without widening into heavy binary parsing.

## Scope
- add a new service for `.parquet`, `.feather`, `.arrow`, `.h5`, `.hdf5`, `.pkl`, `.joblib`, `.pt`, and `.onnx`
- keep extraction metadata-only and degrade gracefully when optional readers are unavailable
- add focused tests for supported types, graceful degradation, and optional-reader hints
- record optional Phase 18 reader dependencies in `pyproject.toml`

## Constraints
- do not wire the extractor into context exports or adapter-driven source selection in this task
- do not inspect or deserialize dataset/model payload contents for pickle, joblib, torch, or onnx files
- keep output deterministic, local-first, and safe for large/binary files

## Escalation Conditions
- if useful schema hints require mandatory heavy dependencies rather than optional readers, keep the extractor metadata-only and log the limit
- if any file type would require unsafe deserialization to inspect, do not add that inspection path
