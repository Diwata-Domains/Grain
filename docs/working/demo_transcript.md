# Grain live-demo transcript

Every command below was run against the SOURCE build:

    uv run --project /Users/domicile/Diwata/Diwata-Labs/products/grain grain <args>

from inside the demo repo:

    /private/tmp/claude-501/-Users-domicile-Diwata/e496d06f-5f12-4fd6-8753-b00fa36ecdc9/scratchpad/grain-demo

For readability the transcript shows the commands as `grain <args>` — the
`uv run --project ...` prefix is implied on every line. Output is verbatim.

The repo is a small mixed monorepo:

    services/api/app.py            tiny Python service
    services/api/test_app.py       3 passing pytest tests
    company/handbook.docx          real .docx (python-docx)
    company/q3-budget.xlsx         real .xlsx (openpyxl), Sheet1!B2 = 12
    README.md                      one paragraph

---

## Setup notes

- `grain init` was run once. `grain status` reported GREEN ("all checks pass")
  and `grain doctor` passed 4/4 WITHOUT `grain upgrade`. No staleness nag
  appeared. Per the task instructions, the `grain upgrade` step was therefore
  SKIPPED — the workspace is already green on a fresh init from the source build.
- After capturing the walk below, the walk-generated artifacts (the TASK-0001
  packet and the explainer recipe run) were removed and the post-init scaffold
  was committed, so the owner can reproduce the exact same walk live from a
  clean `git log` of two commits.

---

## Beat 1 — the workflow loop

### grain status

    Grain Status — 2026-07-08

    Phase:      Phase 1 — [Phase name] — Not Started
    Tasks:      1 total · 0 done · 0 ready · 0 in_progress · 0 blocked

    Current:    no active task
    Workflow:   task_planning

    Health:     ✓ all checks pass
    Install:    grain 0.5.0 (editable)

### grain doctor

    Grain Doctor — 2026-07-08

    Install:
      version            0.5.0
      install mode       editable
      install path       /Users/domicile/Diwata/Diwata-Labs/.venv/lib/python3.12/site-packages
      source path        /Users/domicile/Diwata/Diwata-Labs/products/grain/src/grain

    Alignment:
      pyproject.toml     (not found)  ✓

    Workspace:
      root               /private/tmp/.../grain-demo  ✓

    Python:
      version            3.12.13
      executable         /Users/domicile/Diwata/Diwata-Labs/.venv/bin/python3

    Checks: 4/4 pass  ✓
    (exit 0)

### grain workflow next

    workflow next: ok
      phase             1
      active_task_id    none
      next_action       task_planning
      recommended_prompt  prompts/task.plan.next.md
      blocking_reasons  0
      affected_artifacts  1
        - docs/working/backlog.md
      candidate_tasks
        - P1-T01 (draft)

### grain task create --phase 1 --task-num 1 --title "Add /health endpoint"

    task create: ok
      created   tasks/P1-T01-TASK-0001
      created   tasks/P1-T01-TASK-0001/task.md
      created   tasks/P1-T01-TASK-0001/context.md
      created   tasks/P1-T01-TASK-0001/plan.md
      created   tasks/P1-T01-TASK-0001/deliverable_spec.md

### grain task close --id TASK-0001   <-- THE "AHA": REFUSED

    task close: failed
      error     results.md is required for closure but is missing
      error     packet status is 'draft' — must be 'review' before closing to 'done'
    Error: closure validation failed
      2 error(s)
    (exit 3)

Grain refuses to mark work done that has not been done. The packet is still a
draft and has no results.md, so closure is blocked with a non-zero exit code.

### grain --format json workflow next   <-- the senior-engineer beat

    {
      "ok": true,
      "command": "workflow evaluate",
      "repo": "/private/tmp/.../grain-demo",
      "task_id": "",
      "status": "",
      "files_created": [],
      "files_updated": [],
      "files_skipped": [],
      "files_blocked": [],
      "errors": [],
      "warnings": [],
      "primary_adapter": "",
      "secondary_adapters": [],
      "bootstrapped_task_id": "",
      "evaluation": {
        "ok": true,
        "next_action": "task_planning",
        "stop_reason": "",
        "blocking_reasons": [],
        "recommended_prompt": "prompts/task.plan.next.md",
        "affected_artifacts": [
          "docs/working/backlog.md"
        ],
        "active_phase": "1",
        "active_task_id": "",
        "candidate_tasks": [
          {
            "task_ref": "P1-T01",
            "status": "draft",
            "source": "backlog",
            "task_id": ""
          }
        ],
        "task_packet_path": "",
        "task_title": "",
        "warnings": [],
        "suggested_branch": "",
        "verification_id": ""
      },
      "observability": null,
      "suggestion": null
    }

### grain workflow guard; echo $?

    ✗ packet_open                            current_task.md is unset; no in_progress packet
      → grain task create --id <TASK-ID>
    ✓ results_not_stub                       no active task — skipped
    ✓ phase_alignment                        no active task — skipped
    ✓ implementation_ahead_of_packet         no implementation files ahead of packet
    ✓ branch_policy                          branch_policy: off

    Guard: 1 violation
    (exit code echoed: 1)

