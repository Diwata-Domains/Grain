# Grain

Grain is a CLI-first workflow system for structured AI-assisted software development.

It gives you:
- canonical docs as source of truth
- working docs for sequencing and planning
- task packets as the execution unit
- explicit review and close loops
- minimal-context execution instead of broad repo dumping
- more useful work per agent context window by reducing drift, retries, and unnecessary rereads

Grain is not a coding model by itself.
It is the workflow and file system that external agent CLIs operate against.
It exists in part to help agent-CLI users avoid burning through token windows on broad, repetitive, underspecified conversations.

---

## Who It Is For

Grain is for developers and technical operators who:
- use agent CLIs such as Codex or Claude Code
- want inspectable markdown files instead of opaque orchestration
- want scoped task execution, review, and closure
- want less context drift and lower token waste than ad hoc prompting
- regularly hit context or usage limits before useful work is complete

---

## Core Idea

Grain separates work into layers:

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

## Adapter Inventory

Grain uses a contract-driven adapter model to tune workflow behavior for different domains.

The workflow loop is the same for every domain. Adapters change context selection, validation hints, and review focus — not workflow law.

### Official Adapters (Supported Today)

- `code_adapter`
  - Python, Rust, backend services, CLI tooling
- `frontend_adapter`
  - TypeScript, JavaScript, React, Storybook, Tauri UI

### Official Adapters (Planned)

- `docs_adapter`
  - Markdown documentation systems, content repositories, knowledge bases
- `spreadsheet_adapter`
  - Excel and spreadsheet workflows

### Custom Adapters

Users may define custom adapter profiles locally for any domain.

Examples of valid custom adapter domains:
- DevOps workflows — VPS provisioning, deployment setup, service configuration
- System administration — reverse-proxy setup, firewall and SSH hardening, backup planning, monitoring
- Local ops — machine-admin repos, dotfile management, workstation automation
- Containerization — Docker/Compose setup, rollback procedures
- Content pipelines — editorial systems, publishing workflows
- Any operational domain expressible through repo artifacts and task packets

Custom adapters follow the same contract as official adapters. Add them to `docs/runtime/adapter_profiles.md` and declare them in the manifest. No plugin system or marketplace is required.

### Future Possibilities

- shareable community adapter profiles
- adapter-aware template sets per domain

If you are managing content with Grain, `docs_adapter` is the natural direction because it fits markdown-first editorial, knowledge-base, and documentation workflows. If you are managing infrastructure or operations work, define a `devops_adapter` or `local_ops_adapter` with the file patterns and validation hints relevant to your domain.

---

## Recursive Build Principle

Grain is intended to be used to build Grain itself, then to build Assay on top of it.

That recursive use is deliberate.
It is one of the main ways the product is validated in real work:

- if Grain cannot manage its own build cleanly, its workflow claims are weak
- if Grain reduces token waste, drift, and retries while building itself, that is stronger evidence than a synthetic demo
- if Assay can later verify work produced through Grain, the loop becomes: structure the work, execute the work, verify the result

Recursive building is validation, not proof of universal fit.
Grain still needs to work outside its own repo shape and outside its creator's habits.

---

## Installation

Requirements:
- Python 3.11+
- `uv` (recommended) or `pip`

### Recommended: uv tool install

```bash
uv tool install grain-kit
```

This installs `grain` into uv's global tool path. No virtual environment needed.

### Alternative: pip install

```bash
pip install grain-kit
```

### Local source install (development or testing)

```bash
uv tool install --from . grain
```

Fallback using a local venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Verify

```bash
grain --version
grain init --help
```

Expected output:
- `grain, version <x.y.z>`
- `Usage: grain init [OPTIONS]`

---

## Updating

### uv tool install

```bash
uv tool upgrade grain-kit
```

### pip install

```bash
pip install --upgrade grain-kit
```

### Local source install

```bash
uv tool install --from . grain --force
```

or for a venv-based install:

```bash
pip install -e . --upgrade
```

---

## Troubleshooting

If `grain` is not found after `uv tool install`:
- run `uv tool dir --bin` and add that directory to your `PATH`
- macOS/Linux: `export PATH="$(uv tool dir --bin):$PATH"`
- Windows PowerShell: `$env:Path = "$(uv tool dir --bin);$env:Path"`

If you have a Python version mismatch:
- check: `python --version` (Grain requires Python 3.11+)
- install with a specific interpreter: `uv tool install --python 3.11 grain`

If venv conflicts cause unexpected behavior:
- check: `which grain` (or `where grain` on Windows) to confirm the active path
- reinstall: `uv tool uninstall grain-kit && uv tool install grain-kit`
- for local source testing, use isolated env vars:
  - point `UV_TOOL_DIR`, `UV_CACHE_DIR`, and `HOME` at temp directories

---

## Should You Use Grain For Your Machine?

Yes, sometimes.

Good use cases:
- managing dotfiles or local automation as a project
- maintaining workstation setup scripts
- organizing home-lab, local tooling, or machine-admin workflows
- managing content repositories, docs sites, and markdown-first knowledge bases
- treating your local environment as an inspectable system with tasks, review, and change history

Bad default:
- treating your entire home directory or whole machine as one Grain project

Better pattern:
- create a dedicated repo such as:
  - `local-ops`
  - `machine-admin`
  - `personal-systems`
