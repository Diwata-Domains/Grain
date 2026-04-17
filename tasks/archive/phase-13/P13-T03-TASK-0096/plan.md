# Plan: TASK-0096

## Approach

Implement an additive document generator that transforms `ScanResult` signals into clearly marked draft docs. Keep content deterministic and minimal, prioritize useful structure over precision claims, and ensure safe no-overwrite behavior.

---

## Step 1 — Implement generator service

Add `OnboardDocGenerator` with `generate(scan, dry_run=False)` and manifest output (`created`, `skipped`, `root`).

---

## Step 2 — Build deterministic draft content

Generate draft `product_scope`, `architecture`, `backlog`, and `open_questions` files from scan signals. Include `# DRAFT` markers and gap-driven open questions.

---

## Step 3 — Add focused tests

Add tests for file creation shape, additive skip behavior, dry-run behavior, draft markers, and sparse-signal open question generation.

---

## Verification

- `.venv/bin/pytest -q tests/test_onboard_doc_generator.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0096`
- `.venv/bin/pytest -q`
