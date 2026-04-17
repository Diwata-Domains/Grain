# Plan: TASK-0067

## Approach

1. `prompt_service.py` — calls `evaluate_workflow_state`, extracts `recommended_prompt`, parses metadata from the prompt file via `_parse_prompt_metadata`. Returns `(CommandResult, dict|None)` payload with: `recommended_prompt`, `prompt_exists`, `model_class`, `escalation_model_class`, `scope`, `stage`, `next_action`, `stop_reason`, `blocking_reasons`, `active_phase`, `active_task_id`.

2. `prompt.py` — `prompt show` subcommand. Text output: key/value lines. JSON output: `{"prompt": payload}` nested under CommandResult. Stopped state exits 0 (consistent with `workflow next`).

3. `__init__.py` — add `from .prompt import prompt_group` and `main.add_command(prompt_group)`.

4. `prompts/README.md` — add "Machine-Readable Prompt Surface" section documenting `forge prompt show`.

5. `tests/test_prompt_show_cmd.py` — 11 tests: metadata parsing, service unit, CLI text/JSON, stopped state, review state recommendation.

## File Changes
- `src/forge/services/prompt_service.py` (new)
- `src/forge/cli/prompt.py` (new)
- `src/forge/cli/__init__.py` — two-line addition
- `prompts/README.md` — new section
- `tests/test_prompt_show_cmd.py` (new)
