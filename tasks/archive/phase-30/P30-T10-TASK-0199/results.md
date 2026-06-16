# Results — TASK-0199

## Status
done — 2026-06-11

## Deliverable
`docs/working/docs_audit_spec.md` — docs audit spec with all check definitions, command interface, and integrations.

## Key Decisions

**21 checks across 6 document types:** current_task, backlog, current_focus, open_questions, tooling_notes, change_proposals, plus structural checks for all registered docs.

**Severity model:** `error` (workflow-breaking state) and `warning` (stale/accumulation). No auto-block — audit is always advisory.

**Configurable thresholds:** `audit_thresholds` block in `docs_manifest.yaml`. Defaults apply if absent. Set to `0` to disable a check.

**Auto-fix:** Safe fixes only; `--fix` prompts per finding; `--fix --no-confirm` for agents.

**Integrations:** `grain workflow guard --check-docs`, post-checkout hook → `.grain/last_docs_audit.json`, `grain suggest --from-audit`.

## Files Changed
- `docs/working/docs_audit_spec.md` — created
- `tasks/P30-T10-TASK-0199/task.md` — status set to done
