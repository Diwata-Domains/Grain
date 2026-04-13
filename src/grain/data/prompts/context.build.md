# Build Packet Context

Assemble the smallest valid execution context for one task packet.

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
* docs/working/backlog.md if needed for sequencing

Then read the active task folder referenced by `docs/working/current_task.md`.

At minimum, read:

* task.md
* context.md
* plan.md
* deliverable_spec.md

Read only the canonical docs referenced by the packet or required by its scope.

---

## Step 2 - Assemble Context

Select only the sources needed to execute the packet safely.

Include:

* the packet itself
* the minimum relevant canonical docs
* only the working docs needed to resolve sequencing or blockers
* only the packet-local materials that affect execution

Exclude:

* unrelated canonical docs
* unrelated working docs
* future-phase material
* broad repo history

---

## Step 3 - Assess Context Quality

Check whether the selected context is sufficient for:

* implementation
* review
* handoff to an external coding agent

If context is insufficient, name the missing artifact or blocker.

---

## Constraints

* do not generate code
* do not modify files directly
* do not load the full repo
* do not include unrelated docs

---

## Output

Return ONLY:

1. packet identified
2. selected sources
3. excluded sources with reasons
4. blockers or missing context
5. readiness for execution

No explanation.
