# Plan: TASK-0161

## Approach

Keep this slice thin and operator-facing. First, identify the minimum guidance and helper surface needed to make Codex/CLI usage explicit now that `grain mcp` exists. Then implement only the smallest repo changes that clarify the desktop/tool-execution path without inventing a parallel control plane.

---

## Step 1 — Codex-facing surface audit

Review the current README, runtime guidance, and command set to see what is still ambiguous for a Codex-style user invoking Grain directly through the CLI.

---

## Step 2 — Guidance and helper implementation

Add the missing documentation and any justifiable helper surface so the CLI-first path is explicit and easy to adopt in Codex or similar tool-execution environments.

---

## Step 3 — Verification and packet closeout

Lock the new guidance/helpers with focused tests where applicable, then record the exact verification slice in `results.md` and prepare the review bundle.

---

## Verification

Run a focused test slice covering any helper commands added plus existing CLI contract tests touched by the changes. Confirm the documentation matches the actual Codex/CLI operating path.
