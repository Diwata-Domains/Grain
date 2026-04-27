# Plan: TASK-0140

## Approach

Patch the task execution prompt wrapper and the underlying executor prompt so they explicitly require an on-disk active packet before code changes. Then align the generated AGENTS instructions and bundled runtime guidance with the same rule, and add focused regression tests to keep the shipped wording from drifting.

---

## Step 1 — Harden execution prompts

Add explicit packet-first guardrails to the stable execution entrypoint and the detailed executor prompt so resumed sessions cannot plausibly interpret them as permission to start coding without a packet.

---

## Step 2 — Align generated agent guidance

Update generated AGENTS instructions and runtime context-loading guidance so agent-facing setup docs reinforce the same packet-first workflow rule.

---

## Step 3 — Lock the release surface with tests

Add focused tests for AGENTS generation and shipped prompt/runtime assets so the packet-first wording remains present in both repo-local and bundled copies.

---

## Verification

Run `.venv/bin/python -m pytest -q tests/test_agents_md_cmd.py tests/test_release_surface.py` and confirm the packet-first guardrail tests pass.
