# Plan: TASK-0114

## Approach

Keep the existing graph-assisted candidate discovery intact, then layer semantic ranking on top as a deterministic reorder step. The context service will read the task objective, resolve the active provider with normal BM25 fallback rules, rerank only graph-traced adapter candidates, and publish enough metadata to explain what happened during review.

---

## Step 1 — Add semantic reranking hooks

Extend `build_context_bundle()` so it can resolve the configured embedding provider, extract a semantic query from `task.md`, and rerank graph-derived adapter candidates without altering the trace map or adding new files.

---

## Step 2 — Record semantic metadata

Capture the configured/active provider, fallback state, provider status, and per-source scores in bundle metadata so CLI output and later tests can inspect the semantic layer.

---

## Step 3 — Add focused tests

Add a context-build test that injects a fake semantic resolver/provider and proves traced adapter sources are reranked semantically while preserving deterministic output shape.

---

## Verification

Run focused context-service tests with the local virtualenv interpreter to verify bundle assembly, semantic reranking, and command output remain green.
