# Task: Add Phase 16 integration tests

## Metadata
- **ID:** TASK-0116
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T08 — Phase 16 integration tests
- **Packet Path:** tasks/P16-T08-TASK-0116/
- **Dependencies:** TASK-0114, TASK-0115
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add integration coverage for the full Phase 16 semantic path: provider resolution, graceful fallback, and context-selection scoring behavior across BM25, Ollama, Local, and OpenAI configurations.

## Why This Task Exists
The individual providers and command surfaces are implemented, but Phase 16 is not complete until the repo has higher-level tests proving those pieces work together under real config settings and fallback conditions.

## Scope
- add an integration test module covering provider resolution and fallback
- cover context-selection semantic metadata/scoring for BM25, Ollama, Local, and OpenAI
- keep the tests dependency-light through fake provider builders and fixture repos

## Constraints
- keep tests deterministic and independent of live network/model services
- validate graceful degradation instead of assuming optional providers are available

## Escalation Conditions
- integration behavior requires canonical changes to provider contracts
- the tests cannot reliably isolate provider availability without new test-only seams
