# Plan: TASK-0113

## Approach

Implement `OpenAIProvider` around the embeddings API with optional runtime client loading and API-key gating. Register it through a built-in resolver factory that falls back to BM25 when credentials or the optional SDK are unavailable.

---

## Step 1 — Add the OpenAI provider

Create `OpenAIProvider` with client initialization, embeddings API calls, and vector-similarity ranking across query and candidate texts.

---

## Step 2 — Register resolver support

Add a built-in resolver factory for `openai` that validates API-key/client availability and triggers BM25 fallback when configuration is incomplete.

---

## Step 3 — Add focused tests

Add tests for embedding-based ranking, missing API-key behavior, and built-in resolver integration.

---

## Verification

Run targeted pytest coverage for imports, grain config, the embedding resolver, and the new OpenAI provider tests.
