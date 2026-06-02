# Task Execute

Stable task execution entrypoint.

Metadata:
- scope: task
- stage: execute
- recommended_model_class: open_model
- escalation_model_class: frontier_model

## Instructions

Read the file `prompts/tasks.next_and_implement.md` and follow all steps in it exactly.

Treat this prompt as packet-first workflow execution, not permission to start coding immediately.
Before any code change, confirm there is an active task packet on disk or generate one through the workflow steps in `prompts/tasks.next_and_implement.md`.
If the workflow state still requires task planning or no packet exists yet, stop and route through the packet-creation path before implementation.
If the conversation has drifted and you are no longer sure the packet, workflow state, or verification state on disk matches the chat, stop and return to `grain workflow next --format json` before continuing.

Do not summarize or abbreviate the steps. Execute the full prompt.
