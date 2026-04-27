# Task: Make upgrade safer for customized repo doc layouts

## Metadata
- **ID:** TASK-0139
- **Status:** done
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Backlog:** P20-T05
- **Packet Path:** tasks/P20-T05-TASK-0139/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Harden `grain upgrade` so customized managed files are detected and skipped by default, with explicit guidance that operators should use interactive or diff mode to review those changes instead of silently overwriting repo-specific edits.

## Why This Task Exists
Field usage from a Grain-managed CRM repo showed that `grain upgrade --diff` can make customized layouts look like they should be reset back to Grain defaults. Phase 20 needs upgrade behavior that is safer and less misleading for repos with intentional doc customization.

## Scope
- Detect customized Grain-managed files during upgrade evaluation.
- Skip overwriting customized files by default in non-interactive mode and surface bounded guidance in CLI output.
- Add focused service and CLI coverage for the new contract.

## Constraints
- Keep `grain upgrade --interactive` available for explicit human-approved application of bundled changes.
- Do not broaden this task into user-owned file ownership changes or non-doc upgrade surfaces.

## Escalation Conditions
- If the current upgrade ownership contract is too broad to distinguish managed customization from true user-owned files, stop and narrow the change to explicit skip-and-guide behavior rather than redesigning upgrade ownership.
