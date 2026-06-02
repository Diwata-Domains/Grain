# Plan: TASK-0159

## Approach

Keep the first MCP slice narrow and local. Add a small stdio server that supports the minimum desktop wrapper handshake and routes a read-oriented tool set to existing Grain services, then expose a CLI manifest command for local client configuration. Verify the scaffold through focused protocol and CLI tests instead of expanding into full desktop execution behavior.

---

## Step 1 — MCP service scaffold

Add the stdio request/response loop, tool catalog, and shared action routing over existing workflow, prompt, review, and office-review inspection services. Keep this deterministic and local-first.

---

## Step 2 — CLI surface

Add `grain mcp manifest` and `grain mcp serve` so desktop clients have a simple local config path and a canonical process entrypoint.

---

## Step 3 — Focused verification

Add tests that prove the MCP handshake, tool listing, routed workflow/prompt calls, and manifest output work without introducing hidden state or CLI drift.

---

## Verification

Run focused MCP and CLI tests and confirm the scaffold only exposes the intended read-oriented tool surface over stdio.
