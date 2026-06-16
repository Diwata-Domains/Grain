# Plan: TASK-0112

## Approach

Implement `LocalProvider` around an optional sentence-transformers model loader, cache the model lazily, and use embedding similarity to rank candidates. Register the provider in the resolver through a built-in factory that falls back to BM25 when the dependency is unavailable.

---

## Step 1 — Add the local provider

Create `LocalProvider` with lazy model loading, batched encoding for query and candidate texts, and status reporting for missing optional dependencies.

---

## Step 2 — Register resolver support

Add a built-in resolver factory for `local` that validates provider availability and triggers BM25 fallback when sentence-transformers is missing.

---

## Step 3 — Add focused tests

Add tests for vector-based ranking, missing-dependency status reporting, and built-in resolver integration.

---

## Verification

Run targeted pytest coverage for imports, grain config, the embedding resolver, and the new local provider tests.
