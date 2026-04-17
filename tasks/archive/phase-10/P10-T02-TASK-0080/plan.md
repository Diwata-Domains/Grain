# Plan: TASK-0080

## Approach

Implement a graph service that consumes Layer 1 structural extraction outputs and emits an inspectable JSON knowledge graph artifact. Prefer NetworkX when available, while preserving deterministic local fallback behavior when the dependency is not present in the runtime.

---

## Step 1 — Add Graph Builder Service

Create `src/grain/services/graph_service.py` with:
- graph node/edge/artifact dataclasses
- graph build function from source paths and structural extractions
- confidence-labeled typed edge construction
- artifact persistence and combined build+persist helper

---

## Step 2 — Add Graph Service Tests

Create `tests/test_graph_service.py` for:
- graph node/edge creation shape
- confidence label contract
- JSON artifact persistence
- combined build+persist payload
- required-input validation

---

## Step 3 — Update Dependency Declaration

Add `networkx` dependency in `pyproject.toml` for Layer 3 implementation.

---

## Verification

- `.venv/bin/pytest -q tests/test_graph_service.py tests/test_structural_intelligence_service.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0080`
- `.venv/bin/pytest -q`
