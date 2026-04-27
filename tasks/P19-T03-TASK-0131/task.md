# Task: Implement grain adapter install

## Metadata
- **ID:** TASK-0131
- **Status:** done
- **Phase:** Phase 19 — Community Adapter Registry
- **Backlog:** P19-T03
- **Packet Path:** tasks/P19-T03-TASK-0131/
- **Dependencies:** TASK-0129, TASK-0130
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Implement `grain adapter install` for explicit, local-only Phase 19 community-adapter installs. The command must accept either a validated package directory or a local reviewed-registry checkout plus handle, validate the chosen package before mutation, and install the adapter into the repo-visible adapter profile file without introducing hidden state.

## Why This Task Exists
Phase 19 has a trust contract and a package validator, but users still cannot adopt a reviewed community adapter into their own repo. This task adds that install surface while keeping the install source explicit and inspectable.

## Scope
- add an install service that resolves either `--source` package dirs or `--handle` plus `--registry-root`
- validate packages before install and append installed adapter profiles into `docs/runtime/adapter_profiles.md`
- reject duplicate adapter IDs and ambiguous or unknown handles
- add focused service and CLI tests

## Constraints
- keep install local-only and deterministic; do not add network fetch behavior in this task
- community installs must stay explicit and bounded by the reviewed-registry contract from Q19
- do not widen the adapter-profile schema; reuse the existing parser and package validator

## Escalation Conditions
- if install semantics require a remote registry protocol or auth model, stop and log the gap instead of inventing one
- if Phase 19 needs a richer registry-handle contract than a local reviewed-registry checkout can support, stop and log the missing contract
