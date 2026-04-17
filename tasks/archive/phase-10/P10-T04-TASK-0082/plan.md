# Plan: TASK-0082

## Approach

Implement a graph-aware adapter capability class that computes scope and impact signals from Layer 3 graph artifacts when available, and register it by default on loaded adapter profiles. Update orchestration scoring and signal payloads to consume both scope and impact capability outputs.

---

## Step 1 — Add Graph-Aware Capability Implementation

Create adapter capability implementation backed by graph service outputs with deterministic static fallback behavior.

---

## Step 2 — Register Capability on Loaded Profiles

Attach graph-aware capabilities in `load_adapter_profiles(...)` so orchestration service receives graph-backed methods through existing protocol calls.

---

## Step 3 — Update Orchestration Signal Consumption and Tests

Update orchestration scoring/scope analysis to consume `analyze_impact` outputs and add tests for capability behavior and payload shape.

---

## Verification

- `.venv/bin/pytest -q tests/test_graph_adapter_capability.py tests/test_orchestration_service.py tests/test_context_build.py tests/test_graph_service.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0082`
- `.venv/bin/pytest -q`
