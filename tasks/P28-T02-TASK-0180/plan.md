# Plan: TASK-0180

## Approach

Keep the status command thin and read-only by resolving `verification_request.json` from its `verification_id`, then returning the stored packet-local request record in both text and JSON formats.

---

## Step 1 — Add verification request lookup

Extend the verification service with a lookup path that resolves a request artifact by `verification_id`.

---

## Step 2 — Expose `grain verify status`

Add the status subcommand and reuse the same explicit error-reporting pattern as `verify submit`.

---

## Step 3 — Verify the read-only bridge

Add focused tests for status success, JSON output, and unknown request failure.

---

## Verification

Run focused verification-bridge and command-group tests.
