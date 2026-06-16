# Plan: TASK-0156

## Approach

Wrap the existing office write and review services in narrow CLI commands rather than inventing new workflow state. The commands should require an active packet context or explicit artifact paths, surface operation mode and output paths clearly, and expose validator/review-bundle results in both human-readable and machine-readable forms.

---

## Step 1 — Define the CLI surface

Choose the smallest command set that can drive `.docx` and spreadsheet propose/export flows and inspect the shared office review bundle.

---

## Step 2 — Wire CLI to the existing services

Connect the commands to the existing office write and review services while preserving packet-first constraints and stable outputs.

---

## Step 3 — Lock command behavior with focused tests

Add focused CLI tests that cover the main mutation and review-inspection paths without expanding into full end-to-end smoke coverage yet.

---

## Verification

Run focused CLI tests plus the office service tests the new commands depend on.
