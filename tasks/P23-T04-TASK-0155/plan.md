# Plan: TASK-0155

## Approach

Build one office-artifact review/validation layer over the existing write services instead of duplicating artifact-specific review code. The shared layer should accept `.docx` and spreadsheet write results, run the first structure/reference/policy validators, assemble a reusable office review bundle, and preserve residual-risk signaling when validation is partial or incomplete.

---

## Step 1 — Define validator and review-bundle inputs

Add the shared input types and service boundary that can consume both `.docx` and spreadsheet write results without introducing artifact-specific branching everywhere else.

---

## Step 2 — Implement the first validator passes

Implement structure, reference, and policy validators for the current office artifact surfaces and make them emit consistent result records.

---

## Step 3 — Assemble office review bundles and test them

Build the shared review-bundle assembly path and lock it with focused tests over both artifact types.

---

## Verification

Run focused validator/review-bundle tests plus the office-write service tests they depend on.
