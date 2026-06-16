# Plan: TASK-0110

## Approach

Promote the lexical fallback logic into a dedicated `BM25Provider` module, then swap the resolver over to use that provider rather than an embedded private class. Lock the behavior down with focused provider and resolver tests so later provider tasks can extend the resolver without changing the BM25 baseline.

---

## Step 1 — Extract the provider

Move the lexical scoring and status-reporting logic into a standalone `BM25Provider` class under `src/grain/services/`.

---

## Step 2 — Integrate the resolver

Update the resolver to instantiate `BM25Provider` for the configured `none` provider and for fallback cases when richer providers are unavailable.

---

## Step 3 — Add focused tests

Add a provider-level test file plus resolver assertions that the BM25 provider is the actual resolved implementation.

---

## Verification

Run targeted pytest coverage for the BM25 provider, embedding resolver, imports, and grain config to confirm the extracted provider preserves the existing deterministic behavior.
