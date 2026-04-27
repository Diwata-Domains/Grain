# Plan: TASK-0129

## Approach

Resolve Q19 in working docs first, then update canonical adapter-language docs so later validation/install tasks inherit one stable trust boundary. Keep the decision explicit: official adapters stay in-core, community adapters live in one dedicated reviewed registry repo, and local/private adapters remain repo-local and unchanged.

---

## Step 1 — Resolve the hosting model

Choose the authoritative home for community adapters and record the rationale in `open_questions.md` and `backlog.md`, including the high-level promotion path from Community to Official.

---

## Step 2 — Update canonical adapter boundaries

Extend the current official/custom adapter language into explicit official/community/local tiers so Phase 19 implementation work has stable terminology and trust expectations.

---

## Step 3 — Align phase-facing docs

Update `current_focus.md` and related working docs so the next Phase 19 tasks build against the chosen hosting/trust contract instead of the old ambiguous note.

---

## Verification

Re-read the updated docs for consistency, run a small targeted docs-adjacent test pass, and confirm `workflow next` still points at `P19-T01` until this packet is closed.
