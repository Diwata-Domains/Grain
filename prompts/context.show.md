# Show Packet Context

Display the selected context for one task packet without exporting it.

---

## Step 1 - Read Files

Read:

* docs/runtime/PROJECT_RULES.md
* docs/runtime/docs_index.md
* docs/runtime/docs_manifest.yaml
* docs/runtime/context_loading.md
* docs/runtime/agent_profiles.md
* docs/working/current_task.md
* docs/working/current_focus.md

Then read the active task folder referenced by `docs/working/current_task.md`.

At minimum, read:

* task.md
* context.md
* plan.md
* deliverable_spec.md

Read only the canonical docs referenced by the packet.

---

## Step 2 - Show the Context

Present:

* the packet identity
* the selected canonical docs
* the packet-local materials
* the reason each source is included
* any obvious gaps or blockers

Keep the output inspectable and minimal.

---

## Constraints

* do not generate code
* do not modify files directly
* do not include unrelated repository material
* do not rewrite the packet

---

## Output

Return ONLY:

1. packet identified
2. selected docs and materials
3. inclusion reasons
4. gaps or blockers

No explanation.
