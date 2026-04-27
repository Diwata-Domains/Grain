# Plan: TASK-0126

## Approach

Use the new extractor and migrated notebook ownership as additive wiring, not a redesign. Extend context export to render metadata-only summaries for data artifacts, then add focused orchestration tests showing `data_adapter` can activate for notebook/data-heavy scopes while preserving proposal-only payload shapes.

---

## Step 1 — Wire context export rendering

Teach the export adapter to render Phase 18 data artifact suffixes through `DataArtifactExtractor` instead of raw/binary fallbacks.

---

## Step 2 — Prove orchestration participation

Add or adjust orchestration tests so a repo with data-adapter profile signals can activate `data_adapter` and report its affected files in scope analysis.

---

## Step 3 — Add focused context/export tests

Cover a representative metadata-only context export path for a data artifact and make sure notebook paths still remain intact after the new rendering branch.

---

## Verification

Run focused export, notebook, orchestration, and import tests to verify the new wiring without relying on the full Phase 18 integration suite.
