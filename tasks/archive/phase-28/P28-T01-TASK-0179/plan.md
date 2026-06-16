# Plan: TASK-0179

## Approach

Implement a narrow packet-local verification request flow that validates the packet state, writes a deterministic request artifact, and updates the review bundle to reflect pending verification. Keep it local and provider-explicit.

---

## Step 1 — Add verification request service

Create a service that resolves the packet, validates submit preconditions, generates a `verification_id`, and writes `verification_request.json`.

---

## Step 2 — Expose `grain verify submit`

Add the new CLI group and submit command, register it in the main CLI, and return clear text/json output.

---

## Step 3 — Verify the bridge contract

Add focused tests for request creation, JSON output, unsupported providers, and packet-state validation.

---

## Verification

Run focused verification-bridge and command-group tests.
