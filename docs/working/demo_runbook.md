# Grain — Live Demo Runbook

**Slot:** ~15–20 min, live screen-share, late July 2026
**Audience:** Python coders, mixed experience
**Every command below was executed and its output verified.**

**Two variants:** this runbook drives the pre-baked `examples/demo` repo (safest, fully scripted).
For an **onboarding-first** demo — adopt a real company monorepo live with `grain onboard`, then let
the agent read it — use **`demo_script_acme.md`** (repo: `/Users/domicile/acme-platform`).

---

## Before you go on stage

1. **grain-kit 0.8.0 is published (latest on PyPI, verified on 0.8.0 2026-07-20).**
   Install it, but pass `--refresh` — `uv tool install` will otherwise reuse a cached
   index and silently give you an older build:
   ```bash
   uv tool install --force --refresh grain-kit
   grain --version        # must print: grain, version 0.8.0 (installed)
   ```
   Verify that line before you go on stage. All beats below were re-run on 0.8.0; the only
   change since 0.6.0 is that `grain status` and the office/json outputs carry a few more
   fields — richer, not different. The exit codes (close → 3, guard → 1) are unchanged.

2. Use the pre-baked repo at `products/grain/examples/demo/`. It is a mixed
   monorepo: `services/api/` (Python, 3 passing tests) plus `company/handbook.docx`
   and `company/q3-budget.xlsx`. Do **not** run `grain init` live — the first-run
   output includes two yellow warnings about the project name and AGENTS.md.
   (`grain onboard` on an *existing* repo is different — a deterministic scaffold, clean to run
   live; that's the `demo_script_acme.md` variant. It does leave `bootstrap_incomplete` until the
   agent runs the onboard prompt, which is the point of that demo, not a wart.)

   **Rehearsing mutates it** — `grain task create` and `grain office propose` write
   packets and artifacts. Treat the committed copy as a template and work on a
   throwaway clone each time:
   ```bash
   rm -rf /tmp/demo && cp -R products/grain/examples/demo /tmp/demo
   cd /tmp/demo && git init -q . && git add -A && git -c user.email=d@d -c user.name=d commit -qm init
   ```
   Do the live demo from `/tmp/demo`, never from the repo copy.

3. Know these three exit codes cold:
   - `grain task close` on an incomplete packet → **3**
   - `grain workflow guard` with no active packet → **1**
   - everything else in this script → **0**

4. `grain workflow reconcile` is safe to show as of 0.6.0 — it now reports the same
   phase-level drift `grain workflow next` refuses on, and names the fix command.
   On a clean demo repo it prints `issues 0`.

5. **Do not type `grain recipe run`.** Operator mode pauses at `awaiting_input` and
   waits for you to hand-author the step's output file. It looks like a hang.

---

## The script

### Beat 1 (0:00–1:30) — the problem, no terminal

> "Your agent says it's done. Did it write results? Did anyone review it?
> Right now, it self-certifies. That's the whole problem."

### Beat 2 (1:30–4:00) — the workspace

```bash
grain status          # Health: ✓ all checks pass
grain workflow next   # the ONE legal next action
grain task create --phase 1 --task-num 1 --title "Add /health endpoint"
```

### Beat 3 (4:00–7:00) — THE AHA. Try to close unfinished work.

```bash
grain task close --id TASK-0001
```

Verbatim output (exit 3):

```
task close: failed
  error     results.md is required for closure but is missing
  error     packet status is 'draft' — must be 'review' before closing to 'done'
Error: closure validation failed
  2 error(s)
```

> "The agent *cannot* mark this done. No results file, no review. That's the
> difference between a note and an enforced workflow."

This is the beat a beginner understands instantly. Do not rush it.

### Beat 4 (7:00–10:00) — the beat that proves it isn't a code tool

You are in a repo with `services/api/` (Python) **and** `company/q3-budget.xlsx`.

```bash
grain office spreadsheet propose \
    --source company/q3-budget.xlsx \
    --set "Sheet1!B2=14" \
    --task-id TASK-0001
```

**`--task-id` is required.** Without it: `Error: office command requires an active
or explicit task` (exit 1). This is the single most likely way to fumble on stage.

Then show that the original was never touched:

```bash
grain office review show --task-id TASK-0001
ls tasks/P1-T01-TASK-0001/
#   q3-budget.proposed.xlsx    <- B2 = 14
#   office_review.json
# company/q3-budget.xlsx       <- B2 still 12. Untouched.
```

