# Grain — Live Demo Script (Acme onboarding)

**Slot:** ~15 min live, Jacob's Python meetup, late July 2026
**Framing:** onboard a *real company monorepo* (`acme-platform`) live, let the agent read it,
then show the review/close gates. **Live + pre-baked fallback.**
**Every command below was executed and verified on grain-kit 0.8.0.**

The companion for the *pre-baked* `examples/demo` flow is `demo_runbook.md` — this script is the
onboarding-first variant. The talk-track lines and the "five hardest questions" there still apply.

---

## Before you go on stage

1. **grain-kit 0.8.0 installed** (pass `--refresh` or uv serves a cached older build):
   ```bash
   uv tool install --force --refresh grain-kit
   grain --version        # must print: grain, version 0.8.0 (installed)
   ```

2. **The repo:** `/Users/domicile/acme-platform` is a pristine company monorepo — `services/api/`
   (Python billing, 3 tests), `web/` (stubbed), `docs/` (+ `handbook.docx`), `finance/q3-budget.xlsx`.
   Its `main` has **no Grain yet** (that's the point — you onboard it live). The tag `healthy-state`
   is the **fallback**: the same repo already onboarded + docs populated.

3. **Demo from a throwaway clone** so `acme-platform` stays pristine and you can re-run:
   ```bash
   rm -rf /tmp/acme && git clone -q /Users/domicile/acme-platform /tmp/acme && cd /tmp/acme
   grain --version
   ```

4. **Arm the fallback** in case the live agent step (Beat 2) drags. One command drops the
   pre-baked, fully-populated docs in:
   ```bash
   git checkout healthy-state -- docs AGENTS.md      # <- your escape hatch
   ```

5. **Know these cold:** `grain task close` on an unfinished packet → **3**; `grain workflow guard`
   with no active packet → **1**; everything else → **0**. Onboard leaves `bootstrap_incomplete`
   with warnings — that is **expected**, not a bug (see Beat 1).

---

## The script

### Beat 0 (0:00–2:00) — the company repo + the problem *(no Grain yet)*

Show the repo in the editor: `services/api/pricing.py`, `finance/q3-budget.xlsx`, `docs/`.

> "This is a normal company monorepo — a Python billing service, some docs, a budget
> spreadsheet. No Grain. And here's the problem Grain solves: your agent says it's done.
> Did it write results? Did anyone review it? Right now it self-certifies. That's the whole bug."

### Beat 1 (2:00–4:30) — `grain onboard` adopts the repo

```bash
grain onboard .
```
44 files scaffolded instantly (AGENTS.md, `docs/canonical`, `docs/working`, `tasks/`,
`prompts/`). Then:
```bash
git status --short | head        # show what Grain added — no rewrite of your code
grain workflow next
```
`workflow next` stops with `bootstrap_incomplete` and `recommended_prompt
prompts/workflow.onboard.existing.md`.

> "Grain dropped a workflow skeleton into my existing repo — it didn't touch my code. And it
> won't pretend it's ready: it tells me the ONE next action — run this onboarding prompt."

### Beat 2 (4:30–8:00) — THE WOW: the agent reads *your* monorepo *(live)*

> "This is the part that matters. I point my agent at that prompt, and it reads MY repo — the
> billing service, the docs, the budget — and writes MY project docs."

Run your agent (Claude Code / Codex) on `prompts/workflow.onboard.existing.md` in `/tmp/acme`.
It populates `docs/working/current_focus.md`, `docs/working/backlog.md`,
`docs/canonical/{product_scope,architecture}.md` from what it finds, then:
```bash
grain status
```
→ `Phase 1 — Billing discounts`, warnings clearing.

> "It read the code and understood this is a billing product mid-way through discount work.
> Nobody typed that in."

**⏱ FALLBACK** — if the agent drags or wanders, cut to the pre-baked docs and keep moving:
```bash
git checkout healthy-state -- docs AGENTS.md
grain status        # Phase 1 — Billing discounts
```

### Beat 3 (8:00–10:30) — THE AHA: try to close unfinished work

```bash
grain task create --phase 1 --task-num 1 --title "Expose discount_percent on the invoices endpoint"
grain task close --id TASK-0001
```
Verbatim (exit **3**):
```
task close: failed
  error     results.md is required for closure but is missing
  error     packet status is 'draft' — must be 'review' before closing to 'done'
Error: closure validation failed
```
> "The agent *cannot* mark this done. No results, no review. That's the difference between a
> note and an enforced workflow." — the beat a beginner gets instantly. Don't rush it.

### Beat 4 (10:30–13:00) — proves it isn't a code tool

```bash
grain office spreadsheet propose \
    --source finance/q3-budget.xlsx \
    --set "Sheet1!B2=14" \
    --task-id TASK-0001
grain office review show --task-id TASK-0001
ls tasks/P1-T01-TASK-0001/
#   q3-budget.proposed.xlsx   <- the change
#   office_review.json
# finance/q3-budget.xlsx      <- original, untouched
```
**`--task-id` is required** — without it: `Error: office command requires an active or explicit
task` (exit 1). This is the single most likely on-stage fumble.

> "It proposed a change to my spreadsheet. It did not make it. I review, then I approve. Same
> gates as the code."

### Beat 5 (13:00–14:30) — the CI beat

```bash
grain --format json workflow next    # clean JSON envelope, agent-drivable
grain workflow guard; echo $?        # -> 1
```
> "Nonzero exit. Put `grain workflow guard` in a pre-commit hook or CI, and an agent physically
> cannot land code that isn't inside a reviewed task packet."

Say out loud: `guard` also returns 1 on a repo with no active packet — intentional (packet-first),
not a false positive.

### Beat 6 (14:30–15:00) — close + Q&A

> "Grain onboarded a real repo, its agent read the codebase, and then it refused to let that
> agent self-certify — code *or* spreadsheet. That's the whole pitch."

---

## Sharp edges (do not demo)

| Thing | Behavior |
|---|---|
| `grain recipe run <id>` | pauses at `awaiting_input`; reads as a hang. **Never type it.** |
| `grain office * propose` without `--task-id` | exit 1 |
| `grain workflow guard` on a clean repo | exit 1 (intentional — say so) |
| `grain onboard` result | `bootstrap_incomplete` + warnings until the onboard prompt runs — **expected** |
| `uv tool install grain-kit` without `--refresh` | may install a cached older build |

## The five hardest questions

See `demo_runbook.md` → "The five hardest questions" (Cursor? no-agent? why-not-TODO? prompt
library? over-engineered?). All apply unchanged.
