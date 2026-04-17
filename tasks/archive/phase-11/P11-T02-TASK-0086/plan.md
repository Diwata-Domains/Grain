# Plan: TASK-0086

## Approach

Implement a release workflow configuration under `.github/workflows/` and a small version bump utility under `scripts/`, then validate artifact build/check flows without publishing.

---

## Step 1 — Add CI Publish Workflow

Create a GitHub Actions workflow that builds artifacts, runs `twine check`, and publishes to TestPyPI or PyPI based on trigger and target.

---

## Step 2 — Add Version Bump Utility

Add a local script to increment semver values in `pyproject.toml` and include tests for this logic.

---

## Step 3 — Validate and Finalize Task Artifacts

Run targeted verification and full suite, then update packet/working docs for review handoff.

---

## Verification

- `.venv/bin/pytest -q tests/test_bump_version_script.py`
- `.venv/bin/python - <<'PY' ... yaml.safe_load('.github/workflows/publish-pypi.yml') ... PY`
- `.venv/bin/python -m build --wheel`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0086`
- `.venv/bin/pytest -q`
