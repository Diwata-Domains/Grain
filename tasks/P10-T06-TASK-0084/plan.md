# Plan: TASK-0084

## Approach

Replace the extraction implementation with tree-sitter parser integration via installed language pack bindings, keeping deterministic entity extraction semantics. Then update tests to enforce parser-contract behavior for supported languages.

---

## Step 1 — Implement Tree-Sitter-Based Extraction

Replace `structural_intelligence_service.py` internals with tree-sitter parser loading and language-aware extraction logic.

---

## Step 2 — Update Dependency Metadata and Tests

Add parser dependency package(s) in `pyproject.toml` and update structural extraction tests to assert tree-sitter parser usage.

---

## Step 3 — Validate Remediation and Update Artifacts

Run targeted and full tests, then update packet and working-doc artifacts for review handoff.

---

## Verification

- `.venv/bin/pytest -q tests/test_structural_intelligence_service.py`
- `.venv/bin/pytest -q tests/test_graph_service.py tests/test_context_build.py tests/test_graph_adapter_capability.py tests/test_phase10_integration_pipeline.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0084`
- `.venv/bin/pytest -q`
