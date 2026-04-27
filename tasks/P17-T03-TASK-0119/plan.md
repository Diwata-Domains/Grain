# Plan: TASK-0119

## Approach

Keep the existing graph-assisted candidate discovery and Phase 16 semantic-provider resolution, but replace the semantic-only path ordering with the shared ranking service. The resulting bundle metadata should show both raw semantic scores and the final weighted ranking breakdown that determined source order.

---

## Step 1 — Wire ranking service into context reranking

Convert graph-derived adapter sources into `RankingCandidateInput` values using graph depth, semantic score, and packet-priority hints, then rank them through `rank_candidates()`.

---

## Step 2 — Expose score breakdown metadata

Add ranked score breakdowns to the bundle’s semantic-ranking metadata so review can explain why one source outranked another.

---

## Step 3 — Validate existing behavior

Extend the context-build tests to prove ranked ordering and component metadata are present while the Phase 16 integration suite stays green.

---

## Verification

Run context-build, ranking-service, import, and Phase 16 integration coverage with the local virtualenv interpreter.
