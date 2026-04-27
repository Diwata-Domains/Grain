# Plan: TASK-0095

## Approach

Implement a deterministic, filesystem-only scanner service with a small explicit heuristic set. Keep the domain output compact but sufficient for downstream draft-doc generation and integration tests.

---

## Step 1 — Define `ScanResult` domain model

Create `src/grain/domain/scan_result.py` with the fields needed by Phase 13 scanner outputs: root, language summary, adapter signals, key files, CI configs, and documentation files.

---

## Step 2 — Implement `CodebaseScanner`

Create `src/grain/services/codebase_scanner.py` with read-only `scan()` behavior.
Use extension/name/path heuristics for language, adapter, key-file, CI, and docs detection.
Ignore common generated/dependency directories and return sorted relative POSIX paths.

---

## Step 3 — Add scanner tests

Create `tests/test_codebase_scanner.py` with fixture-style synthetic repo trees covering language frequency ordering, adapter detection, key file detection, CI detection, docs detection, ignored dirs, and missing-root behavior.

---

## Verification

- `.venv/bin/pytest -q tests/test_codebase_scanner.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0095`
- `.venv/bin/pytest -q`
