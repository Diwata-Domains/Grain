# Plan: TASK-0079

## Approach

Add a dedicated structural extraction service that inspects file content by language family and emits normalized structural entity records. Use deterministic parsers only (Python AST and rule-based extraction) so Phase 10 Layer 1 remains local and reproducible.

---

## Step 1 — Add Structural Extraction Service

Create `src/grain/services/structural_intelligence_service.py` with:
- normalized result dataclasses
- single-file extraction entrypoint
- batch extraction helper
- language-specific extractors for code/frontend/docs/devops artifacts

---

## Step 2 — Add Layer 1 Test Coverage

Create `tests/test_structural_intelligence_service.py` to verify extraction behavior for:
- python structural entities
- frontend imports/calls
- markdown headings/links
- devops dependency declarations
- multi-file extraction skipping missing files

---

## Step 3 — Update Runtime Dependency Declaration

Add `tree-sitter` binding dependency in `pyproject.toml` for Phase 10 structural-intelligence implementation track.

---

## Verification

- `.venv/bin/pytest -q tests/test_structural_intelligence_service.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0079`
- `.venv/bin/pytest -q`
