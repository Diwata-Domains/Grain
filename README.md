# Grain

[![PyPI](https://img.shields.io/pypi/v/grain-kit)](https://pypi.org/project/grain-kit/)
[![CI](https://github.com/Diwata-Labs/Grain/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/Diwata-Labs/Grain/actions)

**Deterministic workflow for agent CLIs.**

Grain is a workflow layer for Codex, Claude Code, and similar agent CLIs. It gives coding agents explicit task packets, minimal context, and review gates so development stays structured, inspectable, and repeatable.

It gives agents:
- task packets as the unit of execution
- file-backed workflow state
- minimal context assembly per task
- explicit execute, review, and close gates
- stable prompt entrypoints for agent-driven work

Grain does not replace coding agents.
It gives them structure.

---

## Why Grain exists

Ad hoc agent-driven development usually degrades into:
- repeated explanations
- oversized repo context
- hidden state across conversations
- context drift across sessions
- inconsistent outputs
- unclear review boundaries

Grain makes the workflow explicit:
- one task packet at a time
- only load the context the task needs
- keep state in repo files
- require explicit review before closure

Mental model:

```text
Idea -> Task Packet -> Context -> Execute -> Review -> Close
```

This is most useful when you are already working inside an agent CLI and want the agent to follow a deterministic workflow instead of an open-ended conversation.

---

## How it is used

Grain is meant to be used through an agent CLI.

The operating loop is:

```text
grain workflow next -> grain prompt show -> agent executes one step -> review -> close
```

Use Grain to determine the next legal step.
Use the agent CLI to carry it out.

---

## What Grain manages

Grain separates work into a few visible layers:

- `docs/canonical/`
  - source-of-truth project decisions
- `docs/working/`
  - backlog, current focus, open questions, proposals
- `docs/runtime/`
  - workflow rules, adapter profiles, context-loading rules
- `tasks/`
  - one folder per task packet
- `prompts/`
  - stable prompt files for your agent CLI

The workflow is file-backed and inspectable. There is no hidden daemon, database, or background service.

---

## Install

Requirements:
- Python 3.11+
- `uv` recommended, `pip` supported

Install from PyPI:

```bash
uv tool install grain-kit
```

or:

```bash
pip install grain-kit
```

For local development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify:

```bash
grain --version
```

---

## Quick start

Grain has two real entry paths today:
- start a new repo with `grain init`
- add Grain to an existing repo with `grain onboard`

In both cases, the intended operator is an agent CLI:
1. run the Grain command
2. ask Grain for the next workflow step
3. open the recommended prompt in the agent CLI
4. let the agent work inside the Grain loop

### New project

```bash
mkdir my-project && cd my-project
git init
grain init
```

That creates the baseline Grain structure:

```text
docs/canonical/
docs/working/
docs/runtime/
tasks/
prompts/
```

Then start onboarding through your agent CLI:

```bash
grain workflow next
grain prompt show
```

Open `prompts/workflow.onboard.new.md` in your agent CLI, fill in the project context section, and let the agent generate the initial docs and backlog.

After onboarding, the normal loop is:

```bash
grain workflow next
grain prompt show
```

Then run the recommended prompt in your agent CLI, review the repo changes, and continue through execute, review, and close.

### Existing project

```bash
cd your-existing-project
grain onboard
grain workflow next
grain prompt show
```

Then open `prompts/workflow.onboard.existing.md` in your agent CLI. That prompt is intended to scan the existing repo, draft the canonical docs, and identify open questions. Review those docs before treating them as authoritative.

---

## Using Grain with agent CLIs

Grain is designed to be used through an agent CLI such as Claude Code or Codex.

In practice, the agent should use Grain as the workflow layer for the repository:
- use `grain` commands to determine the next legal step
- use prompt files under `prompts/` as stable workflow entrypoints
- operate within the execute, review, and close loop
- respect explicit review and closure gates

The CLI is the delivery surface.
The product value is the workflow structure it gives the agent.

Example instruction for an agent:

```text
You have access to the Grain CLI.

Use Grain to onboard this repository and follow the workflow.
Always use Grain commands to determine the next workflow step.
Use the prompt files Grain recommends.
Respect review and closure gates before marking work complete.
```

That keeps agent-driven work:
- structured
- lower-context
- inspectable
- repeatable

## The daily loop

The practical loop is:

1. Ask Grain what the next legal action is.
2. Run the recommended prompt in your agent CLI.
3. Review the proposed work.
4. Close the task only when the packet is complete.

That is the main operating model for the app today.

Typical commands:

```bash
grain workflow next
grain prompt show
grain review check --id TASK-0001
grain task close --id TASK-0001
```

If you want Grain to execute one legal state transition and stop at gates:

```bash
grain workflow run
```

If you want repeated state-driven execution:

```bash
grain workflow loop --steps 3
```

## Onboarding flow

Onboarding is one of the most important workflows in Grain because it gives the agent the initial structure it will follow later.

For a new repo:

```bash
grain init
grain workflow next
grain prompt show
```

Then run the recommended onboarding prompt in your agent CLI.

For an existing repo:

```bash
grain onboard
grain workflow next
grain prompt show
```

Then run the recommended onboarding prompt in your agent CLI.

The onboarding goal is to establish:
- canonical docs
- working docs
- the current backlog shape
- the next valid task flow

Review onboarding output before treating it as project truth.

---

## Task packets

A task packet is the unit of execution. Each task lives in its own directory under `tasks/`.

That includes small fixes and hotfixes. Grain does not have a separate packetless patch mode today:
- if you want the change tracked by Grain, give it a packet
- if the fix is tiny, keep the packet small and use `grain task close --quick` for low-overhead closure

Packet files include:
- `task.md`
- `context.md`
- `plan.md`
- `deliverable_spec.md`
- `results.md`
- `handoff.md` when needed

Useful commands:

```bash
grain task list
grain task show --id TASK-0001
grain task prepare --id TASK-0001
grain task validate --id TASK-0001
```

To create a packet directly:

```bash
grain task create --phase 3 --task-num 4 --title "Add packet validator"
```

Example small-fix flow:

```bash
grain task create --phase 3 --task-num 5 --title "Fix CLI help typo"
grain workflow next
grain prompt show
grain task close --id TASK-0002 --quick --summary "Fixed the CLI help typo."
```

---

## Context control

Grain is built around minimal context loading instead of dumping the whole repo into every interaction.

Build or inspect the context bundle for a task:

```bash
grain context build --id TASK-0001
grain context show --id TASK-0001
grain context export --id TASK-0001
```

The context system can also include selected working docs and adapter-specific hints when relevant.

---

## Review and closure

Grain keeps review explicit.

Use:

```bash
grain review check --id TASK-0001
grain review summary --id TASK-0001
grain review handoff --id TASK-0001
grain task close --id TASK-0001
```

The goal is simple: intelligence may propose changes, but closure should be deliberate and inspectable.

---

## Adapters

Grain uses adapters to tune context selection and review focus for different types of work while keeping the workflow loop the same.

Current adapter surface includes:
- `code_adapter`
- `frontend_adapter`
- `docs_adapter`
- `spreadsheet_adapter`

Inspect adapters with:

```bash
grain adapter list
grain adapter show --id code_adapter
```

---

## Orchestration

Grain can also generate plan proposals for larger scopes without silently mutating the repo plan.

```bash
grain orchestrate scope --scope "Add authentication system"
grain orchestrate plan --scope "Add authentication system"
grain orchestrate accept --plan OP-XXXXXXXX
```

These outputs are proposals. They are meant to support sequencing, not bypass review.

---

## What Grain is not

Grain is not:
- a coding model
- a GUI project manager
- a hidden orchestration service
- a database-backed autonomy layer

It is a disciplined filesystem-first workflow layer for agent-assisted work.

---

## Troubleshooting

If `grain` is not found after install:

```bash
uv tool dir --bin
```

Add that directory to your `PATH`.

If you hit Python version issues, use Python 3.11+ and reinstall with the interpreter you intend to use.

If you want a local editable install, prefer a dedicated virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Feedback

Issues and feedback:

https://github.com/Diwata-Labs/Grain/issues
