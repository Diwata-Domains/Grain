# Task: Draft canonical doc generation from scan

## Metadata
- **ID:** TASK-0096
- **Status:** done
- **Phase:** Phase 13 — Existing Project Adoption
- **Backlog:** P13-T03
- **Packet Path:** tasks/P13-T03-TASK-0096/
- **Dependencies:** TASK-0095
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** code_adapter, frontend_adapter

## Objective
Implement `OnboardDocGenerator` that consumes `ScanResult` and generates additive draft onboarding documents for existing project adoption. Generated docs must be clearly marked draft and must never overwrite existing files.

## Why This Task Exists
Phase 13 requires a first-pass draft document generation layer after scanning existing repositories. This task bridges scanner output (`P13-T02`) to editable draft docs that operators can refine before treating them as project truth.

## Scope
- Add `src/grain/services/onboard_doc_generator.py`
- Implement `OnboardDocGenerator.generate(scan, dry_run=False)` with additive behavior
- Generate drafts for:
  - `docs/canonical/product_scope.md`
  - `docs/canonical/architecture.md`
  - `docs/working/backlog.md`
  - `docs/working/open_questions.md`
- Ensure every generated doc includes a `# DRAFT` marker
- Add focused tests for generation shape, additive behavior, dry-run, and gap-driven open-question entries

## Constraints
- Additive only: existing files are skipped, not overwritten
- Generated content is draft scaffolding only; no claim of canonical authority
- No prompt updates in this task (`P13-T04`)

## Escalation Conditions
- If draft generation requires canonical schema or workflow contract changes, stop and route through `docs/working/change_proposals.md`
