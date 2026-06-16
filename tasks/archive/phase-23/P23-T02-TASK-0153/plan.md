# Plan: TASK-0153

## Approach

Build a thin `.docx` write service on top of `python-docx` and the shared office-write contracts. Keep the update surface explicit and deterministic: load a document, apply a bounded mutation input, write either a preview/export file or a proposed output file, and emit a structural change summary that records heading, paragraph, and table-level effects.

---

## Step 1 — Define the `.docx` write surface

Add the `.docx` service types and core operations that use the shared office-write request/decision model from `TASK-0152`.

---

## Step 2 — Implement safe propose and export behavior

Implement the document load/update/save path for `propose` and `export-as-new-file`, keeping all outputs explicit and reviewable.

---

## Step 3 — Lock the structural summary with tests

Add focused tests that prove the service preserves a usable `.docx` structure and produces the expected change-summary output.

---

## Verification

Run focused tests for the new `.docx` write service and any supporting import or extraction seams it depends on.
