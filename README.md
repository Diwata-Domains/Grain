# Forge

Forge is a CLI-first workflow system for structured AI-assisted software development.

It gives you:
- canonical docs as source of truth
- working docs for sequencing and planning
- task packets as the execution unit
- explicit review and close loops
- minimal-context execution instead of broad repo dumping

Forge is not a coding model by itself.
It is the workflow and file system that external agent CLIs operate against.

---

## Who It Is For

Forge is for developers and technical operators who:
- use agent CLIs such as Codex or Claude Code
- want inspectable markdown files instead of opaque orchestration
- want scoped task execution, review, and closure
- want less context drift and lower token waste than ad hoc prompting

---

## Core Idea

Forge separates work into layers:

- `docs/canonical/`
  - source-of-truth decisions
- `docs/working/`
  - current plan, backlog, questions, proposals, metrics
- `docs/runtime/`
  - execution rules, manifest, context-loading rules, model profiles
- `tasks/`
  - one packet per task
- `prompts/`
  - stable workflow entrypoints for agent CLIs

---

## Installation

Current install path is local Python package install from source.

Requirements:
- Python 3.11+
- `pip`

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify:

```bash
forge --help
```

This installs the `forge` CLI entrypoint defined in [`pyproject.toml`](/Users/barbaricum/ai-build-toolkit/pyproject.toml).

Current state:
- supported now: local editable install
- not yet productized: PyPI, Homebrew, standalone installer, global bootstrap flow

If you are using an agent CLI, install Forge first, then run the onboarding/start prompts from `prompts/`.

---

## Should You Use Forge For Your Machine?

Yes, sometimes.

Good use cases:
- managing dotfiles or local automation as a project
- maintaining workstation setup scripts
- organizing home-lab, local tooling, or machine-admin workflows
- treating your local environment as an inspectable system with tasks, review, and change history

Bad default:
- treating your entire home directory or whole machine as one Forge project

Better pattern:
- create a dedicated repo such as:
  - `local-ops`
  - `machine-admin`
  - `personal-systems`
- use Forge inside that repo

Reason:
- keeps scope bounded
- keeps context smaller
- keeps tasks coherent
- avoids mixing unrelated files and projects into one authority tree

---

## How New Users Should Start

Use the `README` as the entrypoint and the prompts as the workflow engine.

There are two starting modes:

1. new project
2. existing project

### New Project

1. create or enter the project repo
2. run `forge init`
3. open [`prompts/workflow.init.md`](/Users/barbaricum/ai-build-toolkit/prompts/workflow.init.md)
4. fill in the `Project Context`
5. paste that prompt into your agent CLI
6. let the agent generate the initial docs, manifest, backlog, and open questions
7. review those generated docs before treating canonical content as approved

After onboarding, use the normal loop:

1. `prompts/task.plan.next.md` only when a task must be selected or split
2. `prompts/task.execute.md`
3. `prompts/task.review.md`
4. `prompts/task.close.md`

### Existing Project

The full adoption flow is planned but not fully productized yet.

Current practical path:

1. run `forge init` inside the existing repo
2. use [`prompts/workflow.init.md`](/Users/barbaricum/ai-build-toolkit/prompts/workflow.init.md) as a temporary onboarding starter, but describe the project as an existing system
3. review generated docs carefully
4. treat generated canonical docs as draft until confirmed

Planned dedicated path:
- Phase 7 onboarding flow for existing project adoption

---

## Agent CLI Usage

Forge is designed to be used from an agent CLI.

The basic pattern is:

1. run the Forge CLI when filesystem scaffolding or validation is needed
2. run a prompt from `prompts/`
3. let the agent update the repo files
4. continue through the structured loop

### Recommended Stable Prompt Surface

Phase planning:
- [`prompts/phase.plan.next.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.plan.next.md)
- [`prompts/phase.replan.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.replan.md)
- [`prompts/phase.review.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.review.md)
- [`prompts/phase.review_and_close.md`](/Users/barbaricum/ai-build-toolkit/prompts/phase.review_and_close.md)

Task planning and execution:
- [`prompts/task.plan.next.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.plan.next.md)
- [`prompts/task.execute.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.execute.md)
- [`prompts/task.review.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.review.md)
- [`prompts/task.close.md`](/Users/barbaricum/ai-build-toolkit/prompts/task.close.md)

Project bootstrap:
- [`prompts/workflow.init.md`](/Users/barbaricum/ai-build-toolkit/prompts/workflow.init.md)

### Recommended Daily Loop

Use this loop continuously inside the active phase:

1. `task.plan.next`
   - only when the next task must be selected, split, or added
2. `task.execute`
3. `task.review`
4. `task.close`

Do not run `task.plan.next` every time if a ready task already exists.

### Recommended Planning Loop

Use this less often:

1. `phase.plan.next`
2. `phase.replan` only when the phase shape is wrong
3. `phase.review` or `phase.review_and_close` at phase boundaries

---

## Customization

Forge is meant to be customized to the project it is managing.

Users should customize:
- canonical docs for the project domain and scope
- working docs for sequencing, backlog, and open questions
- adapter selection and adapter profiles
- model strategy and agent preferences
- onboarding outputs for new or existing projects

Users should try to keep stable:
- the core workflow loop
  - plan
  - execute
  - review
  - close
- file-backed workflow state
- authority boundaries between canonical, working, runtime, and task layers
- explicit review and change-proposal gates

Good customization:
- adapt Forge to Python, Rust, React, docs, spreadsheets, local-ops, or mixed projects
- add project-specific constraints, risks, adapters, and backlog structure

Bad customization:
- silently bypass review
- hide state outside the repo
- collapse canonical and working docs into one layer
- make every project invent its own incompatible workflow loop

In short:
- customize the project model
- keep the workflow model disciplined

---

## Minimal CLI Flow

Common commands:

```bash
forge init
forge docs validate
forge task create --title "..."
forge task list
forge task show --id TASK-####
forge task close --id TASK-####
```

In normal Forge usage, the prompts drive most of the workflow and the CLI handles scaffolding, validation, and command surfaces.

---

## Important Rules

- do not treat prompts as canonical truth
- do not edit canonical docs silently
- do not execute multiple unrelated tasks in one packet
- do not let review and close perform backlog planning implicitly
- if prompt or workflow-contract docs change mid-conversation, restart the relevant agent conversation

See:
- [`docs/runtime/PROJECT_RULES.md`](/Users/barbaricum/ai-build-toolkit/docs/runtime/PROJECT_RULES.md)
- [`docs/runtime/docs_manifest.yaml`](/Users/barbaricum/ai-build-toolkit/docs/runtime/docs_manifest.yaml)

---

## Current Product State

Current repo status:
- v1 core workflow is complete
- current active work is v2 Phase 6: adapter system foundation
- onboarding for new and existing projects is planned as a later v2 phase

See:
- [`docs/working/current_focus.md`](/Users/barbaricum/ai-build-toolkit/docs/working/current_focus.md)
- [`docs/working/implementation_plan.md`](/Users/barbaricum/ai-build-toolkit/docs/working/implementation_plan.md)
- [`docs/working/v2_onboarding.md`](/Users/barbaricum/ai-build-toolkit/docs/working/v2_onboarding.md)

---

## Short Recommendation

For future users, the intended startup experience should be:

1. read this `README`
2. choose:
   - new project
   - existing project
3. run `forge init`
4. run the onboarding prompt in an agent CLI
5. move into the standard task loop

That is the cleanest human entrypoint without overloading the `README` itself with the entire onboarding conversation.
