# Plan: TASK-0045

## Approach

Build a small review service on top of the existing packet validators. The service will resolve the packet directory, run packet validity and closure-prerequisite checks, and return a structured report that later CLI commands can format.

---

## Step 1 — Add review domain/report types

Create a lightweight report object that captures packet status, readiness, warnings, and blocker lists in a form suitable for future CLI output.

---

## Step 2 — Implement review validation service

Add a service function that loads the packet, validates it, and derives review/completion readiness from existing validator rules.

---

## Step 3 — Add focused tests

Cover the happy path, missing-packet failure, and incomplete-packet behavior so the service contract is stable before CLI work begins.

---

## Verification

Run the targeted review-service tests and the full pytest suite.
