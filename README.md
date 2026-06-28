# Grain

[![PyPI](https://img.shields.io/pypi/v/grain-kit)](https://pypi.org/project/grain-kit/)
[![License: AGPL-3.0-only](https://img.shields.io/badge/license-AGPL--3.0--only-blue)](LICENSE)

**Deterministic workflow for agent CLIs.**

Grain is a workflow layer for Claude Code, Codex, and similar agent CLIs. It gives coding agents explicit task packets, minimal context, and review gates so development stays structured, inspectable, and repeatable.

---

## Why Grain

Ad hoc agent-driven development tends to degrade into repeated explanations, oversized context, hidden state across conversations, and unclear review boundaries.

Grain makes the workflow explicit:

- one task packet at a time
- only load the context the task needs
- keep state in repo files, not agent memory
- require explicit review before closure

```text
Idea → Task Packet → Context → Execute → Review → Close
```

This is most useful when you are already working inside an agent CLI and want the agent to follow a deterministic workflow instead of an open-ended conversation.

---

## Install

Requirements: Python 3.11+, `uv` recommended

```bash
uv tool install grain-kit
```

Or with pip:

```bash
pip install grain-kit
```

Verify:

```bash
grain --version
```

---

## Quick start

### New project

```bash
mkdir my-project && cd my-project
git init
grain init
grain workflow next
grain prompt show
```

Open `prompts/workflow.onboard.new.md` in your agent CLI, fill in the project context section, and let the agent generate the initial docs and backlog.

### Existing project

```bash
cd your-existing-project
grain onboard
grain workflow next
grain prompt show
```

Open `prompts/workflow.onboard.existing.md` in your agent CLI. That prompt scans the existing repo, drafts canonical docs, and identifies open questions. Review those docs before treating them as authoritative.

---

## How Grain organizes a repo

```text
docs/canonical/   — source-of-truth project decisions
docs/working/     — backlog, current focus, open questions
docs/runtime/     — workflow rules, adapter profiles, context-loading rules
tasks/            — one folder per task packet
prompts/          — stable prompt files for your agent CLI
```

The workflow is file-backed and inspectable. There is no hidden daemon, database, or background service.

---

## The daily loop

```bash
grain workflow next      # what is the next legal step?
grain prompt show        # surface the stable prompt entrypoint
```

Run the recommended prompt in your agent CLI, review the proposed work, then close the task when complete.

Full command set:

```bash
grain workflow next
grain workflow explain      # translate the current gate into concrete actions
grain workflow reconcile --dry-run   # repair packet/backlog drift before continuing
grain prompt show
grain review check --id TASK-0001
grain task close --id TASK-0001
grain tui                   # terminal dashboard
```

One-shot and loop modes:

```bash
grain workflow run            # execute one legal state transition, stop at gates
grain workflow loop --steps 3 # repeated state-driven execution
```

When Grain stops, use `grain workflow explain` first. Return to `grain workflow next` only after the file-backed issue is repaired.

---

## Using Grain with Claude Code and Codex

Grain is designed to be the workflow layer for any agent CLI. Paste the instruction below into your CLAUDE.md or equivalent config file:

```text
You are operating inside a repository that uses Grain as its workflow system.

Rules:
- Run `grain workflow next` before deciding what to do.
- If Grain stops or the repo state looks inconsistent, run `grain workflow explain` before improvising.
- If the explanation points to drift, run `grain workflow reconcile --dry-run` before making manual repairs.
- Run `grain prompt show` before executing the next step.
- Follow the recommended prompt exactly.
- Work on only one active task packet at a time.
- Do not bypass review or closure gates.
- Do not modify canonical docs directly.
- Do not invent workflow steps outside Grain.
```

**Codex and CLI-first usage:**

```bash
grain --format json workflow next
grain prompt show --format json
```

Use `--format json` when the calling environment wants structured state. Use text output when a human operator is driving the loop directly.

**Claude Desktop / MCP:**

```bash
grain --format json mcp manifest    # inspect available tools
grain mcp serve                     # start local stdio MCP wrapper
```

Current intent:
- Codex/tool-execution path: direct CLI
- Claude/Desktop-style path: local stdio MCP wrapper over the same Grain services
- both paths preserve the same workflow rules and packet-first boundaries

---

## Task packets

A task packet is the unit of execution. Each task lives in its own directory under `tasks/`.

```text
task.md             — description, status, acceptance criteria
context.md          — files and docs relevant to this task
plan.md             — proposed approach
deliverable_spec.md
results.md
handoff.md          — (when needed)
```

Commands:

```bash
grain task list
grain task show --id TASK-0001
grain task prepare --id TASK-0001
grain task validate --id TASK-0001
grain task create --phase 3 --task-num 4 --title "Add packet validator"
```

Small-fix example:

```bash
grain task create --phase 3 --task-num 5 --title "Fix CLI help typo"
grain workflow next
grain prompt show
grain task close --id TASK-0002 --quick --summary "Fixed the CLI help typo."
```

---

## Context control

Grain loads only the context each task needs instead of dumping the whole repo into every interaction.

```bash
grain context build --id TASK-0001
grain context show --id TASK-0001
grain context export --id TASK-0001
```

---

## Adapters

Adapters tune context selection and review focus for different types of work while keeping the workflow loop identical.

```bash
grain adapter list
grain adapter show --id code_adapter
```

Available adapters: `code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`, `obsidian_adapter`, `database_adapter`, `crawler_adapter`.

Declare the adapter on the task packet when the work targets that domain. Grain assembles focused context from relevant files instead of broad app code.

---

## Review and closure

Grain keeps review explicit.

```bash
grain review check --id TASK-0001
grain review summary --id TASK-0001
grain review handoff --id TASK-0001
grain task close --id TASK-0001
```

Intelligence may propose changes. Closure is a deliberate gate.

---

## Verification (Assay integration)

Grain integrates with [Assay](https://github.com/Diwata-Labs/Assay) for visual and functional verification of tasks before closure.

```bash
grain verify submit --id TASK-0001
grain verify status --verification-id VERIFY-0001-001
grain verify ingest --verification-id VERIFY-0001-001 --payload payload.json
```

Verification rules:
- submit after the packet has `results.md` and is in `review` or `done`
- `verification_request.json` and `verification_result.json` are packet-local artifacts
- do not close a task while verification is `pending`
- if verification is `failed`, resolve the findings or explicitly waive before closure

---

## Office documents

Grain supports packet-first mutation of `.docx` and spreadsheet files with a review step before any writes land.

```bash
grain office docx propose --source docs/brief.docx --replace "old=new"
grain office docx export --source docs/brief.docx --replace "old=new"
grain office spreadsheet propose --source data/report.xlsx --set "Sheet1!B2=14"
grain office spreadsheet export --source data/report.xlsx --set "Sheet1!B2=14"
grain office review show --task-id TASK-0001
```

Every office command persists `office_review.json` into the packet. Review the artifact summary before closing the packet.

---

## Orchestration

Generate plan proposals for larger scopes without silently mutating the repo plan.

```bash
grain orchestrate scope --scope "Add authentication system"
grain orchestrate plan --scope "Add authentication system"
grain orchestrate accept --plan OP-XXXXXXXX
```

These outputs are proposals meant to support sequencing, not bypass review.

---

## Recipes

A recipe is a deterministic, multi-step workflow engine — an ordered list of steps,
each producing an inspectable artifact, with memory flowing between steps via declared
inputs. The step-runner engine **supersedes the older single-packet recipe model** (a
recipe is no longer "one configured task packet"). Recipes run as their own small linear
state machine **parallel to** — never inside — the task-packet loop: they never create
task packets and never touch the workflow engine.

Definitions are `grain.recipe/v2` (`docs/recipes/<id>/recipe.yaml` or bundled); run state
is `grain.recipe-run/v1` under `docs/recipes/runs/<run-id>/`, file-backed and resumable.

Default **operator mode** is offline and deterministic: `grain recipe next` renders the
current step's prompt with its scoped inputs and pauses at `awaiting_input`; you (or an
agent) write the step's `output` artifact, then advance. The engine never writes the
artifact itself and never auto-completes — a missing output is a pause, not a failure.

```bash
grain recipe run research-brief --param topic="GLP-1 obesity market"   # start a run
grain recipe status                                                    # cursor + per-step state
# write the cursor step's output artifact under docs/recipes/runs/<run-id>/, then:
grain recipe next                                                      # advance one step
grain recipe resume <run-id>                                           # re-enter a paused/failed run
```

Add `--format json` to any recipe command to drive it headlessly from an agent.

---

## Terminal UI

`grain tui` is an operator shell over Grain's CLI and file-backed workflow.

Surfaces:
- workflow dashboard and current task status
- phase backlog and packet artifact inspection
- prompt preview and compact context summary
- blocker detail and action feedback
- execute, review, and close launchers

The TUI reads the same repo files and service outputs the CLI uses. It does not maintain hidden state or bypass review gates.

---

## What Grain is not

- a coding model
- a GUI project manager
- a hidden orchestration service
- a database-backed autonomy layer

It is a filesystem-first workflow layer for agent-assisted development.

---

## Troubleshooting

If `grain` is not found after install:

```bash
uv tool dir --bin
```

Add that directory to your `PATH`.

For a local editable install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## License

[AGPL-3.0-only](LICENSE). Commercial licensing for closed-source or hosted use: ss@diwata.domains

---

## Feedback

[https://github.com/Diwata-Labs/Grain/issues](https://github.com/Diwata-Labs/Grain/issues)
