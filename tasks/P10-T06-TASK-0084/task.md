# Task: Replace ast/regex extraction with full tree-sitter parser coverage

## Metadata
- **ID:** TASK-0084
- **Status:** done
- **Phase:** Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph
- **Backlog:** P10-T06
- **Packet Path:** tasks/P10-T06-TASK-0084/
- **Dependencies:** TASK-0079
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Replace the structural extraction layer implementation so it uses tree-sitter parsers for supported languages instead of Python `ast` and regex fallbacks.

## Why This Task Exists
Phase 10 was reopened because the original extraction implementation did not satisfy tree-sitter requirements. This remediation aligns implementation behavior with declared architecture and backlog contract.

## Scope
- Rewrite `structural_intelligence_service.py` to use tree-sitter parser bindings.
- Update packaging dependencies to include language parser support package.
- Update structural extraction tests to assert `parser == "tree-sitter"` for supported fixtures.

## Constraints
- Deterministic and local-only behavior.
- No regex fallback path for supported grammars.
- Return `parser = "none"` only when parser support is unavailable.

## Escalation Conditions
- If required parser dependencies are unavailable in runtime, stop and document explicit blocker details.
- If tree-sitter behavior changes graph/context/orchestration contracts, stop and capture regression details.
