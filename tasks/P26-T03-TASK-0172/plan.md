# Plan: TASK-0172

## Approach

Keep the output-validation slice objective-sensitive. The crawler adapter already selects the right class of files, so this task should only change their ordering when the packet objective clearly points at extraction quality, output validation, or normalization work.

---

## Step 1 — Audit the current crawler selection behavior

Inspect the new crawler selection rules to see where output fixtures, schemas, and normalization surfaces can be introduced without weakening the config/selector-first default.

---

## Step 2 — Add extraction-quality prioritization

Update the crawler ordering helper so objectives mentioning output validation, normalization, or extraction quality lift fixtures and normalization files ahead of schema-adjacent context while still excluding unrelated application code.

---

## Step 3 — Verify with focused integration coverage

Add a quality-oriented integration test that proves output and normalization files are included and prioritized correctly, then record the verification slice in `results.md`.

---

## Verification

Run the focused adapter-profile, release-surface, and crawler integration tests. Confirm output and normalization surfaces are included only when the objective points at extraction-quality work and that unrelated application code still stays out of the bundle.
