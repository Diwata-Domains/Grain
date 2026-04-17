# Task: Add forge prompt show

## Metadata
- **ID:** TASK-0067
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T07
- **Packet Path:** tasks/P8-T07-TASK-0067/
- **Dependencies:** TASK-0061, TASK-0062
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add `forge prompt show` — a command that evaluates current workflow state and surfaces the recommended stable prompt entrypoint with model class, scope, and stage metadata, without making prompts the source of truth.

## Why This Task Exists
Phase 8 requires machine-readable prompt surface exposure so agents and operators can discover the correct prompt to run next without reading the prompts directory manually or embedding prompt paths in automation scripts.

## Scope
- `src/forge/services/prompt_service.py` — new service: evaluates workflow state, extracts recommended prompt, parses prompt metadata
- `src/forge/cli/prompt.py` — new `prompt` group with `show` subcommand; text and JSON output
- `src/forge/cli/__init__.py` — register `prompt_group`
- `prompts/README.md` — document the `forge prompt show` machine-readable surface
- `tests/test_prompt_show_cmd.py` — 11 tests covering service, CLI, JSON, metadata parsing, review state

## Constraints
- Read-only: must not mutate repo state
- Prompts remain execution aids; canonical authority stays in workflow_spec.md
- Prompt metadata (model class, scope, stage) is parsed from the prompt file; no hardcoded mapping

## Reviewer Focus
- Stopped workflow state still returns exit 0 (stop_reason surfaced, not error)
- JSON output has `prompt` key with all required fields per Phase 8 contract
- Prompt metadata parsing stops at the first non-metadata line after the Metadata: block
