# Plan: TASK-0152

## Approach

Add one shared domain contract and one thin service layer for office artifact writes. The domain layer will define reusable request, decision, validator, and review-bundle shapes. The service layer will resolve the allowed write mode according to the locked Phase 23 safety rules and assemble the reusable review bundle for later `.docx` and spreadsheet tasks.

---

## Step 1 — Define shared domain types

Add the office artifact, write-request, write-decision, validator-result, and review-bundle dataclasses with narrow validation so later tasks can reuse one consistent contract.

---

## Step 2 — Implement safety-mode resolution

Add a shared service that resolves `propose`, `apply`, and `export-as-new-file` according to explicit operator intent, validation state, and high-risk flags.

---

## Step 3 — Lock behavior with focused tests

Add targeted tests for fallback behavior and review-bundle assembly so later `.docx` and spreadsheet tasks can build on a proven contract.

---

## Verification

Run focused tests for the new office-write contract/service plus a package import sanity check.
