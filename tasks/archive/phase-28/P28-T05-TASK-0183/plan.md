# Plan: TASK-0183

## Approach

Update the public/operator-facing surfaces that an agent or reviewer will actually read, then lock that guidance with release-surface tests so the Assay bridge does not drift back to the old deferred Sentinel story.

---

## Step 1 — Fix the public/operator guidance

Add the real `grain verify submit/status/ingest` loop to the README and runtime project rules, including the packet-local and no-close-while-pending constraints.

---

## Step 2 — Repair the canonical CLI spec

Replace the stale deferred Sentinel wording in `docs/canonical/cli_spec.md` with the live Assay bridge contract and its packet-local boundaries.

---

## Step 3 — Lock the guidance with tests

Update the close prompt and release-surface tests so future edits keep the verification loop visible and consistent with the current implementation.

---

## Verification

Run `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_verify_submit_cmd.py tests/test_command_groups.py tests/test_closure_validation.py tests/test_workflow_state_service.py tests/test_task_close_cmd.py tests/test_release_surface.py`.
