# Escalate Model Class

Determine whether a task or workflow stage should move from one model class to another.

---

## Step 1 - Read Files

Read:

* docs/runtime/PROJECT_RULES.md
* docs/runtime/docs_index.md
* docs/runtime/docs_manifest.yaml
* docs/runtime/agent_profiles.md
* docs/working/current_focus.md
* docs/working/current_task.md
* any canonical docs from `docs/runtime/docs_manifest.yaml` that are relevant to the escalation decision

Then read the active task packet if one exists.

---

## Step 2 - Evaluate Escalation

Check whether the current work has:

* ambiguity that blocks progress
* cross-file coordination needs
* architecture or workflow tradeoffs
* review or acceptance requirements
* a risk level that exceeds the current class

---

## Step 3 - Recommend the Move

State:

* whether escalation is needed
* the source class
* the target class
* the reason for the escalation or why it should stay put
* any next step required after escalation

---

## Constraints

* do not generate code
* do not modify files directly
* do not escalate without a clear reason

---

## Output

Return ONLY:

1. escalation decision
2. source class
3. target class
4. reasoning
5. next step

No explanation.
