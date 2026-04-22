# Task: Improve onboarding and scanner detection for data workflows

## Metadata
- **ID:** TASK-0127
- **Status:** done
- **Phase:** Phase 18 — Data Adapter
- **Backlog:** P18-T05
- **Packet Path:** tasks/P18-T05-TASK-0127/
- **Dependencies:** TASK-0125
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none

## Objective
Update onboarding and repo scanning so notebook and dataset signals surface `data_adapter` as an official applicable adapter instead of only a custom-adapter hint. The scanner and generated draft docs should now represent data workflows as first-class Phase 18 onboarding paths.

## Why This Task Exists
Phase 18 already defines and wires `data_adapter`, but existing onboarding still treats data workflows as a custom-hint edge case. This task closes that mismatch so new or adopted repos can see `data_adapter` alongside the other official adapters.

## Scope
- detect `data_adapter` as an applicable adapter when notebooks or Phase 18 data files are present
- stop emitting the old custom-hint text for data workflows now that `data_adapter` is official
- update onboarding draft tests so generated docs surface `data_adapter` through `applicable_adapters`
- keep unrelated custom-adapter hints intact

## Constraints
- do not widen into adapter installation/registry work
- preserve existing behavior for devops/mobile custom-adapter hints
- keep onboarding output additive and file-backed

## Escalation Conditions
- if data workflows need a separate onboarding surface rather than `applicable_adapters`, stop and log that contract gap
- if promoting `data_adapter` to official onboarding status conflicts with runtime adapter documentation, stop and reconcile the docs first
