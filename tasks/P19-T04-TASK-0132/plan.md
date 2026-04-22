# Plan: TASK-0132

## Approach

Add a small `contrib/community_adapter_registry/` tree that mirrors the reviewed community registry repo at a template level: submission guidance, package metadata template, adapter profile template, review metadata, and a review checklist. Keep the templates aligned with the package validator and install flow so later CI and integration tasks can consume the same scaffold.

---

## Step 1 — Define the scaffold layout

Choose the minimum directory and file set needed to communicate how a reviewed community adapter submission should be packaged and reviewed.

---

## Step 2 — Add templates and guidance

Write the template files and contribution guidance so authors and maintainers can see the expected package shape and review metadata directly in repo-visible files.

---

## Step 3 — Add focused scaffold tests

Verify the scaffold files exist and that the adapter profile template can be converted into a valid profile for the current parser contract.

---

## Verification

Run direct Python execution checks for the new scaffold test file and note any environment limitation if `pytest` remains unavailable.
