# Task: Migrate notebook ownership into data_adapter

## Metadata
- **ID:** TASK-0125
- **Status:** done
- **Phase:** Phase 18 — Data Adapter
- **Backlog:** P18-T03
- **Packet Path:** tasks/P18-T03-TASK-0125/
- **Dependencies:** TASK-0123
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none

## Objective
Move `.ipynb` primary ownership from `code_adapter` to `data_adapter` without breaking existing notebook selection and export behavior. The migration must preserve current notebook extraction paths while updating adapter hints to reflect data-science workflows as the new primary home.

## Why This Task Exists
Phase 18 defines `data_adapter` as the home for notebook-driven analysis, but the runtime adapter profiles still assign notebooks to `code_adapter`. A direct profile-only move would also break selection because `data_adapter` still inherits graph-trace requirements, so this task handles the migration and the minimum compatibility logic together.

## Scope
- move `.ipynb` file-pattern ownership and notebook-facing hints from `code_adapter` to `data_adapter`
- preserve notebook selection by exempting `data_adapter` from graph-trace requirements for now
- add focused tests proving `data_adapter` still selects and exports notebooks
- keep the migration additive and backward-compatible for existing notebook extraction behavior

## Constraints
- do not implement broader data-artifact context integration in this task
- do not change notebook extraction content rendering itself
- preserve deterministic, inspectable adapter-source selection behavior

## Escalation Conditions
- if notebook selection under `data_adapter` needs broader graph semantics rather than a narrow compatibility exemption, log the design gap before widening this slice
- if moving `.ipynb` ownership breaks existing context export behavior, stop and preserve backward compatibility first
