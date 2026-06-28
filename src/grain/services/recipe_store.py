# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""File-backed persistence for recipe runs (``apiVersion: grain.recipe-run/v1``).

Owns the run-directory layout under ``docs/recipes/runs/<run-id>/``, run-id
allocation, and the atomic read/write protocol that makes a run resumable. The
single source of truth for a run is its ``run.json``; resume = re-read it.

Atomic-write contract (the load-bearing invariant):
  * Every file write goes to a sibling temp file in the same directory, then
    ``os.replace(tmp, target)`` (atomic on POSIX) renames it onto the target.
  * In :func:`write_step_artifact` the step artifact lands FIRST; ``run.json`` is
    rewritten only after — so a crash between steps never leaves ``run.json``
    pointing at a missing artifact, and the prior ``run.json`` is never observed
    truncated.

This layer is state + I/O only: no cursor advancement, no execution, no gate
transitions. The recipe engine is parallel to the SDLC loop and never writes
under ``tasks/`` or touches packet lifecycle code.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from grain.domain.recipe import (
    RECIPE_API_VERSION,
    RecipeDefinition,
    ensure_output_within,
)
from grain.domain.recipe_run import (
    RecipeRun,
    RecipeStepRecord,
    VALID_MODES,
)

RUNS_SUBDIR = "docs/recipes/runs"
_RUN_FILE = "run.json"
_ID_WIDTH = 4


def _utc_now() -> str:
    """ISO-8601 UTC timestamp with a trailing ``Z`` (project convention)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _atomic_write_text(target: Path, content: str) -> None:
    """Write ``content`` to ``target`` via a sibling temp file + ``os.replace``.

    The temp file lives in the same directory as ``target`` so ``os.replace`` is
    a same-filesystem atomic rename. If the rename raises, ``target`` is left
    untouched (never truncated).
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.name}.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, target)


def runs_root(workspace: Path) -> Path:
    """Absolute path to ``docs/recipes/runs/`` (created on demand)."""
    root = Path(workspace) / RUNS_SUBDIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_dir(workspace: Path, run_id: str) -> Path:
    """``docs/recipes/runs/<run-id>/`` for ``run_id`` (not auto-created)."""
    return Path(workspace) / RUNS_SUBDIR / run_id


def next_run_id(workspace: Path, recipe_id: str) -> str:
    """Allocate ``'<recipe-id>-NNNN'`` (zero-padded width 4), max existing + 1.

    Scans run dirs whose name is ``<recipe-id>-<digits>``; the first id for a
    recipe is ``<recipe-id>-0001``.
    """
    root = runs_root(workspace)
    pattern = re.compile(rf"^{re.escape(recipe_id)}-(\d+)$")
    highest = 0
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        match = pattern.match(entry.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{recipe_id}-{highest + 1:0{_ID_WIDTH}d}"


def create_run(
    workspace: Path,
    definition: RecipeDefinition,
    params: dict[str, str],
    mode: str = "operator",
) -> RecipeRun:
    """Allocate a run id, build the run dir, and persist the initial ``run.json``.

    The run starts ``status='pending'`` with the cursor on the first step and one
    ``pending`` :class:`RecipeStepRecord` per definition step (each carrying that
    step's declared ``gate``). ``supervision`` is copied verbatim from the parsed
    definition; ``mode`` is taken from the caller.
    """
    if mode not in VALID_MODES:
        raise ValueError(
            f"invalid mode {mode!r}; expected one of {sorted(VALID_MODES)}"
        )
    if not definition.steps:
        raise ValueError("cannot create a run for a recipe with no steps")

    run_id = next_run_id(workspace, definition.id)
    now = _utc_now()
    step_records = [
        RecipeStepRecord(id=step.id, status="pending", gate=step.gate)
        for step in definition.steps
    ]
    run = RecipeRun(
        run_id=run_id,
        recipe=definition.id,
        recipe_api_version=RECIPE_API_VERSION,
        params=dict(params),
        mode=mode,
        supervision=definition.supervision,
        status="pending",
        cursor=definition.steps[0].id,
        steps=step_records,
        created=now,
        updated=now,
    )

    directory = run_dir(workspace, run_id)
    directory.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(
        directory / _RUN_FILE, json.dumps(run.to_dict(), indent=2) + "\n"
    )
    return run


def load_run(workspace: Path, run_id: str) -> RecipeRun:
    """Read ``<run-dir>/run.json`` into a :class:`RecipeRun` (resume = re-read).

    Raises ``FileNotFoundError`` if the run dir / ``run.json`` is missing and
    ``ValueError`` on an unsupported ``apiVersion`` major.
    """
    path = run_dir(workspace, run_id) / _RUN_FILE
    if not path.is_file():
        raise FileNotFoundError(f"no run.json for run {run_id!r} at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return RecipeRun.from_dict(data)


def save_run(workspace: Path, run: RecipeRun) -> None:
    """Stamp ``run.updated`` and atomically rewrite ``run.json``."""
    run.updated = _utc_now()
    directory = run_dir(workspace, run.run_id)
    directory.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(
        directory / _RUN_FILE, json.dumps(run.to_dict(), indent=2) + "\n"
    )


def list_runs(workspace: Path) -> list[str]:
    """Run ids under ``docs/recipes/runs/`` that carry a ``run.json`` (newest-first)."""
    root = runs_root(workspace)
    ids = [
        entry.name
        for entry in root.iterdir()
        if entry.is_dir() and (entry / _RUN_FILE).is_file()
    ]
    return sorted(ids, reverse=True)


def write_step_artifact(
    workspace: Path,
    run: RecipeRun,
    step_id: str,
    content: str,
    artifact_name: str,
) -> None:
    """Persist a step artifact then ``run.json`` (artifact-first ordering).

    1. atomically write ``<run-dir>/<artifact_name>`` (temp + ``os.replace``),
    2. set the step record's ``artifact = artifact_name``,
    3. then :func:`save_run` (which atomically rewrites ``run.json``).

    Never mutates any other step's artifact. The runner sets status / attempts /
    cursor on the :class:`RecipeRun` before calling; this function only persists
    the artifact + ``run.json``.
    """
    record = run.step(step_id)  # raises KeyError if the step is unknown
    directory = run_dir(workspace, run.run_id)
    directory.mkdir(parents=True, exist_ok=True)

    # Defensive path-traversal guard (F1): the artifact name must resolve to a
    # path strictly inside the run dir. The parser already rejects unsafe step
    # outputs, so this never fires for a parsed recipe — belt-and-suspenders at
    # the join site.
    target = ensure_output_within(directory, artifact_name, label="step")

    # 1. Artifact lands first — durably on disk before run.json references it.
    _atomic_write_text(target, content)

    # 2. Point the step record at the now-persisted artifact.
    record.artifact = artifact_name

    # 3. run.json updated only after the artifact is in place.
    save_run(workspace, run)
