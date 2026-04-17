# Task: `docs_adapter` Word/docx extraction service

## Metadata
- **ID:** TASK-0100
- **Status:** done
- **Phase:** Phase 14 — Document and Spreadsheet Adapters
- **Backlog:** P14-T02
- **Packet Path:** tasks/P14-T02-TASK-0100/
- **Dependencies:** TASK-0099
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Implement `DocsExtractor` that reads `.docx` files using `python-docx` and returns structured text content (headings, paragraphs, tables). Extend the `docs_adapter` profile in `adapter_profiles.md` to cover `.docx` in addition to existing `.md` file patterns. Add `python-docx>=1.1` to project dependencies.

## Why This Task Exists
Word documents are a common artifact in any product or project context — specs, briefs, requirements, meeting notes. Grain must be able to include `.docx` content in context bundles the same way it includes markdown files.

## Scope
- Implement `src/grain/services/docs_extractor.py`:
  - `DocsExtractor` class with `extract(path: Path) -> str` method
  - `.docx`: use `python-docx` — extract heading text (with level prefix e.g. `## Heading`), paragraph text, and table cells as pipe-delimited rows
  - Returns graceful warning string on any extraction error — never raises
- Extend `docs_adapter` profile in `docs/runtime/adapter_profiles.md`:
  - Add `.docx` to `relevant_file_patterns` alongside existing `.md`
  - Update context priority rules to cover both file types
- Wire `.docx` into context assembly to invoke `DocsExtractor.extract()`
- Add `python-docx>=1.1` to `dependencies` in `pyproject.toml`
- Tests: ≥ 8 (create `.docx` fixtures in-memory using `python-docx` in test setup)

## Constraints
- Extraction is read-only — never modify source `.docx` files
- Tables: extract cell text only — do not try to preserve table layout
- Images/embedded objects: skip silently — text content only
- Synthetic test fixtures created in-memory via `python-docx`, not committed as binary files

## Escalation Conditions
- If `docs_adapter` profile changes require architectural decisions (e.g. conflicting `.md` handling), stop and log a change proposal
