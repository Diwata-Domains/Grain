# Plan: TASK-0139

## Approach

Extend the upgrade result model so Grain can classify stale managed files that contain user-added content, then change the default non-interactive upgrade path to skip those files while still reporting them as stale/customized. Finish by aligning CLI text/JSON output and focused tests so operators get clear guidance instead of destructive-looking default rewrites.

---

## Step 1 — Detect customized managed files

Use unified diffs to distinguish ordinary stale files from managed files with user-added content, and record that classification in the service result.

---

## Step 2 — Make default upgrade behavior safer

Skip overwriting customized files unless an explicit override path is chosen, while preserving interactive review and normal updates for uncustomized managed files.

---

## Step 3 — Align CLI output and tests

Update text/JSON output so skipped customized files are clearly surfaced, then add focused service and command tests for skip-by-default, explicit apply, and output reporting.

---

## Verification

Run `.venv/bin/python -m pytest -q tests/test_upgrade_cmd.py` and confirm the customization-safety tests pass alongside existing upgrade coverage.
