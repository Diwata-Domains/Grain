# Grain Recipe Spec

**Status:** Canonical — locked in v0.4.0 planning (Phase 30, TASK-0192)

---

## 1. What a Recipe Is

A recipe is a named, parameterized workflow slice. It is the full execute → review → close pattern configured for a specific, repeatable use case.

A recipe is not:
- A prompt template alone (that belongs in `prompts/`)
- A packet template alone (that is a scaffold, not a recipe)
- A script or shell command (recipes work through Grain's existing workflow engine)

A recipe consists of:
1. A **recipe manifest** (`recipe.yaml`) — name, description, parameters, workflow configuration
2. A **prompt template** (`prompt.md`) — the agent instruction for the execute step, with `{{parameter}}` interpolation
3. A **packet scaffold template** (`task_template.md`) — the task.md structure that gets created when the recipe runs

When a recipe runs, Grain:
1. Prompts the operator for any required parameters
2. Creates a task packet from the scaffold template
3. Assembles context using the recipe's configured adapter scope
4. Surfaces the interpolated prompt for the execute step
5. Gates at review and close as normal

Recipes do not bypass the workflow engine. They are a configured entry point into the normal packet/workflow lifecycle.

---

## 2. Recipe File Structure

Recipes live in `docs/recipes/` within a Grain workspace. Each recipe is a directory:

```
docs/recipes/
  update-planning-doc/
    recipe.yaml
    prompt.md
    task_template.md
  revise-meeting-notes/
    recipe.yaml
    prompt.md
    task_template.md
  fix-vault-links/
    recipe.yaml
    prompt.md
    task_template.md
```

### 2.1 `recipe.yaml`

```yaml
name: update-planning-doc
version: "1.0"
description: "Update a planning or PRD document from source inputs"
category: docs              # docs | code | data | review | office | vault | custom
author: grain               # grain (bundled) | local | <registry-handle>

parameters:
  - id: target_doc
    label: "Target document path"
    description: "Path to the doc being updated, relative to workspace root"
    required: true
    type: path
  - id: source_inputs
    label: "Source input paths (comma-separated)"
    description: "Paths to source materials driving the update"
    required: true
    type: path_list
  - id: update_scope
    label: "Scope of changes"
    description: "What to update: summary, sections, full rewrite"
    required: false
    default: "sections"
    type: string

workflow:
  adapter_scope: docs           # which adapter profile scopes context assembly
  write_mode: propose           # propose | apply — default propose; apply requires graduation
  review_required: true
  close_policy: requires_review_pass

toolkit:
  may_call: []                  # sibling tool IDs this recipe may invoke; empty = Grain only
```

### 2.2 `prompt.md`

A Jinja2-style template (Grain uses a minimal `{{var}}` substitution — no control flow):

```markdown
# Recipe: Update Planning Document

Target: {{target_doc}}
Source inputs: {{source_inputs}}
Update scope: {{update_scope}}

## Instructions

Review the source inputs listed above and update `{{target_doc}}` accordingly.
Focus on `{{update_scope}}` changes. Do not rewrite sections not covered by the source inputs.

After updating, write a change summary in the review bundle covering:
- Which sections changed and why
- What source input drove each change
- Any residual uncertainty or content that may need human review
```

### 2.3 `task_template.md`

A task.md scaffold with `{{parameter}}` slots:

```markdown
# Task: Update {{target_doc}} from source inputs

## Metadata
- **ID:** {{task_id}}
- **Status:** in_progress
- **Phase:** {{active_phase}}
- **Recipe:** update-planning-doc
- **Recipe-Parameters:**
  - target_doc: {{target_doc}}
  - source_inputs: {{source_inputs}}
  - update_scope: {{update_scope}}

## Objective
Update `{{target_doc}}` based on the provided source inputs, scoped to `{{update_scope}}`.

## Deliverable
Updated `{{target_doc}}` with a review bundle documenting changes.
```

---

## 3. Command Interface

### `grain recipe list`

```
grain recipe list
grain recipe list --category docs
grain recipe list --source bundled|local|all
grain recipe list --format json
```

Discovers recipes in:
1. Grain's bundled recipe library (shipped with the package)
2. Workspace-local `docs/recipes/`
3. Installed community recipes (from `grain recipe install`, v0.4.0 candidate)

Output: table of name, category, description, source, version.

### `grain recipe show <name>`

Shows full recipe details: parameters, workflow config, toolkit dependencies, prompt template preview.

### `grain recipe run <name>`

```
grain recipe run <name>
grain recipe run <name> --param target_doc=docs/canonical/architecture.md
grain recipe run <name> --dry-run
grain recipe run <name> --format json
```

Execution flow:
1. Validate that `<name>` resolves to a recipe (bundled or local)
2. Collect required parameters: CLI `--param` flags first; interactive prompt for missing required params
3. Validate parameter types (path existence for `path` type, etc.)
4. Check workflow preconditions: no other `in_progress` task in the active phase (unless `--force`)
5. Create task packet from `task_template.md` with parameters interpolated
6. Set `current_task.md` to the new packet
7. Assemble context using `adapter_scope` from recipe manifest
8. Render prompt from `prompt.md` with parameters interpolated
9. Output the rendered prompt and packet path — the operator runs the prompt in their agent

After execution, the normal `grain workflow loop` or `grain task review` / `grain task close` flow applies. Recipes do not automate the execute step — they prepare everything up to it.

`--dry-run` performs all validation steps and shows what would happen (parameter collection, packet that would be created, context sources) without creating any files.

### `grain recipe scaffold <name>`

```
grain recipe scaffold <name>
grain recipe scaffold <name> --category docs
grain recipe scaffold <name> --from <existing-recipe>
```

Creates a new recipe directory at `docs/recipes/<name>/` with a starter `recipe.yaml`, `prompt.md`, and `task_template.md`. If `--from <existing-recipe>` is given, copies that recipe as the starting point.

### `grain recipe install <handle>` *(candidate — v0.4.0 if community registry ships)*

Installs a recipe from the community adapter registry. Requires the community registry to be available (Phase 19 prerequisite).

---

## 4. Relationship to `grain workflow loop`

Recipes and `grain workflow loop` are complementary, not competing:

- `grain recipe run` **prepares** the packet and prompt, then stops — it hands off to the agent
- `grain workflow loop` **drives** the execute → review → close cycle once a packet is open
- A recipe-created task is a normal task packet; `grain workflow loop` drives it identically to a manually-created task

Typical recipe workflow:
```
grain recipe run update-planning-doc --param target_doc=docs/canonical/architecture.md
→ creates TASK-0199 packet, renders prompt, outputs packet path

[operator runs the rendered prompt in their agent CLI]

grain workflow next
→ routes to task_review (execution artifacts exist)

grain task review
→ review gate

grain task close
→ packet closes, backlog updated
```

Recipes do not require `grain workflow loop`. They work equally well with manual `grain workflow next` → execute → review → close steps.

---

## 5. Relationship to the Toolkit Contract

A recipe may call sibling tools during its execute step if the recipe's `toolkit.may_call` list is non-empty. This is opt-in and declared explicitly — recipes that don't need sibling tools leave `may_call` empty.

When a recipe declares a sibling tool call:
1. Grain validates that the sibling tool's `toolkit_contract.yaml` is present and the required capability is satisfied
2. The rendered prompt includes the call instructions (e.g., "After updating the document, call `grain verify submit` with the capture path")
3. The sibling tool result flows back through the normal `grain verify ingest` path

Recipes do not automate inter-tool calls. They include the call instructions in the prompt, and the agent executing the recipe step makes the call. This keeps recipes agent-agnostic.

---

## 6. Bundled Recipes — Initial Set

Grain v0.4.0 ships with at least two bundled recipes drawn from the v0.3.0 recipe targets:

| Name | Category | Description |
|------|----------|-------------|
| `update-planning-doc` | docs | Update a PRD or planning doc from source inputs |
| `revise-meeting-notes` | docs | Structure or expand raw meeting notes into a canonical format |

Additional bundled recipes are candidates for v0.4.0:

| Name | Category | Description |
|------|----------|-------------|
| `fix-vault-links` | vault | Repair broken Obsidian wiki-links and metadata drift |
| `update-spreadsheet-report` | office | Update a tracked spreadsheet report from new source data |

Bundled recipe count is not a hard v0.4.0 requirement. Two shipped and working is sufficient. Community-contributed recipes follow after Phase 19's community adapter registry is active.

---

## 7. Design Constraints Enforced

- **No hidden state:** all recipe execution artifacts are written to the task packet — nothing in `.grain/` or temp directories
- **No bypass of workflow gates:** recipe-created packets go through normal review and close gates; no `--skip-review` flag
- **Traceable:** the packet's `task.md` includes a `Recipe:` metadata field so the recipe origin is always visible
- **Agent-agnostic:** the rendered prompt is plain markdown; no agent-specific syntax is emitted by the recipe engine
- **Backwards-compatible:** workspaces without a `docs/recipes/` directory are unaffected; `grain recipe list` shows only bundled recipes
