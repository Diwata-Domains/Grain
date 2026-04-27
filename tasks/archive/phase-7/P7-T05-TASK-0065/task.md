# Task: Add starter task-packet bootstrap for the onboarding path

## Metadata
- **ID:** TASK-0065
- **Status:** done
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Backlog:** P7-T05
- **Packet Path:** tasks/P7-T05-TASK-0065/
- **Dependencies:** TASK-0063, TASK-0064
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Add an optional `--bootstrap` flag to `forge init` that creates one starter task packet (P1-T01) and initializes `docs/working/current_task.md` as `ready` after scaffolding. When a validated `primary_adapter` is also set, it is written into the starter task.md. Dry-run mode reports the intended actions without writing.

## Why This Task Exists
Phase 7 requires onboarding to reduce time-to-first-execution. After running `forge init --bootstrap`, a new project has a ready-to-use task packet and a current_task pointer so the executor can start immediately.

## Scope
- `--bootstrap` flag on `forge init`
- `_run_bootstrap()` service helper that creates the starter packet and writes current_task.md
- `_patch_task_adapter()` helper that sets Primary Adapter in the starter task.md when a validated adapter was selected
- `bootstrapped_task_id` field on `InitResult` and `CommandResult`
- Dry-run: reports predicted task ID and files without writing
- 6 new service tests, 2 new CLI tests

## Constraints
- Additive-only: existing init behavior unchanged when `--bootstrap` is not passed
- Bootstrap always uses phase=1, task_num=1 for the starter packet
- If `create_packet_directory` fails, record the error as a warning and continue
- No canonical doc changes required

## Escalation Conditions
- If starter packet metadata contract requires canonical changes, stop and route through change_proposals.md

## Reviewer Focus
- Verify `current_task.md` is written with `Status: ready` (not `in_progress`)
- Verify `--bootstrap` with `--dry-run` does not write anything
- Verify adapter patching only applies when `primary_adapter` was successfully validated
