# Plan: TASK-0123

## Approach

Document the `data_adapter` in the existing runtime profile format without changing parser or service behavior. Keep this slice purely contractual: define supported patterns, hints, and the metadata-only extraction boundary, then prove the contract with focused adapter-profile parsing tests.

---

## Step 1 — Update the packet and phase-facing docs

Fill the packet with the Phase 18 scope, Q18 boundary decision, and explicit non-goals. Align `current_focus.md` so the immediate goals no longer reference an unresolved extraction-boundary decision.

---

## Step 2 — Define the runtime adapter contract

Add `data_adapter` to `docs/runtime/adapter_profiles.md` with a stable profile, metadata-only file handling guidance, and an explicit note that `.ipynb` ownership migration is deferred to P18-T03.

---

## Step 3 — Add focused parser coverage

Extend adapter-profile loader tests to verify the runtime contract can represent `data_adapter` and preserve its metadata-only hints without requiring code-path changes.

---

## Verification

Run focused adapter-profile tests and inspect `grain workflow next` after the packet state is updated, confirming Phase 18 can proceed from planning into execution without reopening the contract question.