- use Grain inside that repo

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
2. run `grain init`
3. open `prompts/workflow.onboard.new.md`
4. fill in the `Project Context`
5. paste that prompt into your agent CLI
6. let the agent generate the initial docs, manifest, backlog, and open questions
7. review those generated docs before treating canonical content as approved

Optional onboarding-aware init flags:

```bash
grain init --primary-adapter code_adapter --secondary-adapter frontend_adapter --bootstrap
```

- `--primary-adapter` sets the default adapter context for onboarding
- `--secondary-adapter` can be repeated for additional adapters
- `--bootstrap` creates a starter task packet and initializes `docs/working/current_task.md`

Compatibility note:
- `prompts/workflow.init.md` is kept as an alias for users who still invoke the old onboarding name.

After onboarding, use the normal loop:

1. `prompts/task.plan.next.md` only when a task must be selected or split
2. `prompts/task.execute.md`
3. `prompts/task.review.md`
4. `prompts/task.close.md`

### Existing Project

The full adoption flow is planned but not fully productized yet.

Current practical path:

1. run `grain init` inside the existing repo
2. use `prompts/workflow.init.md` as a temporary onboarding starter, but describe the project as an existing system
3. review generated docs carefully
4. treat generated canonical docs as draft until confirmed

Planned dedicated path:
- FR-013 (Existing Project Adoption) — deferred until new-project onboarding is stable; entry criteria recorded in `docs/working/v2_onboarding.md §10`

---

## Agent CLI Usage

Grain is designed to be used from an agent CLI.

The basic pattern is:

1. run the Grain CLI when filesystem scaffolding or validation is needed
2. run a prompt from `prompts/`
3. let the agent update the repo files
4. continue through the structured loop

### Recommended Stable Prompt Surface

Phase planning:
- `prompts/phase.plan.next.md`
- `prompts/phase.review.md`
- `prompts/phase.review_and_close.md`

Task planning and execution:
- `prompts/task.plan.next.md`
- `prompts/task.execute.md`
- `prompts/task.review.md`
- `prompts/task.close.md`

Project bootstrap:
- `prompts/workflow.onboard.new.md`
- `prompts/workflow.init.md` (compatibility alias)

### Recommended Daily Loop

Use this loop continuously inside the active phase:

1. `task.plan.next` — only when the next task must be selected, split, or added
2. `task.execute`
3. `task.review`
4. `task.close`

Do not run `task.plan.next` every time if a ready task already exists.

### Recommended Planning Loop

Use this less often:

1. `phase.plan.next`
2. `phase.review` or `phase.review_and_close` at phase boundaries

---

## Customization

Grain is meant to be customized to the project it is managing.

Users should customize:
- canonical docs for the project domain and scope
- working docs for sequencing, backlog, and open questions
- adapter selection and adapter profiles
- model strategy and agent preferences
- onboarding outputs for new or existing projects

Users should try to keep stable:
- the core workflow loop: plan → execute → review → close
- file-backed workflow state
- authority boundaries between canonical, working, runtime, and task layers
- explicit review and change-proposal gates

Good customization:
- adapt Grain to Python, Rust, React, docs, spreadsheets, local-ops, or mixed projects
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

## Minimal CLI Reference

```bash
grain init
grain docs validate
grain task create --title "..."
grain task list
grain task show --id TASK-####
grain task close --id TASK-####
grain workflow next
grain workflow run
grain task next
grain task prepare
grain orchestrate scope --scope "..."
grain orchestrate plan --scope "..."
grain adapter list
grain adapter show --id <id>
```

In normal Grain usage, the prompts drive most of the workflow and the CLI handles scaffolding, validation, and command surfaces.

---

## Important Rules

- do not treat prompts as canonical truth
- do not edit canonical docs silently
- do not execute multiple unrelated tasks in one packet
- do not let review and close perform backlog planning implicitly
- if prompt or workflow-contract docs change mid-conversation, restart the relevant agent conversation

See:
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/docs_manifest.yaml`

---

## Current Product State

- v1 core workflow complete (Phases 1–5 closed) — init, docs, task, context, model, review commands
- Phase 6 closed — adapter system foundation (`code_adapter`, `frontend_adapter`)
- Phase 7 closed — new-project onboarding flow (`grain init` with adapter selection and starter-packet bootstrap)
- Phase 8 closed — workflow automation runner (`grain workflow next/run`, `grain task next/prepare`, `grain phase next`, `grain prompt show`, machine-readable JSON contract)
- Phase 9 closed — orchestration service (`grain orchestrate scope/plan`, `grain adapter list/show`, OrchestratorPlan domain model)
- Phase 10 closed — structural intelligence (tree-sitter extraction, knowledge graph, graph-assisted context selection)
- Phase 11 closed — distribution and global install (`pip install grain`, `uv tool install grain`, PyPI publish workflow)
- Phase 12 in progress — automated workflow loop (`grain workflow loop`)
- existing-project adoption deferred behind FR-013 entry criteria

Workflow loop guardrails:
- `grain workflow loop --steps N` sets a hard loop-step limit
- `grain workflow loop --dry-run` previews planned actions without mutating state
- supervision levels:
  - `supervised`: operator approval before each action
  - `gated`: automatic run, stops at review/close gates (default)
  - `autonomous`: minimal stops, unverified automation (Assay will provide future independent verification)

See `docs/working/current_focus.md` and `docs/working/implementation_plan.md` for active phase detail.
