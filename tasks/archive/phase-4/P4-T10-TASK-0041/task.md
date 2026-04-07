# Task: Implement forge model show

## Metadata
- **ID:** TASK-0041
- **Status:** done
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Backlog:** P4-T10
- **Packet Path:** tasks/P4-T10-TASK-0041/
- **Dependencies:** TASK-0039 (P4-T08, done)

## Objective
Implement `forge model show` so the CLI displays configured model classes and profile details in text mode and serializes model profiles in JSON mode.

## Why This Task Exists
Phase 4 requires inspectable model routing configuration. `forge model show` is the first user-facing model command and provides visibility into runtime profile definitions used by later selection/escalation commands.

## Scope
- Implement `model show` command behavior in `src/forge/cli/model.py`.
- Load and render data from `docs/runtime/agent_profiles.md` via existing model config loader.
- Add CLI tests for text output, JSON output, and missing-config failure.
- Keep `model select` and `model escalate` out of scope for this task.

## Constraints
- Preserve provider-agnostic model class abstraction in user-visible output.
- Follow existing CLI output patterns (`text` default, `json` structured output).
- Do not alter canonical docs or workflow contracts.

## Escalation Conditions
- If `agent_profiles.md` content is insufficient to render required model profile fields, stop and record config-contract ambiguity.
- If implementing `model show` requires changing `model select` or `model escalate` behavior, stop and defer to P4-T11/P4-T12.
