# Plan: TASK-0154

## Approach

Build a thin spreadsheet write service on top of `openpyxl` and the shared office-write contracts. Keep the mutation surface explicit and deterministic: load a workbook, apply bounded cell updates, write either a proposal or export file, and emit a touched-sheet, touched-range, and formula-aware summary that later review-bundle plumbing can consume.

---

## Step 1 — Define the spreadsheet write surface

Add the spreadsheet service types and core operations that use the shared office-write request/decision model from `TASK-0152`.

---

## Step 2 — Implement safe propose and export behavior

Implement workbook load/update/save behavior for `propose` and `export-as-new-file`, keeping all outputs explicit and reviewable.

---

## Step 3 — Lock the spreadsheet summary with tests

Add focused tests that prove the service preserves a usable workbook and emits the expected touched-sheet, touched-range, and formula-aware summary output.

---

## Verification

Run focused tests for the new spreadsheet write service and any supporting shared office-write seams it depends on.
