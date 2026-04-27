# Task: Strengthen packet-first guidance in bundled prompts and agent instructions

## Metadata
- **ID:** TASK-0140
- **Status:** done
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Backlog:** P20-T06
- **Packet Path:** tasks/P20-T06-TASK-0140/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Strengthen the shipped execution prompts and generated agent instructions so resumed sessions treat packet creation or packet activation as a hard prerequisite for implementation instead of jumping from backlog context straight into code changes.

## Why This Task Exists
Field usage showed that resumed AI sessions can skip task packet creation and start implementing directly from conversational context. Phase 20 needs explicit packet-first guardrails in the bundled prompt and instruction surfaces so the on-disk packet remains the workflow authority.

## Scope
- Add packet-first guardrails to the task execution prompt surfaces.
- Add corresponding packet-first guidance to generated agent instructions and bundled runtime guidance.
- Add focused regression tests that lock the wording into shipped assets.

## Constraints
- Do not introduce hidden workflow steps; guidance must align with existing `workflow next` and `workflow run` behavior.
- Do not add Assay-specific instructions or broaden the task into general workflow redesign.

## Escalation Conditions
- If packet-first hardening requires changing task lifecycle command contracts rather than shipped prompt/instruction text, stop and treat that as a separate workflow-engine task.
