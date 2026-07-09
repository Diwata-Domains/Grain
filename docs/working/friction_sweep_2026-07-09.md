# Friction Sweep — 2026-07-09

A fleet-wide sweep of `docs/working/tooling_notes.md` across every Grain workspace on the
machine. 37 files found; 12 unique after removing git-worktree copies, phase archives, and
untouched templates. 87 entries harvested, 75 open, 65 logged against Grain, 61 unique after
deduplication.

**Every open Grain friction was replayed against the published grain-kit 0.6.0 in a throwaway
workspace.** 28 still reproduce and became Phase 38. The 29 below no longer reproduce and can
be closed without work.

---

## Notes to close without work

| Command | Why it can be closed |
|---|---|
| ``grain upgrade`` | The note's symptom is that `templates/tasks/results.md` and `docs/runtime/context_loading.md` get silently skipped as "customized" on every workspace, including fresh ones, so upgrade changes never... |
| ``grain workflow next` in monorepo` | The friction makes two claims; neither holds against grain 0.6.0. CLAIM A — "workflow next from monorepo root resolves to the root workspace, not the nearest product/tooling workspace." This is lit... |
| ``grain task create` — orchestrator workspace` | The note's core technical claim is that Grain tracks tasks through packet directories (tasks/) rather than backlog entries, so a phase whose work was done directly — with no `grain task create` pac... |
| ``grain task create --id`` | The friction is obsolete because the task-ID model changed fundamentally. When it was logged, the human-facing ID was an opaque auto-incremented TASK-#### that the user could not set, so a pre-plan... |
| `grain doctor` | Both claims in the note fail to reproduce against grain 0.6.0. The note assumes repo detection keyed on grain.toml. Current grain has no grain.toml at all — root detection is anchored on the marker... |
| `grain task create` | The note asks for a lightweight packet mode via a `--simple` flag that produces only task.md + results.md instead of the full multi-file packet. That exact flag now exists in grain 0.6.0, documente... |
| `prompts/task.execute.md` | The friction is behavioral: in a live AI session, an agent told to "execute inline" via prompts/task.execute.md skipped the packet-generation steps and jumped to coding. The note itself flagged it ... |
| `grain upgrade` | The friction claimed `grain upgrade` silently skips seeding working docs (e.g. tooling_notes.md) that are defined in the source manifest but absent in the project, and should instead detect and off... |
| `grain workflow next` | The note (GB-005) says `grain workflow next` at Phase 3 start emitted `phase_boundary_review_close_required` "because no task packets existed yet — indistinguishable from a completed phase awaiting... |
| `data_contracts.md §1` | Both concrete assertions in the friction are now false. (1) data_contracts.md 1 heading now reads 'Assay Result Payload Schema' with no 'Sentinel' anywhere in the file - the exact CP-002 rename is ... |
| `grain workflow next` | The reported bug was that `workflow next` misroutes to `task_execute` for a completed task because grain reads current_task.md as active without checking task status. In grain 0.6.0 this is fixed. ... |
| `grain workflow next` | The friction's core factual claim — "backlog entries alone are not sufficient; Grain requires a task packet folder (tasks/P6-T0N-.../) in ready status before routing, workaround: grain task create ... |
| `grain workflow next` | The friction was a missing-command report: `grain phase close` did not exist, so a phase_boundary_review_close_required stop had no CLI to resolve it — the only workaround was hand-seeding the next... |
| `AI session resume` | The friction is a workflow-behavior gap: on session resume from a context summary, the AI went straight to implementation and skipped creating task packets. The note's own suggested fix was "add a ... |
| `assay submit` | test |
| `grain workflow next` | The friction was: "Grain has no project-complete terminal state; after all phases done, `grain workflow next` returns `required_docs_invalid` / 'unable to parse current phase'." That terminal state... |
| `grain task create` | The friction's root cause was that the next-ID rule derived from the tasks/archive max alone, so a done-but-unarchived packet living in tasks/P29-...-TASK-0077/ was invisible to the counter and TAS... |
| `—` | The note is a doc-wrong report: it claims the AGENTS.md scaffold shows the incorrect `grain workflow next --format json` form, when `--format` is actually a global flag. In grain 0.6.0 the underlyi... |
| `grain --repo . upgrade --diff` | The note complains that managed-file drift surfaced via `grain upgrade --diff` during onboarding, adding noise before the repo reached a stable baseline. This is the upgrade-side sibling of the ini... |
| `grain workflow run` | The note claims `grain workflow run` only activates an already-existing packet and cannot auto-create one for a ready backlog task, forcing an explicit `grain task create` first. That is no longer ... |
| `grain task create --help` | The friction claims simple mode exists and fits small mechanical tasks, but the workflow runner does not yet guide or auto-bootstrap that path when a ready task has no packet. Both halves are now c... |
| `packet structure` | The note is a UX/discipline observation, not a tooling defect: during Phase 30 an agent externalized design/spec detail into ad-hoc `docs/working/` files (scaffold_audit.md, apply_graduation.md) wh... |
| `Phase 5 execution pattern` | This note is not a tool bug — it's a retrospective root_cause analysis of a past agent's behavior in Diwata-Infra (P5-T01/02/03 were generated without an explicit `grain task create`, no scope lock... |
| `backlog status drift` | The friction was "backlog status drift": tasks executed but left `draft` in backlog.md, plus a stale current_task.md, with the stated root cause being "no automated hook or enforced convention requ... |
| `packet-first discipline` | This friction described a MISSING agent-agnostic enforcement layer for packet-first discipline. Its named fix (Grain P30-T08 / TASK-0197) called for four concrete deliverables: (1) `grain workflow ... |
| `grain workflow next` | The note worried that numbered-prefix phase headings (`## 3. Phase 2 — Multi-domain substrate`) would not be resolved by Grain because Grain was "documented to parse `## Phase N —`". This is exactl... |
| `grain --format json workflow next` | The friction claimed `grain --format json workflow next` reports the `phase_has_no_tasks` stop_reason even though backlog.md, implementation_plan.md, and `grain task list` all show ready Phase 1 ta... |
| `grain upgrade --diff` | The friction claims `grain upgrade --diff` produces diffs that try to revert a repo's custom `docs/working/*` and CRM-specific canonical doc layout back to Grain default filenames. Against grain 0.... |
| `grain onboard / docs workflow` | The friction was that the agent needed a first-class working doc to log Grain/workflow friction and had to hand-add `tooling_notes.md` locally. In grain 0.6.0 this is fully first-class and no longe... |

Three further notes were unverifiable by the sweep and were checked by hand:

- **`grain notes add` does not exist** (severity `high`, logged in `products/grain`) — **stale.**
  It shipped. `grain notes add "msg" --type friction --severity low` round-trips to the table
  and `grain notes list` reads it back. Close it.
- **`canonical docs scope`** (low, monorepo root) — an enhancement request for cross-repo context,
  not a defect. Fold into `grain notes --fleet` thinking (P38-T10) or close as wontfix.
- **`grain task create` task-type differentiation** (low, monorepo root) — enhancement; `--simple`
  already covers the direct case. Close as wontfix unless handoff packets get a real design.

---

## Open friction about other tools

These are logged in Grain inboxes but are not Grain defects. They belong in their own trackers.

| Tool | Command | Workspace |
|---|---|---|
| other | ``git mv` on untracked dirs` | Diwata-Labs (monorepo root) |
| trace | `pnpm trace lint-commit` | Diwata-Labs (monorepo root) |
| other | `POST /people/{id}/interactions` | Diwata-Labs (monorepo root) |
| other | `diwa.domains` | Diwata-Labs (monorepo root) |
| other | `datamodel-codegen` | Diwata-Labs (monorepo root) |
| other | `cargo typify` | Diwata-Labs (monorepo root) |
| other | `GitHub branch protections` | Diwata-Infra |
| other | `—` | Diwata-Labs/products/diwa |
| other | `—` | Diwata-Labs/products/diwa |
| other | `pnpm build` | Diwata-Labs/packages/aether |

`pnpm trace lint-commit` was fixed on 2026-07-09: it takes a path to a message file, not the
message string, and both `CLAUDE.md` and `AGENTS.md` said otherwise. That note can be closed.

---

## Fleet hygiene

- `~/Limitless` and `~/Documents/Limitless` are **different trees with different inbox contents**.
- `~/Limitless-wt/{stg,pg-lift,crm-backfill}` carry byte-identical copies of Limitless's inbox.
  They are git worktrees; the inboxes diverge the moment anyone writes to one.
- 15 workspaces carry an untouched template inbox (`Zera`, `Diwata-Atelier`, `Diwata-Brand`,
  `Diwata-Site`, `Diwata-Programs/founder-institute`, and others).

The same defect was independently logged in up to four repos. A per-repo inbox cannot dedupe
that; see P38-T10.

---

## Addendum — `grain notes triage --fleet` measured against the real fleet

Run after Phase 38 shipped, dry-run, across 9 roots. All 46 `tooling_notes.md` files on the
machine were hashed before and after: **none was modified.**

```
notes triage (fleet, dry-run) — grain 0.6.0
  15 stale candidate(s) · 7 still open · 27 need human
```

**Do not run `--resolve-stale` against this.** The classifier is unsound, in both directions.

*Precision.* Triage marks a note stale when its recorded command now exits 0 in a pristine
throwaway workspace. But the sandbox has none of the state the symptom needed. Installing
`grain-kit==0.5.0` in an isolated venv and replaying every candidate settles it — these all
exit **0 on 0.5.0 too**, so their exit code never encoded the defect:

| Command | exit on 0.5.0 | exit on 0.6.0 | sound? |
|---|---|---|---|
| `grain task list --format json` | 2 | 0 | yes |
| `grain workflow next --format json` | 2 | 0 | yes |
| `grain phase list` | 2 | 0 | yes |
| `grain phase status` | 2 | 0 | yes |
| `grain onboard .` | 0 | 0 | no |
| `grain upgrade` | 0 | 0 | no |
| `grain upgrade --diff` | 0 | 0 | no |
| `grain upgrade --add-missing` | 0 | 0 | no |
| `grain doctor` | 0 | 0 | no |
| `grain phase next` | 0 | 0 | no |
| `grain workflow next` | 0 | 0 | no |
| `grain task validate` | 0 | 0 | no |
| `grain --format json workflow next` | 0 | 0 | no |

Four of fifteen. The four that work are exactly the ones whose symptom lived on the CLI
surface — a command or a flag that did not exist. `upgrade --add-missing` and the positional
`task validate` *were* fixed in Phase 38, but the replay did not establish it; they land in the
stale bucket by accident.

*Recall.* The `still open` bucket is no better. It lists `grain task close` (fixed — `grain
review approve` now sets the state) and `grain notes add` (shipped long ago) as open, because a
bare invocation exits 2 for a missing argument, and Click exits 2 for `No such command` too.

An exit code is not evidence. See P38-T12.
