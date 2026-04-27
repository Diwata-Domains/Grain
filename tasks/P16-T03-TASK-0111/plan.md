# Plan: TASK-0111

## Approach

Implement an Ollama provider that converts a query and candidate texts into embedding vectors and ranks them by cosine similarity. Integrate it into the resolver through a built-in factory that checks provider availability and falls back to BM25 when the local server is unreachable.

---

## Step 1 — Add the provider module

Create `OllamaProvider` with local HTTP requests to the Ollama embeddings endpoint, vector-similarity scoring, and a status method that reports reachability.

---

## Step 2 — Register resolver support

Add a built-in resolver factory for `ollama` that returns the provider when reachable and raises a controlled error to trigger BM25 fallback when not.

---

## Step 3 — Lock the behavior with tests

Add focused tests for ranking, unavailable-server status, and resolver integration with the built-in Ollama factory.

---

## Verification

Run targeted pytest coverage for imports, grain config, the embedding resolver, and the new Ollama provider tests.
