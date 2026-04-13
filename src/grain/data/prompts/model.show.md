# Show Model Routing

Display the configured model classes and the routing rules that apply to them.

---

## Step 1 - Read Files

Read:

* docs/runtime/PROJECT_RULES.md
* docs/runtime/docs_index.md
* docs/runtime/docs_manifest.yaml
* docs/runtime/agent_profiles.md
* docs/canonical/workflow_spec.md
* docs/canonical/cli_spec.md

Read working docs only if needed to explain the current phase or active task.

---

## Step 2 - Summarize Model Routing

Show:

* model classes
* intended use for each class
* escalation triggers
* current preferred mapping
* any gaps or ambiguities in routing rules

Keep the result focused on workflow use, not provider branding.

---

## Constraints

* do not generate code
* do not modify files directly
* do not infer provider-specific behavior unless documented

---

## Output

Return ONLY:

1. model classes
2. intended use
3. escalation triggers
4. ambiguities or gaps

No explanation.
