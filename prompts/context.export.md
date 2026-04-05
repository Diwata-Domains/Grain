# Export Packet Context

Export a packet context bundle for use by an external tool or agent.

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

Read only the canonical docs needed by the packet scope.

---

## Step 2 - Build the Export

Produce an export-ready bundle that includes:

* packet identity
* source list
* short purpose for each source
* required packet-local materials
* any blockers or missing inputs

Prefer a single markdown bundle with a clear metadata header unless a structured export is explicitly required.

---

## Step 3 - Check Export Fitness

Confirm the bundle is:

* minimal
* complete enough for execution
* free of unrelated context
* aligned with packet scope

If the bundle cannot be exported cleanly, state why.

---

## Constraints

* do not generate code
* do not modify files directly
* do not include unrelated repository content
* do not invent missing context

---

## Output

Return ONLY:

1. packet identified
2. export bundle summary
3. source list
4. blockers or missing inputs
5. export readiness

No explanation.
