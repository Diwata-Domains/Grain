# Grain — research-brief recipe demo (Evening of Python Coding)

A deterministic, offline, multi-step research workflow you can run from a single
directory. No API key, no network.

## Install

```
uv tool install grain-kit
# or:
pip install grain-kit

grain --version
```

## What this is

`grain recipe` is a small linear workflow engine that runs **parallel** to
Grain's coding workflow. A *recipe* is an ordered list of steps; each step reads
only its declared inputs and produces one inspectable Markdown artifact. The
*process* — step order and input scoping — is fixed and replayable; only the
content of each artifact varies. Everything here runs offline and deterministically.

This workspace ships the `research-brief` recipe (6 steps:
intake → gather → outline → draft → self_check → format) plus a committed
reference run so the workflow can be shown with zero network and zero risk.

## Run it — reference run + live next (operator mode)

### (a) Show the committed reference run

Proves the finished structure — zero network, zero risk:

```
cd examples/recipe-demo
grain recipe show research-brief
cat docs/recipes/runs/research-brief-0001/run.json    # status: done, cursor: format, 6 steps done
cat docs/recipes/runs/research-brief-0001/brief.md    # the finished deliverable artifact
```

### (b) Drive the live state machine on a fresh run

```
grain recipe run research-brief --param topic="GLP-1 obesity market"   # outcome: started; pauses
grain recipe next       # renders step 1 (intake) prompt; run -> awaiting_input
grain recipe status     # shows the cursor (intake) + per-step state
```

A bare `grain recipe run` only *starts* the run (status `pending`, cursor on the
first step). In operator mode the engine **never** writes artifacts: a human or
agent authors each step's `output` file, then `grain recipe next` advances the
cursor. The run does **not** auto-complete offline — the finished shape is shown
by the committed reference run above, not by a live bare run.

## What you'll see

The reference run shows the finished shape: 6 ordered artifacts ending at
`brief.md`, each step reading only its declared prior `inputs`. On the live fresh
run, `grain recipe next` renders step 1's prompt and the run enters
`awaiting_input` — the operator-mode pause for the human/agent to author the
artifact — and `grain recipe status` shows the cursor. The process (step order +
input scoping) is fixed and replayable; only the content varies.

## Offline fallback

The committed `docs/recipes/runs/research-brief-0001/` reference run is the
always-available, zero-network proof of the finished structure. If a live run is
undesirable, `cat docs/recipes/runs/research-brief-0001/brief.md` at any time to
show the finished deliverable.

Auto mode (`grain recipe run --auto`) is the OPTIONAL "watch the artifacts
appear" beat: it shells out to an agent per step and writes the artifacts itself.
It is networked and can hang, so it is intentionally out of scope here —
pre-record it for the demo rather than running it live.

## Reference values

| Fact            | Value                                              |
| --------------- | -------------------------------------------------- |
| PyPI package    | `grain-kit`                                         |
| Install         | `uv tool install grain-kit` / `pip install grain-kit` |
| CLI commands    | `grain recipe show` / `run` / `next` / `status`    |
| Workflow file   | `docs/recipes/research-brief/recipe.yaml`          |
| Reference run   | `docs/recipes/runs/research-brief-0001/`           |
| Repo            | `https://github.com/Diwata-Domains/Grain`             |

## Failure / resume

A failed step keeps the cursor on that step; `grain recipe resume` retries from
the cursor in the run's recorded mode.
