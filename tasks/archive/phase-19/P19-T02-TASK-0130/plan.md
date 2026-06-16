# Plan: TASK-0130

## Approach

Define one small registry-entry contract and validate it locally from disk. Reuse the current adapter-profile markdown parser for the profile payload, add a lightweight metadata file for registry-facing information, and return structured results that `grain adapter install` can consume later without reparsing everything itself.

---

## Step 1 — Define the minimum package shape

Choose the smallest useful filesystem contract for a community adapter entry, including metadata and one adapter profile payload file.

---

## Step 2 — Implement validation service and result model

Add a service that checks required files, parses metadata, parses adapter profiles, and returns deterministic validation findings without mutating anything.

---

## Step 3 — Add focused tests

Cover happy path, missing-file errors, malformed metadata, and malformed adapter-profile content so later install work can trust the validation surface.

---

## Verification

Run the new validation-service tests together with existing adapter-profile loader tests and import smoke tests.
