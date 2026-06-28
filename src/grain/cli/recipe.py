# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""CLI surface for the recipe step-runner.

Discovery / authoring verbs (``list`` / ``show`` / ``scaffold``) plus the
operator-mode run verbs (``run`` / ``next`` / ``status`` / ``resume`` / ``gate``)
for the PARALLEL recipe engine (``grain.recipe/v2`` definitions,
``grain.recipe-run/v1`` run state). None of these ever touch
``evaluate_workflow_state`` or the SDLC packet loop; the run verbs drive the
engine through ``RecipeService`` + ``recipe_store`` and never create task packets.

Run state lives under ``docs/recipes/runs/<run-id>/`` and the run verbs are
operator-mode only: deterministic, offline, no network and no API key — the
engine renders a step prompt and pauses at ``awaiting_input`` until the
human/agent writes the step's ``output`` artifact (a missing output is a pause,
never a failure). The CLI stays thin: it marshals args, calls the service/store,
and formats output.

Every command honours the GLOBAL ``--format`` flag read from ``ctx.obj["fmt"]``
(mirroring :mod:`grain.cli.workflow`); there is no per-command ``--format``
option. Errors are routed through :mod:`grain.domain.errors` types and
:func:`grain.cli.error_handler.handle_error` for a clean non-zero exit.
"""

from __future__ import annotations

import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.domain.errors import (
    ForgeError,
    MissingPathError,
    UsageError,
    ValidationError,
)
from grain.domain.recipe import RECIPE_API_VERSION, RecipeSchemaError
from grain.services import recipe_store
from grain.services.recipe_service import (
    RECIPES_DIR,
    RUNS_DIR,
    GateStateError,
    MissingParamError,
    RecipeEngineError,
    RecipeNotFoundError,
    RecipeService,
    RunNotFoundError,
    resolve_recipe_agent,
)

from .error_handler import handle_error


def _fmt(ctx) -> str:
    return ctx.obj.get("fmt", "text") if ctx.obj else "text"


def _repo(ctx) -> str | None:
    return ctx.obj.get("repo") if ctx.obj else None


def _fail(exc: ForgeError) -> None:
    """Print via handle_error and exit non-zero (no traceback)."""
    code = handle_error(exc)
    raise SystemExit(code)


def _drive(fn, *args, **kwargs):
    """Run an engine call, mapping its TYPED errors to ForgeError exit codes.

    The engine raises its own typed exceptions (recipe-not-found, run desync,
    undeclared/unknown tokens, non-UTF8 artifacts, ...). Without translation
    these would fall through to the CLI catch-all as a bare ``Error: ...`` exit 1.
    This routes each to the right :mod:`grain.domain.errors` type (and thus the
    spec exit code), so no raw ``KeyError`` / ``UnicodeDecodeError`` ever escapes.

    A handful of engine errors map to a more specific exit code (missing path /
    usage); the rest are validation failures. The final
    ``except RecipeEngineError`` is the catch-all (F14): because EVERY engine
    error subclasses :class:`RecipeEngineError`, no typed engine error — present
    or added later — can leak past this to the CLI catch-all as exit 1.
    """
    try:
        return fn(*args, **kwargs)
    except ForgeError as exc:
        # Already typed (e.g. a bad agent config from resume's auto path).
        _fail(exc)
    except RecipeNotFoundError as exc:
        _fail(MissingPathError("unknown recipe", str(exc)))
    except RunNotFoundError as exc:
        _fail(MissingPathError("unknown run", str(exc)))
    except MissingParamError as exc:
        _fail(UsageError("missing required recipe param", str(exc)))
    except GateStateError as exc:
        _fail(UsageError("invalid gate decision", str(exc)))
    except RecipeSchemaError as exc:
        _fail(ValidationError("malformed recipe", str(exc)))
    except RecipeEngineError as exc:
        # Catch-all for the WHOLE engine-error family (F14): definition-changed,
        # undeclared/unknown tokens, input-not-ready, artifact decode, and any
        # future typed error all land here as a clean ValidationError exit.
        _fail(ValidationError("recipe engine error", str(exc)))


def _step_to_dict(step) -> dict:
    """Serialize a RecipeStep for ``show`` — drops ``prompt``; omits unset keys."""
    obj: dict = {"id": step.id}
    if step.name:
        obj["name"] = step.name
    obj["inputs"] = list(step.inputs)
    obj["output"] = step.output
    if step.gate and step.gate != "none":
        obj["gate"] = step.gate
    return obj


def _definition_to_dict(definition) -> dict:
    """Serialize a RecipeDefinition to the normalized ``show`` shape (spec §2.1)."""
    return {
        "apiVersion": RECIPE_API_VERSION,
        "id": definition.id,
        "name": definition.name,
        "description": definition.description,
        "category": definition.category,
        "supervision": definition.supervision,
        "params": [
            {
                "id": p.id,
                "label": p.label,
                "required": p.required,
                "type": p.type,
            }
            for p in definition.params
        ],
        "steps": [_step_to_dict(s) for s in definition.steps],
        "final": definition.final,
    }


_SCAFFOLD_FILES = ("recipe.yaml", "steps/intake.md", "steps/draft.md")


def _scaffold_recipe_yaml(recipe_id: str) -> str:
    title = recipe_id.replace("-", " ").replace("_", " ").title()
    return (
        "apiVersion: grain.recipe/v2\n"
        f"id: {recipe_id}\n"
        f'name: "{title}"\n'
        'description: "TODO: describe what this recipe produces."\n'
        "category: custom        # research | docs | data | ops | content | code | custom\n"
        "supervision: gated      # supervised | gated | autonomous\n"
        "\n"
        "params:\n"
        "  - id: topic\n"
        '    label: "Topic"\n'
        "    required: true\n"
        "    type: string\n"
        "\n"
        "steps:\n"
        "  - id: intake\n"
        '    name: "Frame the work"\n'
        "    prompt: steps/intake.md      # {{topic}} substitution available\n"
        "    inputs: [params]\n"
        "    output: 01-intake.md\n"
        "  - id: draft\n"
        '    name: "Draft the deliverable"\n'
        "    prompt: steps/draft.md\n"
        "    inputs: [params, intake]\n"
        "    output: draft.md\n"
        "\n"
        "final: draft.md\n"
    )


_INTAKE_STUB = (
    "Frame the work for {{topic}}. "
    "(Replace this placeholder with the step prompt; "
    "use {{topic}} for params and {{steps.<id>}} for prior artifacts.)\n"
)
_DRAFT_STUB = (
    "Draft the deliverable for {{topic}}, building on {{steps.intake}}. "
    "(Replace this placeholder with the step prompt.)\n"
)


@click.group("recipe")
def recipe_group():
    """Recipe step-runner commands (parallel to the SDLC workflow engine)."""


@recipe_group.command("list")
@click.pass_context
def recipe_list(ctx):
    """Enumerate bundled + workspace recipes."""
    fmt = _fmt(ctx)
    root = resolve_repo_root(_repo(ctx))
    service = RecipeService(root)

    summaries = service.list_recipes()
    rows = []
    for summary in summaries:
        try:
            step_count = len(service.resolve(summary.id).steps)
        except Exception:
            step_count = 0
        rows.append((summary, step_count))

    # Bundled before workspace; alphabetical within each source.
    rows.sort(key=lambda r: (0 if r[0].source == "bundled" else 1, r[0].id))

    if fmt == "json":
        data = [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "source": s.source,
                "step_count": count,
            }
            for s, count in rows
        ]
        click.echo(json.dumps(data, indent=2))
        return

    bundled = sum(1 for s, _ in rows if s.source == "bundled")
    workspace = sum(1 for s, _ in rows if s.source == "workspace")

    if rows:
        headers = ("ID", "NAME", "CATEGORY", "SOURCE", "STEPS")
        widths = [len(h) for h in headers]
        cells = []
        for s, count in rows:
            row = (s.id, s.name, s.category or "-", s.source, str(count))
            cells.append(row)
            for i, value in enumerate(row):
                widths[i] = max(widths[i], len(value))
        line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        click.echo(line.rstrip())
        for row in cells:
            click.echo(
                "  ".join(value.ljust(widths[i]) for i, value in enumerate(row)).rstrip()
            )
        click.echo("")

    click.echo(
        f"{len(rows)} recipe{'s' if len(rows) != 1 else ''} "
        f"({bundled} bundled, {workspace} workspace)"
    )


@recipe_group.command("show")
@click.argument("recipe_id")
@click.pass_context
def recipe_show(ctx, recipe_id):
    """Load and render one recipe definition (params + ordered steps)."""
    fmt = _fmt(ctx)
    root = resolve_repo_root(_repo(ctx))
    service = RecipeService(root)

    try:
        definition = service.resolve(recipe_id)
    except RecipeNotFoundError as exc:
        _fail(MissingPathError(f"unknown recipe {recipe_id!r}", str(exc)))
        return
    except RecipeSchemaError as exc:
        _fail(ValidationError(f"malformed recipe {recipe_id!r}", str(exc)))
        return

    if fmt == "json":
        click.echo(json.dumps(_definition_to_dict(definition), indent=2))
        return

    click.echo(f"recipe: {definition.id}")
    click.echo(f"  name          {definition.name}")
    click.echo(f"  category      {definition.category or '-'}")
    click.echo(f"  supervision   {definition.supervision}")
    if definition.description:
        click.echo(f"  description   {definition.description}")

    click.echo("Params:")
    if definition.params:
        for param in definition.params:
            req = "required" if param.required else "optional"
            label = f": {param.label}" if param.label else ""
            click.echo(f"  - {param.id} ({param.type}, {req}){label}")
    else:
        click.echo("  (none)")

    click.echo("Steps:")
    for index, step in enumerate(definition.steps, start=1):
        name = f" [{step.name}]" if step.name else ""
        gate = f"  gate={step.gate}" if step.gate and step.gate != "none" else ""
        click.echo(
            f"  {index}. {step.id}{name}  inputs={list(step.inputs)} "
            f"-> {step.output}{gate}"
        )
    click.echo(f"Final: {definition.final}")


@recipe_group.command("scaffold")
@click.argument("recipe_id")
@click.option("--force", is_flag=True, default=False, help="Overwrite an existing recipe dir.")
@click.pass_context
def recipe_scaffold(ctx, recipe_id, force):
    """Bootstrap a minimal valid grain.recipe/v2 skeleton under docs/recipes/<id>/."""
    fmt = _fmt(ctx)
    root = resolve_repo_root(_repo(ctx))

    recipe_dir = root / RECIPES_DIR / recipe_id
    if recipe_dir.exists() and not force:
        _fail(
            ValidationError(
                f"recipe {recipe_id!r} already exists",
                f"{recipe_dir} exists; pass --force to overwrite",
            )
        )
        return

    steps_dir = recipe_dir / "steps"
    steps_dir.mkdir(parents=True, exist_ok=True)
    (recipe_dir / "recipe.yaml").write_text(
        _scaffold_recipe_yaml(recipe_id), encoding="utf-8"
    )
    (steps_dir / "intake.md").write_text(_INTAKE_STUB, encoding="utf-8")
    (steps_dir / "draft.md").write_text(_DRAFT_STUB, encoding="utf-8")

    rel_path = f"{RECIPES_DIR}/{recipe_id}"

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "id": recipe_id,
                    "path": rel_path,
                    "files": list(_SCAFFOLD_FILES),
                    "created": True,
                },
                indent=2,
            )
        )
        return

    click.echo(f"scaffolded recipe {recipe_id} at {rel_path}")
    for rel in _SCAFFOLD_FILES:
        click.echo(f"  created  {rel_path}/{rel}")


# ===========================================================================
# Operator-mode run verbs (P34-T05): run / next / status / resume / gate
# ===========================================================================
#
# These wire the PARALLEL recipe engine (P34-T03 ``RecipeService`` + the
# ``recipe_store`` persistence layer) into the ``recipe`` Click group. They are
# operator-mode only (deterministic, offline, no network / no API key): the
# engine renders a step prompt and pauses at ``awaiting_input`` until the
# human/agent writes the step's ``output`` artifact — a missing output is a
# pause, never a failure. ``run.json`` lives under ``docs/recipes/runs/<run-id>/``
# and is the single source of truth; the CLI delegates all parse/advance/I-O to
# the service + store and only marshals args and formats output.


def _service(ctx) -> tuple[RecipeService, "object"]:
    """Build a RecipeService for the resolved workspace root; return (svc, root)."""
    root = resolve_repo_root(_repo(ctx))
    return RecipeService(root), root


def _load_run_or_fail(root, run_id: str):
    """Load a run by id via the store, or fail with a clean non-zero exit."""
    try:
        return recipe_store.load_run(root, run_id)
    except FileNotFoundError as exc:
        _fail(MissingPathError(f"unknown run {run_id!r}", str(exc)))
    except (ValueError, KeyError) as exc:
        # unsupported apiVersion / malformed run.json / a missing required key
        # surfaced as a raw KeyError from RecipeRun.from_dict (F15) — surface a
        # clean "unreadable run" ValidationError, never a cryptic Error: 'cursor'.
        _fail(ValidationError(f"unreadable run {run_id!r}", str(exc)))


# Statuses that mean a run is genuinely IN PROGRESS (still being driven). A
# ``failed`` run is parked (resume/start fresh) and a ``done`` run is finished —
# neither blocks starting a new run (F6).
_IN_PROGRESS_STATUSES = frozenset(
    {"pending", "running", "awaiting_input", "awaiting_gate"}
)


def _open_runs(root) -> list:
    """Return loaded runs that are not yet ``done`` (i.e. still drivable).

    An UNREADABLE run is NOT silently skipped (F9). Swallowing it (the old
    ``except Exception: continue``) let "no open recipe run" be reported falsely
    and allowed a conflicting second run to start over a broken one. Instead we
    surface it as a clean ``ValidationError`` (non-zero exit) so the operator
    fixes/removes it — targeting a readable run explicitly with ``--run`` bypasses
    this scan entirely.
    """
    runs = []
    for run_id in recipe_store.list_runs(root):
        try:
            run = recipe_store.load_run(root, run_id)
        except (ValueError, KeyError, OSError) as exc:
            _fail(
                ValidationError(
                    f"unreadable recipe run {run_id!r}",
                    f"{exc}; fix or remove its run.json, or target a readable "
                    f"run with --run",
                )
            )
        if run.status != "done":
            runs.append(run)
    return runs


def _in_progress_runs(root) -> list:
    """Open runs that are genuinely in progress (excludes ``failed``), for F6."""
    return [r for r in _open_runs(root) if r.status in _IN_PROGRESS_STATUSES]


def _ambiguous(open_runs) -> UsageError:
    ids = ", ".join(r.run_id for r in open_runs)
    return UsageError(
        "ambiguous: multiple open recipe runs",
        f"pass --run <run-id> to choose one; open runs: {ids}",
    )


def _new_run_blocked(in_progress) -> UsageError:
    """Accurate refusal when starting a new run while one is in progress (F6).

    Distinguishes the single-run case (the common one) — which must NOT claim
    "ambiguous: multiple open recipe runs" — from the genuinely ambiguous
    multi-run case, which keeps the accurate "ambiguous" wording.
    """
    if len(in_progress) == 1:
        run = in_progress[0]
        return UsageError(
            f"a recipe run is already in progress: {run.run_id}",
            "advance it with `grain recipe next` / `resume`, or pass --run to "
            "drive a specific run",
        )
    return _ambiguous(in_progress)


def _resolve_run(root, run_opt: str | None) -> str:
    """Resolve the target run for next/status/gate.

    ``--run`` wins; otherwise the sole open run is used implicitly and an
    ambiguous (>1) or empty set raises ``UsageError`` (non-zero exit).
    """
    if run_opt:
        _load_run_or_fail(root, run_opt)  # validates existence
        return run_opt
    open_runs = _open_runs(root)
    if not open_runs:
        _fail(
            UsageError(
                "no open recipe run",
                "start one with `grain recipe run <id>`",
            )
        )
    if len(open_runs) > 1:
        _fail(_ambiguous(open_runs))
    return open_runs[0].run_id


def _parse_params(pairs: tuple[str, ...]) -> dict[str, str]:
    """Parse repeated ``key=value`` ``--param`` pairs; malformed -> UsageError."""
    params: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            _fail(
                UsageError(
                    f"malformed --param {pair!r}",
                    "expected key=value",
                )
            )
        key, value = pair.split("=", 1)
        key = key.strip()
        if not key:
            _fail(
                UsageError(
                    f"malformed --param {pair!r}",
                    "param key must be non-empty",
                )
            )
        params[key] = value
    return params


def _advance_to_pause(service: RecipeService, run_id: str):
    """Drive ``next`` until the run reaches a pause / gate / completion.

    Operator-mode ``run`` advances the cursor across already-authored steps but
    stops at the first un-authored step (``prompt_ready`` / ``awaiting_input``),
    a review gate (``awaiting_gate``), or the end (``run_complete``). It never
    loops on a non-advancing outcome.
    """
    while True:
        result = service.next(run_id)
        if result.outcome != "advanced":
            return result


def _steps_summary(run) -> str:
    return " ".join(f"{s.id}={s.status}" for s in run.steps)


def _emit_run(ctx, run, verb: str, *, with_artifacts: bool = False) -> None:
    """Render a run as text (human) or run.json dict (json), per spec §3."""
    fmt = _fmt(ctx)
    if fmt == "json":
        click.echo(json.dumps(run.to_dict(), indent=2))
        return

    click.echo(f"recipe {verb}: {run.status}")
    click.echo(f"  run_id   {run.run_id}")
    click.echo(f"  recipe   {run.recipe}")
    click.echo(f"  mode     {run.mode}")
    click.echo(f"  cursor   {run.cursor}")
    click.echo(f"  steps    {_steps_summary(run)}")

    if with_artifacts:
        for record in run.steps:
            if record.artifact:
                rel = f"{RUNS_DIR}/{run.run_id}/{record.artifact}"
                click.echo(f"    {record.id}  {record.status}  {rel}")
            else:
                click.echo(f"    {record.id}  {record.status}")

    if run.status == "awaiting_gate":
        record = run.step(run.cursor)
        if record.artifact:
            rel = f"{RUNS_DIR}/{run.run_id}/{record.artifact}"
            click.echo(f"  review   {rel}")
        click.echo(
            f"  hint     grain recipe gate approve --run {run.run_id}"
        )


@recipe_group.command("run")
@click.argument("recipe_id")
@click.option(
    "--param", "-p", "params", multiple=True, metavar="KEY=VALUE",
    help="Recipe parameter (repeatable).",
)
@click.option("--run", "run_opt", default=None, metavar="RUN_ID",
              help="Advance an existing run instead of starting a new one.")
@click.option("--auto", "auto", is_flag=True, default=False,
              help="Auto mode: shell to the configured agent per step "
                   "(implied when supervision is 'autonomous').")
@click.pass_context
def recipe_run(ctx, recipe_id, params, run_opt, auto):
    """Start a run and advance to the first pause / gate / end.

    Default is operator mode (offline, deterministic, no agent). ``--auto``
    (or supervision ``autonomous``) shells to the configured agent per step.
    """
    service, root = _service(ctx)
    parsed = _parse_params(params)

    if run_opt is None:
        # A new run is refused only while a genuinely IN-PROGRESS run exists
        # (spec §4) — a failed or done run does NOT block one (F6). Disambiguate
        # with --run to drive a specific run instead. (_open_runs/_in_progress_runs
        # also surfaces an unreadable run rather than silently ignoring it, F9.)
        existing = _in_progress_runs(root)
        if existing:
            _fail(_new_run_blocked(existing))
        # Resolve the definition first so 'autonomous' supervision can imply --auto.
        try:
            definition = service.resolve(recipe_id)
        except RecipeNotFoundError as exc:
            _fail(MissingPathError(f"unknown recipe {recipe_id!r}", str(exc)))
        except RecipeSchemaError as exc:
            _fail(ValidationError(f"malformed recipe {recipe_id!r}", str(exc)))
        auto = auto or definition.supervision == "autonomous"
        mode = "auto" if auto else "operator"
        try:
            started = service.start_run(recipe_id, parsed, mode=mode)
        except RecipeNotFoundError as exc:
            _fail(MissingPathError(f"unknown recipe {recipe_id!r}", str(exc)))
        except RecipeSchemaError as exc:
            _fail(ValidationError(f"malformed recipe {recipe_id!r}", str(exc)))
        except MissingParamError as exc:
            _fail(UsageError("missing required recipe param", str(exc)))
        run_id = started.run_id
    else:
        run_id = run_opt
        existing_run = _load_run_or_fail(root, run_id)
        # An existing auto run stays auto on re-drive (recorded mode wins).
        auto = auto or existing_run.mode == "auto"

    if auto:
        # Resolve the agent BEFORE any step runs; an invalid/missing config fails
        # cleanly here (typed ForgeError -> non-zero exit).
        try:
            agent = resolve_recipe_agent(root)
        except ForgeError as exc:
            _fail(exc)
        _drive(service.run_auto, run_id, agent=agent)
    else:
        _drive(_advance_to_pause, service, run_id)

    run = _load_run_or_fail(root, run_id)
    _emit_run(ctx, run, "run")
    if run.status == "failed":
        # Agent error / missing output: leave the run parked and exit non-zero.
        raise SystemExit(1)


@recipe_group.command("next")
@click.option("--run", "run_opt", default=None, metavar="RUN_ID",
              help="Run to advance (required when >1 open run exists).")
@click.pass_context
def recipe_next(ctx, run_opt):
    """Advance EXACTLY one step (operator mode)."""
    service, root = _service(ctx)
    run_id = _resolve_run(root, run_opt)
    _drive(service.next, run_id)
    run = _load_run_or_fail(root, run_id)
    _emit_run(ctx, run, "next")


@recipe_group.command("status")
@click.option("--run", "run_opt", default=None, metavar="RUN_ID",
              help="Run to report (required when >1 open run exists).")
@click.pass_context
def recipe_status(ctx, run_opt):
    """Report run state: status, cursor, and per-step status + artifacts."""
    _, root = _service(ctx)
    run_id = _resolve_run(root, run_opt)
    run = _load_run_or_fail(root, run_id)
    _emit_run(ctx, run, "status", with_artifacts=True)


@recipe_group.command("resume")
@click.argument("target")
@click.pass_context
def recipe_resume(ctx, target):
    """Re-enter a paused/failed run from its cursor in the recorded mode.

    ``target`` is a run-id or a recipe-id (resolving to its sole open run). On an
    ``awaiting_gate`` run this does NOT pass the gate — use ``gate approve``.
    """
    service, root = _service(ctx)
    run_id = _resolve_resume_target(root, target)
    # resume re-enters in the run's recorded mode (operator or auto). For an auto
    # run this resolves the agent (typed ForgeError on a bad/missing config);
    # engine typed errors (desync, decode, ...) map through _drive.
    _drive(service.resume, run_id)
    run = _load_run_or_fail(root, run_id)
    _emit_run(ctx, run, "resume")
    if run.status == "failed":
        raise SystemExit(1)


def _resolve_resume_target(root, target: str) -> str:
    """Resolve a resume ``target`` (run-id, else recipe-id -> sole open run)."""
    try:
        recipe_store.load_run(root, target)
        return target
    except FileNotFoundError:
        pass
    except ValueError as exc:
        _fail(ValidationError(f"unreadable run {target!r}", str(exc)))
    # Not a run id — treat as a recipe id and find its open run(s).
    matches = [r for r in _open_runs(root) if r.recipe == target]
    if not matches:
        _fail(
            MissingPathError(
                f"no open run for {target!r}",
                "pass an existing run-id, or start one with `grain recipe run`",
            )
        )
    if len(matches) > 1:
        _fail(_ambiguous(matches))
    return matches[0].run_id


@recipe_group.command("gate")
@click.argument("decision", type=click.Choice(["approve", "reject"]))
@click.option("--run", "run_opt", default=None, metavar="RUN_ID",
              help="Run to decide (required when >1 open run exists).")
@click.pass_context
def recipe_gate(ctx, decision, run_opt):
    """Decide a review gate on an ``awaiting_gate`` run (approve / reject)."""
    service, root = _service(ctx)
    run_id = _resolve_run(root, run_opt)
    run = _load_run_or_fail(root, run_id)

    if run.status != "awaiting_gate":
        _fail(
            UsageError(
                f"run {run_id} is not awaiting a gate",
                f"current status: {run.status}",
            )
        )

    if decision == "reject":
        # reject -> rework (F7): reset the gated step so `next`/`resume` re-render
        # it, instead of freezing the run at a dead-end gate.
        _drive(service.reject_gate, run_id)
    else:
        # approve: advance PAST the gated step without re-running it.
        _drive(service.approve_gate, run_id)

    run = _load_run_or_fail(root, run_id)
    _emit_run(ctx, run, "gate")
