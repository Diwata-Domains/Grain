# Plan: TASK-0085

## Approach

Update `pyproject.toml` with production-ready package metadata and build-tool configuration for the existing `src/` layout, then validate by building a wheel and inspecting the archive content to ensure only package artifacts ship.

---

## Step 1 — Finalize Packaging Metadata

Add project metadata fields required for distribution clarity: summary, readme reference, license expression, URLs, keywords, and classifiers.

---

## Step 2 — Validate Build Artifact Hygiene

Build wheel from source with current config and inspect wheel file entries to verify no development/test files are included.

---

## Step 3 — Update Task and Working Artifacts

Record results and set Phase 11 sequencing docs for the next task.

---

## Verification

- `.venv/bin/python -m build --wheel`
- `python -m zipfile -l dist/grain-*.whl`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0085`
- `.venv/bin/pytest -q`
