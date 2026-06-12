# Results — TASK-0192

## Status
done — 2026-06-11

## Deliverable
`docs/canonical/recipe_spec.md` — recipe command group spec.

## Key Decisions

**Recipe unit:** Workflow slice = manifest + prompt template + packet scaffold template. Not a prompt alone or packet alone.

**Relationship to workflow loop:** Recipes prepare the packet and prompt, then stop. `grain workflow loop` drives the execute/review/close cycle as normal. Recipes are an entry point, not a replacement.

**Toolkit integration:** `may_call` field in recipe manifest declares sibling tool dependencies. Grain validates the contract exists before running. Agent makes the tool call (from rendered prompt instructions) — recipes don't automate inter-tool calls.

**Bundled recipes for v0.4.0:** `update-planning-doc` and `revise-meeting-notes` required; `fix-vault-links` and `update-spreadsheet-report` as candidates.

**Command surface:** `grain recipe list`, `show`, `run`, `scaffold`. `install` is a v0.4.0 candidate (depends on community registry).

## Files Changed
- `docs/canonical/recipe_spec.md` — created
- `tasks/P30-T03-TASK-0192/task.md` — status set to done
