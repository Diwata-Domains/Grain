# Plan: TASK-0083

## Approach

Add a focused integration test module that exercises the complete structural-intelligence pipeline from deterministic extraction through graph construction, graph-assisted context selection, and orchestration scope analysis. Add a second integration test to confirm graph artifacts are rebuilt from source state rather than relying on prior persisted artifacts.

---

## Step 1 — Add Full-Pipeline Integration Coverage

Create a seeded temporary repository fixture in tests and assert the extraction, graph, context, and orchestration services interoperate with deterministic outputs.

---

## Step 2 — Add Graph Rebuild Determinism Validation

Build and persist a graph, tamper with the persisted file, rebuild from source artifacts, and assert rebuilt graph nodes/edges remain consistent.

---

## Step 3 — Validate and Update Packet Artifacts

Run targeted and full tests, then finalize packet artifacts and working docs for handoff at `review`.

---

## Verification

- `.venv/bin/pytest -q tests/test_phase10_integration_pipeline.py`
- `.venv/bin/pytest -q tests/test_graph_service.py tests/test_context_build.py tests/test_orchestration_service.py tests/test_graph_adapter_capability.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0083`
- `.venv/bin/pytest -q`
