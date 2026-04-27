# Plan: TASK-0118

## Approach

Build one service that consumes normalized candidate inputs and emits `RankedCandidate` results with explicit components for every supported signal. The service will clamp advisory inputs to a stable range, convert graph depth into a normalized score, and sort deterministically with candidate-name tie-breaking.

---

## Step 1 — Add service input and scoring helpers

Create the input dataclass and graph-distance normalization helper so callers can provide a consistent signal set without open-coded conversions.

---

## Step 2 — Build weighted ranking output

Assemble `RankingComponent` entries for graph distance, semantic similarity, authority, and packet priority, then emit ranked candidates sorted by weighted total score.

---

## Step 3 — Add focused service tests

Add tests for combined-signal ordering, deterministic tie-breaking, and clamping behavior for out-of-range advisory inputs.

---

## Verification

Run the ranking-service tests together with ranking-domain and import coverage.
