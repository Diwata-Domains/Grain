# Plan: TASK-0127

## Approach

Promote `data_adapter` from a custom hint into the official adapter-detection path with the smallest possible scanner change, then update onboarding-oriented tests so draft docs show the new adapter through normal `applicable_adapters` output.

---

## Step 1 — Update scanner adapter detection

Teach `CodebaseScanner` to treat notebook/data-file signals as `data_adapter` applicability instead of only custom-hint material.

---

## Step 2 — Preserve custom-hint boundaries

Remove the obsolete data-adapter custom hint while keeping devops and mobile custom hints unchanged.

---

## Step 3 — Add onboarding coverage

Extend scanner and onboarding-doc tests so generated drafts surface `data_adapter` through the normal adapter list and no longer rely on a data-workflow custom hint.

---

## Verification

Run focused scanner and onboarding-doc tests to confirm `data_adapter` behaves like an official adapter in adoption flows.