> "The agent proposed a change to my spreadsheet. It did not make it.
> I review, then I approve. Same loop as the code — same gates."

This is the beat that separates Grain from every coding-agent task manager.

### Beat 5 (10:00–13:00) — the senior-engineer beat

```bash
grain --format json workflow next    # clean JSON envelope, agent-drivable
grain workflow guard; echo $?        # -> 1
```

`guard` fails with `packet_open — current_task.md is unset; no in_progress packet`.

> "It's a nonzero exit. Put it in a pre-commit hook or CI, and an agent physically
> cannot land code that isn't inside a reviewed task packet."

Note: guard **also** returns 1 on a pristine repo with no active packet. That is
intentional (packet-first), but say it out loud or it looks like a false positive.

### Beat 6 (13:00–15:00) — close, then Q&A

```bash
grain tui    # open on a repo WITH an in-progress packet, or the panels are empty
```

It is a static snapshot, not a live dashboard. Treat it as garnish, not the payoff.

---

## The five hardest questions

**"Does it work with Cursor?"**
Grain is CLI- and file-first, agent-agnostic. Anything that runs a shell command and
reads files works. Confirmed on Claude Code and Codex. It is not a Cursor extension.

**"What if I don't use an agent?"**
Then Grain is mostly overhead. Say so. `product_scope.md` assumes an agent CLI.

**"Why not just a TODO.md?"**
A TODO can't refuse a bad close. Point back to Beat 3.

**"Isn't this just a prompt library?"**
No. `prompts/` are stable entrypoints; the value is the file-backed state machine —
`grain workflow next` computes the single legal next step — plus gates, plus
`grain workflow guard` returning nonzero for CI.

**"Isn't this over-engineered for one dev?"**
Concede it. It's Alpha and it's heavy (30+ command groups). It's structure for
agent-driven, multi-session work. Overkill for a 10-line script.

**Competitors, if raised.** Taskmaster tracks a list; Grain adds the review/close gate
and keeps state in git-diffable files. claude-flow is a multi-agent swarm runtime;
Grain is single-loop and deliberately not an execution engine. spec-kit scaffolds a
one-shot build; Grain governs the ongoing per-task loop.

---

## Known sharp edges (do not demo)

| Thing | Behavior |
|---|---|
| `grain recipe run <id>` | pauses at `awaiting_input`; reads as a hang |
| `grain recipe run research-brief` | `supervision: autonomous` — shells to a live agent, exit 1 without one |
| `grain recipe status` / `next` with 2+ open runs | exit 2, `ambiguous`; needs `--run <id>` |
| `grain office * propose` without `--task-id` | exit 1 |
| `uv tool install grain-kit` without `--refresh` | may install a cached 0.5.0 |

Fixed in 0.6.0, no longer hazards: the `grain orchestrate` crashes (task packets and
binary files), the `grain init` staleness nag and health error, `grain status`
reporting `Tasks: 0 total`, and `grain workflow reconcile` being blind to phase drift.

---

## Recording the asciinema cast

An asciinema cast is a *terminal recording*: it stores the characters and their timing,
not pixels. A viewer can pause it and copy a command straight out of the page. It embeds
in the README, weighs a few kilobytes, and stays sharp at any size — which is why it
beats both a screen recording and a landing page for this audience.

`scripts/demo_cast.sh` drives the whole thing and types each command for you, so a cast
never contains a typo. It rebuilds a throwaway workspace from `examples/demo` on every
run, so re-record as often as you like.

```bash
uv tool install asciinema
uv tool install --force --refresh grain-kit          # must be >= 0.6.0

bash products/grain/scripts/demo_cast.sh --check     # dry run, no recording

asciinema rec --overwrite --idle-time-limit 2 --cols 92 --rows 28 \
    -c "bash products/grain/scripts/demo_cast.sh" grain-demo.cast

asciinema play grain-demo.cast                       # watch it back
```

Runs about **45 seconds**. Slow it down with `READ_PAUSE=3 BEAT_PAUSE=1.5` if it feels
rushed; `--idle-time-limit 2` already caps dead air at two seconds.

To publish: `asciinema upload grain-demo.cast` gives a shareable link, or self-host with
[asciinema-player](https://github.com/asciinema/asciinema-player) — one JS file and one
`<div>` — so the cast lives next to Grain rather than on someone else's service.
