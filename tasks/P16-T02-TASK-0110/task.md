# Task: Implement BM25Provider

## Metadata
- **ID:** TASK-0110
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T02 — Implement `BM25Provider`
- **Packet Path:** tasks/P16-T02-TASK-0110/
- **Dependencies:** TASK-0109
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Extract the resolver's internal lexical fallback into a formal `BM25Provider` implementation. This provider must be deterministic, dependency-free, and become the canonical baseline used whenever semantic enrichment resolves to the `none` provider.

## Why This Task Exists
P16-T01 defined the provider contract and fallback rules, but the lexical scorer still lives as an internal helper in the resolver. Phase 16 needs a real provider implementation that later provider tasks can be compared against and that the resolver can instantiate directly.

## Scope
- add a dedicated BM25 provider module under `src/grain/services/`
- switch resolver fallback/default behavior to use `BM25Provider`
- add focused tests for provider scoring and resolver integration

## Constraints
- keep the provider deterministic and dependency-free
- do not add provider-network integration in this task
- preserve the existing resolver contract introduced in P16-T01

## Escalation Conditions
- BM25 scoring requirements need canonical ranking-policy changes to proceed
- provider extraction would force incompatible changes to the resolved-provider contract
