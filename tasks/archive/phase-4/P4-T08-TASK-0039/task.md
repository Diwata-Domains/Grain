# Task: Implement model profile configuration loader

## Metadata
- **ID:** TASK-0039
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T08
- **Packet Path:** tasks/P4-T08-TASK-0039/
- **Dependencies:** none

## Objective
Implement a runtime model profile loader that parses `docs/runtime/agent_profiles.md` into structured routing domain objects for `open_model`, `frontier_model`, and `reviewer_model`, including escalation rules.

## Why This Task Exists
Phase 4 requires model routing support. P4-T08 provides the config-loading foundation needed before selection, display, and escalation CLI behavior can be implemented in P4-T09 through P4-T12.

## Scope
- Add routing domain models in `src/forge/domain/routing.py`.
- Add markdown config loader in `src/forge/adapters/model_config.py`.
- Add loader/parser tests in `tests/test_model_config_loader.py`.
- Keep this task limited to config loading and parsing; no CLI command behavior changes.

## Constraints
- Parse existing `docs/runtime/agent_profiles.md` as the v1 source of truth (Q8).
- Keep routing provider-agnostic and class-based (`open_model`, `frontier_model`, `reviewer_model`).
- Do not introduce a new config file format in this task.

## Escalation Conditions
- If `agent_profiles.md` format cannot be parsed reliably without redefining runtime contract, stop and log a proposal instead of guessing.
- If task work drifts into CLI command contracts (`forge model show/select/escalate`), stop and defer to P4-T09+ scope.
