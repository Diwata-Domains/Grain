# Plan: TASK-0134

## Approach

Add one focused Phase 19 integration test module that assembles a reviewed-registry style submission in a temporary repo, validates it, installs it by local registry handle, and then checks that the scaffold, author guide, and CI workflow all point at the same contract. Keep the file count low and the assertions end-to-end.

---

## Step 1 — Cover validation and install end-to-end

Build one temporary reviewed-registry submission using the Phase 19 scaffold shape, then validate and install it through the real service and CLI entrypoints.

---

## Step 2 — Cover contract alignment artifacts

Assert the scaffold templates, author guide, and CI workflow reference the same file names and validation flow so the phase closes on one visible contract.

---

## Step 3 — Verify directly

Run the integration module through direct Python execution and record the environment limitation if `pytest` is still unavailable.

---

## Verification

Run direct Python execution of the new Phase 19 integration module and note the result in `results.md`.
