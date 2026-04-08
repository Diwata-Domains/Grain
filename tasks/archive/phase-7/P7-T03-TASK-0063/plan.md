# Plan: TASK-0063

## Approach

Extend `init_repo` to create required directories and seed baseline files from repository templates/runtime seed sources. Track created, skipped, blocked, and updated actions explicitly so `--dry-run` and `--force` report accurately. Update CLI result wiring and tests to validate additive-only defaults and non-writing dry-run behavior.

---

## Step 1 — Expand Init Service Seeding

Add seed-file mapping for baseline runtime docs and task templates, then write missing files during init. Preserve skip behavior for existing files and allow `--force` updates for non-canonical seed files.

---

## Step 2 — Surface Update Actions In CLI Result

Propagate service `updated` paths through `forge init` output so force-update behavior is inspectable in both text and JSON output.

---

## Step 3 — Add Coverage For Skip And Dry-Run

Update init-service tests to assert seed-file creation, skip behavior when files already exist, force update behavior, and dry-run no-write behavior.

---

## Verification

- `.venv/bin/pytest -q tests/test_init_service.py`
- `.venv/bin/pytest -q tests/test_phase5_integration.py`
- `.venv/bin/pytest -q`
