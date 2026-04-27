# Task: Verify uv tool install compatibility and update install documentation

## Metadata
- **ID:** TASK-0087
- **Status:** done
- **Phase:** Phase 11 — Distribution and Global Install
- **Backlog:** P11-T03
- **Packet Path:** tasks/P11-T03-TASK-0087/
- **Dependencies:** TASK-0086
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Verify `uv tool install` compatibility for `grain` and update installation documentation with recommended install/verification commands.

## Why This Task Exists
Phase 11 requires confirming that `uv tool install grain` is viable and clearly documented before broader install verification and troubleshooting work.

## Scope
- Verify `uv` tool installation path using an isolated local tool environment.
- Confirm installed `grain` binary resolves and runs `grain --help` without activating project venv.
- Update README installation guidance to make `uv tool install` the recommended path and retain fallback instructions.

## Constraints
- Avoid modifying user-global tool paths during verification.
- Do not perform external publish actions.
- Do not modify canonical docs.

## Escalation Conditions
- If `uv tool install` cannot resolve package/install behavior in isolated environment, stop and record blocker details.
- If docs changes require canonical policy decisions, stop and log proposal candidate.
