# Select Model Class

Resolve the model class that should be used for a workflow stage or task.

---

## Step 1 - Read Files

Read:

* docs/runtime/PROJECT_RULES.md
* docs/runtime/docs_index.md
* docs/runtime/docs_manifest.yaml
* docs/runtime/context_loading.md
* docs/runtime/agent_profiles.md
* docs/working/current_focus.md
* docs/working/current_task.md
* docs/canonical/workflow_spec.md
* docs/canonical/cli_spec.md

Then read the active task packet if one exists.

---

## Step 2 - Select the Model

Choose the best class from:

* open_model
* frontier_model
* reviewer_model

Use the simplest class that can safely handle the work.

Prefer:

* open_model for narrow or mechanical work
* frontier_model for ambiguity, coordination, or tradeoff analysis
* reviewer_model for validation and acceptance checks

---

## Step 3 - Justify the Choice

State:

* the selected class
* why it fits the work
* whether escalation is likely later
* what would cause a higher class to be required

---

## Constraints

* do not generate code
* do not modify files directly
* do not overfit to provider identity

---

## Output

Return ONLY:

1. selected model class
2. reasoning
3. escalation risk
4. fallback or higher-class trigger

No explanation.
