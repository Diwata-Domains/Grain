# Grain

[![PyPI](https://img.shields.io/pypi/v/grain-kit)](https://pypi.org/project/grain-kit/)
[![CI](https://github.com/Diwata-Labs/Grain/actions/workflows/ci.yml/badge.svg)](https://github.com/Diwata-Labs/Grain/actions/workflows/ci.yml)

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

For release validation:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[release] pytest
pytest -q
python -m build
python -m twine check dist/*
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

### Codex and CLI-first usage

For Codex or any environment that can invoke local commands directly, the canonical integration path is still the Grain CLI.

Preferred operating pattern:

```bash
grain --format json workflow next
grain prompt show --format json
```

Use JSON output when the calling environment wants structured state.
Use text output when a human operator is driving the loop directly.

For Codex-style usage:
- call `grain` commands directly
- prefer `grain workflow next` to decide the next legal state transition
- use `grain prompt show` to surface the stable prompt entrypoint
- keep task execution packet-first and file-backed
- treat `grain mcp` as optional, not required

### Claude Desktop and MCP-style usage

For desktop clients that prefer MCP tools over direct CLI execution, use the local MCP wrapper:

```bash
grain --format json mcp manifest
grain mcp serve
```

Current intent:
- Codex/tool-execution path: direct CLI
- Claude/Desktop-style path: local stdio MCP wrapper over the same Grain services
- both paths preserve the same workflow rules and packet-first boundaries

### Assay verification loop

Phase 28 adds the first packet-local verification bridge for Assay-backed review.

Current commands:

```bash
grain verify submit --id TASK-0001
grain verify status --verification-id VERIFY-0001-001
grain verify ingest --verification-id VERIFY-0001-001 --payload payload.json
```

Operator rules for this slice:
- submit verification only after the packet has `results.md` and is in `review` or `done`
- treat `verification_request.json` and `verification_result.json` as packet-local workflow artifacts
- do not close a task while verification is `pending`
- if verification is `failed`, resolve the findings or explicitly waive verification before closure
- keep the loop file-backed: Assay can produce the payload elsewhere, but Grain only reads and records the packet-local artifacts

### Obsidian vault usage

For Obsidian vault work, keep the CLI and packet workflow canonical:

- declare `obsidian_adapter` on the active packet when the task is about vault notes
- let `grain context build` and the normal workflow loop assemble context from the target note and nearby wiki-linked notes
- treat `.obsidian/` config as secondary context unless the task is explicitly about vault settings
- use the local MCP wrapper only as a desktop invocation surface; it does not replace the Grain workflow rules

### Database workflow usage

For database work, keep the same packet-first and local-first posture:

- declare `database_adapter` on the active packet when the task is about schema, migrations, queries, or persistence layers
- let `grain context build` assemble focused schema, migration, query, and repository context instead of loading broad app code by default
- review destructive migration risk, rollback expectations, and schema/query drift before closing the task
- treat database execution or live mutation tooling as separate future work; the current `v0.3.0` slice is about context, review, and validation guidance

### Crawler workflow usage

For crawler work, keep the same packet-first and local-first posture:

- declare `crawler_adapter` on the active packet when the task is about crawl configs, selectors, extraction schemas, or output validation
- let `grain context build` assemble focused crawl, selector, extraction, and validation context instead of loading broad app code by default
- review robots constraints, rate limits, retry policy risk, selector brittleness, and extraction drift before closing the task
- treat broad crawl execution or live scraping automation as separate future work; the current `v0.3.0` slice is about context, review, and validation guidance

Example instruction for an agent:

```text
You have access to the Grain CLI.

Use Grain to onboard this repository and follow the workflow.
Always use Grain commands to determine the next workflow step.
Use the prompt files Grain recommends.
Respect review and closure gates before marking work complete.
```

### Recommended agent instruction

If you want the agent to operate strictly through Grain, use a stronger instruction like this:

```text
You are operating inside a repository that uses Grain as its workflow system.

Your role is to execute work through Grain's state-driven workflow.

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

If you take action without first calling `grain workflow next`, you are operating incorrectly.
```

That instruction matches the real usage model well:
- Grain decides the next legal step
- the agent carries out the current step
- review and close remain explicit gates

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
grain workflow explain
grain workflow reconcile --dry-run
grain prompt show
grain review check --id TASK-0001
grain task close --id TASK-0001
grain tui
```

When Grain stops:

- use `grain workflow explain` to translate the current gate into concrete operator actions
- use `grain workflow reconcile --dry-run` when the explanation points to packet/backlog drift
- return to `grain workflow next` only after the file-backed issue is repaired

If you want Grain to execute one legal state transition and stop at gates:

```bash
grain workflow run
```

If you want repeated state-driven execution:

```bash
grain workflow loop --steps 3
```

Grain controls:
- what happens next
- what context is valid
- when execution stops

The agent controls:
- executing the current step correctly

## Terminal UI

`grain tui` is the first operator shell over Grain’s existing CLI and file-backed workflow.

Current TUI surfaces:
- workflow dashboard and current task status
- phase backlog and packet artifact inspection
- prompt preview and compact context summary
- blocker detail and action feedback
- execute, review, and close launchers that delegate to the normal Grain workflow services

The TUI is intentionally thin:
- it reads the same repo files and service outputs the CLI already uses
- it does not maintain hidden workflow state
- it does not bypass review or close gates

Current deferrals:
- deep packet content editors
- full prompt-body rendering
- full context export rendering
- embedded agent terminals
- multi-project views
- broad GUI beyond the terminal shell

## Writable office artifacts

Phase 23 adds the first packet-first office mutation workflow for `.docx` and spreadsheets.

Current commands:

```bash
grain office docx propose --source docs/brief.docx --replace "old=new"
grain office docx export --source docs/brief.docx --replace "old=new"
grain office spreadsheet propose --source data/report.xlsx --set "Sheet1!B2=14"
grain office spreadsheet export --source data/report.xlsx --set "Sheet1!B2=14"
grain office review show --task-id TASK-0001
```

Operator rules for this slice:
- run office commands inside an active task packet, or pass `--task-id` explicitly
- `.docx` and spreadsheet writes currently support `propose` and `export-as-new-file`
- every office command persists `office_review.json` into the packet for review inspection
- review the artifact summary and validator results before closing the packet

What this does not do yet:
- in-place `apply` for `.docx` or spreadsheets
- TUI-native office editors
- desktop/MCP office invocation layers

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

## Release checklist

Before publishing a release:

1. Update `pyproject.toml` and `CHANGELOG.md`.
2. Run the release validation commands above.
3. Verify `grain init`, `grain onboard`, `grain workflow next`, and `grain prompt show` still behave correctly on a clean repo.
4. Check that bundled prompts, templates, and runtime docs do not contain local absolute paths or stale project names.
5. Publish to TestPyPI first when validating packaging changes.

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
