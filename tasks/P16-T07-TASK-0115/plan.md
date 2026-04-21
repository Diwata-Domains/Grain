# Plan: TASK-0115

## Approach

Build a thin inspection service around `EmbeddingProviderResolver`, then expose it via a new `embedding` CLI group. The command should show both configured intent and actual runtime resolution so fallback cases are obvious in text and JSON output.

---

## Step 1 — Add inspection service

Create a small service helper that resolves the active provider for a repo and returns the structured resolution payload used by the CLI.

---

## Step 2 — Add CLI command

Register a new `embedding` group and implement `embedding show` with text and JSON output covering configured provider, active provider, model names, availability, and fallback details.

---

## Step 3 — Add command tests

Add command coverage that proves both text and JSON output render the expected provider-resolution fields.

---

## Verification

Run focused provider, entrypoint, import, and `embedding show` CLI tests with the local virtualenv interpreter.
