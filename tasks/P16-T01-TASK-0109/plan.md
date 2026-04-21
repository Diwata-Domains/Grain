# Plan: TASK-0109

## Approach

Introduce the semantic-layer types first, then wire config parsing and provider resolution around them. The resolver should be usable immediately with a deterministic local fallback, while leaving room for later tasks to add Ollama, Local, and OpenAI factories without changing the public contract.

---

## Step 1 — Define the domain contract

Add a dedicated embedding domain module with scored-candidate, provider-status, provider protocol, and resolved-provider types. This locks the contract before provider-specific implementation work begins.

---

## Step 2 — Extend manifest config parsing

Update `GrainConfig` and `load_grain_config()` to accept `ollama` as a provider and parse provider-specific model settings with sane defaults. Update runtime manifest templates so the new config surface is discoverable.

---

## Step 3 — Add resolver and focused tests

Implement a resolver service that chooses the configured provider when available and falls back deterministically to BM25 when it is not. Cover the config defaults, fallback behavior, and domain defaults with focused tests.

---

## Verification

Run targeted pytest coverage for grain config parsing and the new embedding domain/resolver tests. Confirm the default config remains stable, `ollama` is accepted, and unsupported providers fall back to the BM25 resolver path without exceptions.
