# Plan: TASK-0124

## Approach

Follow the existing extractor pattern: one service class with suffix dispatch, deterministic markdown-like output, and graceful degradation for missing readers. Keep schema hints shallow and optional, and test them with local fakes rather than requiring real binary dependencies in the test suite.

---

## Step 1 — Implement the extractor surface

Add a new data-artifact extractor service covering dataset and model artifact suffixes, shared metadata rendering, and optional-reader hooks for cheap schema hints.

---

## Step 2 — Document dependency posture

Update `pyproject.toml` so optional Phase 18 reader libraries are discoverable without turning them into mandatory runtime requirements for every Grain install.

---

## Step 3 — Add focused tests

Cover unsupported types, generic metadata rendering, graceful degradation when optional readers are missing, and fake-reader schema hints for at least one data format family.

---

## Verification

Run focused extractor tests and any adjacent adapter-profile/import tests needed to prove the new service is stable without touching later context-integration paths.
