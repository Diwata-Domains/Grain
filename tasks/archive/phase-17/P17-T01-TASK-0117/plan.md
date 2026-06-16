# Plan: TASK-0117

## Approach

Add a small ranking domain module that mirrors the style of the existing embedding contracts: explicit dataclasses, stable defaults, and helper functions with focused tests. The goal is to lock down how score components and weighted results are represented before building any ranking service logic.

---

## Step 1 — Add ranking contracts

Create ranking dataclasses for score components, ranked candidates, and configured weights, plus constants for supported signal IDs and default weights.

---

## Step 2 — Add authority scoring helper

Expose a normalized authority-scoring helper and mapping so later ranking code can incorporate document authority without inventing a new hidden ordering.

---

## Step 3 — Add domain tests

Add focused tests for default weight totals, component lookup, distinct metadata defaults, and authority-score ordering.

---

## Verification

Run the ranking-domain tests plus import coverage to confirm the new contracts are stable and correctly exported.
