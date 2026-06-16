# Plan: TASK-0181

## Approach

Extend the packet-local verification service with a deterministic ingest path, then add a thin CLI wrapper and focused tests that prove request lookup, payload validation, result persistence, and review-bundle updates.

---

## Step 1 — Add ingest service support

Implement payload validation plus packet-local result writing in `verification_service.py`, reusing the existing `verification_id` request lookup instead of inventing a second verification index.

---

## Step 2 — Add CLI surface

Expose `grain verify ingest --verification-id --payload` in `src/grain/cli/verify.py` and keep both text and JSON modes aligned with the rest of the verify group.

---

## Step 3 — Prove the packet-local workflow effects

Add tests that show successful ingestion updates `verification_request.json`, writes `verification_result.json`, and rewrites the `Verification Review` section in `results.md`, plus failure coverage for malformed payloads.

---

## Verification

Run the focused verify-bridge and command-group suite with `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_verify_submit_cmd.py tests/test_command_groups.py`.
