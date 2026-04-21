# Plan: TASK-0116

## Approach

Build one integration test module that configures temporary repos with different `grain.embedding_provider` values, then verifies both provider resolution and context-selection semantic metadata using deterministic fake providers for optional backends.

---

## Step 1 — Add provider-resolution coverage

Test the service-level resolver path for default BM25 behavior, graceful fallback from an unavailable provider, and successful resolution for Local and OpenAI when fake providers are injected.

---

## Step 2 — Add context-selection coverage

Exercise `build_context_bundle()` against fixture repos so Phase 16 proves semantic metadata and candidate reranking behavior across BM25, Ollama, Local, and OpenAI configurations.

---

## Step 3 — Run targeted semantic suites

Re-run the provider, context, CLI, and new integration tests together to catch regressions across the full Phase 16 surface.

---

## Verification

Run the new integration module plus the surrounding provider/context/CLI tests with the local virtualenv interpreter and confirm all targeted coverage passes.