Guard exits non-zero because a task packet exists in draft but nothing is the
active in-progress packet. On stage this is the "the workspace enforces its own
state" beat — the exit code is CI-usable.

---

## Beat 2 — the general-workflow beat (code AND company documents, one workspace)

The office commands require an active or explicit task. In this walk we pass
`--task-id TASK-0001` explicitly. (Run as written WITHOUT a task id, the command
returns the message shown at the end of this section — the owner should either
set docs/working/current_task.md or pass --task-id on stage.)

### grain office spreadsheet propose --source company/q3-budget.xlsx --set "Sheet1!B2=14" --task-id TASK-0001

    office spreadsheet propose: ok
      created   tasks/P1-T01-TASK-0001/q3-budget.proposed.xlsx
      created   tasks/P1-T01-TASK-0001/office_review.json
      output_path      tasks/P1-T01-TASK-0001/q3-budget.proposed.xlsx
      operation_mode   propose
      validator_results
        - spreadsheet-structure [structure] passed: Workbook change summary includes touched sheets and ranges.
        - spreadsheet-reference [reference] passed: Referenced spreadsheet output file exists.
        - spreadsheet-policy [policy] passed: Write mode respects Phase 23 policy.
      residual_risks
        - None

### grain office review show --task-id TASK-0001

    office review show: ok
      updated   tasks/P1-T01-TASK-0001/office_review.json
      operation_mode   propose
      artifact_paths
        - company/q3-budget.xlsx
        - tasks/P1-T01-TASK-0001/q3-budget.proposed.xlsx
      validator_results
        - spreadsheet-structure [structure] passed: Workbook change summary includes touched sheets and ranges.
        - spreadsheet-reference [reference] passed: Referenced spreadsheet output file exists.
        - spreadsheet-policy [policy] passed: Write mode respects Phase 23 policy.
      residual_risks
        - None

### grain office docx propose --source company/handbook.docx --replace "flexible=compressed" --task-id TASK-0001

(the word "flexible" appears in the handbook's Working Hours paragraph)

    office docx propose: ok
      created   tasks/P1-T01-TASK-0001/handbook.proposed.docx
      created   tasks/P1-T01-TASK-0001/office_review.json
      output_path      tasks/P1-T01-TASK-0001/handbook.proposed.docx
      operation_mode   propose
      validator_results
        - docx-structure [structure] passed: Document preserved heading and table structure.
        - docx-reference [reference] passed: Referenced `.docx` output file exists.
        - docx-policy [policy] passed: Write mode respects Phase 23 policy.
      residual_risks
        - None

### Proof that NO write lands on the originals

    xlsx  original B2=12   proposed B2=14
    docx  original has 'flexible': True | 'compressed': False
    docx  proposed has 'flexible': False | 'compressed': True

The mutation lands only in the `.proposed.` file inside the task packet. The
source `company/q3-budget.xlsx` still reads 12 and the source handbook still
says "flexible". The change is proposed and reviewable before any write lands.

### Run as written WITHOUT --task-id (for the owner's awareness)

    grain office spreadsheet propose --source company/q3-budget.xlsx --set "Sheet1!B2=14"

    Error: office command requires an active or explicit task
      set docs/working/current_task.md or pass --task-id
    (exit 1)

---

## Beat 3 — the recipe engine

### grain recipe list

    ID              NAME                CATEGORY  SOURCE   STEPS
    explainer       Beginner Explainer  content   bundled  3
    research-brief  Research Brief      research  bundled  6

    2 recipes (2 bundled, 0 workspace)

### grain recipe show explainer

    recipe: explainer
      name          Beginner Explainer
      category      content
      supervision   gated
      description   Turn a topic into a short, beginner-friendly explainer
    Params:
      - topic (string, required): Topic to explain
    Steps:
      1. outline [Outline the explanation]  inputs=['params'] -> 01-outline.md
      2. draft [Draft the explainer]  inputs=['params', 'outline'] -> 02-draft.md
      3. polish [Tighten and format]  inputs=['draft'] -> explainer.md
    Final: explainer.md

### grain recipe run explainer --param topic="deterministic workflows"

    recipe run: awaiting_input
      run_id   explainer-0001
      recipe   explainer
      mode     operator
      cursor   outline
      steps    outline=awaiting_input draft=pending polish=pending

Default mode is "operator": offline, deterministic, NO agent. The run pauses at
`awaiting_input` on the first step. To advance, the operator writes the step's
output file (docs/recipes/runs/explainer-0001/01-outline.md) then runs
`grain recipe next`. Repeating for each step drives the run to `done`:

    grain recipe next --run explainer-0001   (after writing 01-outline.md)
    -> outline=done draft=pending polish=pending

    grain recipe next --run explainer-0001   (after writing 02-draft.md)
    -> outline=done draft=done polish=pending

    grain recipe next --run explainer-0001   (after writing explainer.md)
    -> recipe next: done   (outline=done draft=done polish=done)

`--auto` mode instead shells to the configured agent per step. That is the
compelling version but it is non-deterministic and depends on a configured
agent CLI plus network — not captured here.
