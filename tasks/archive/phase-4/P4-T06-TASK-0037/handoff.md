# Handoff: P4-T06-TASK-0037

## For P4-T07 (context export)

`context show` and `context build` emit different JSON shapes for doc records:

- `context build` → full `DocumentRecord`: `id`, `path`, `layer`, `purpose`, `authority`, `editable_by_agents`, `read_when`
- `context show` → slim: `id`, `path` only

P4-T07 must pick one of these shapes as the export schema or define a new one.
Do not introduce a third divergent shape.

## Open Question (carried from TASK-0036)

`build_context_bundle` defaults `context_tags` to `{"running_tasks"}` when none are passed.
`context show` inherits this behavior. P4-T07 will too.
See `docs/working/open_questions.md` for the logged question.
