# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""grain status — single workspace-state summary command."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root


@click.command("status")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Show full audit findings and recent git summary.")
@click.pass_context
def status_cmd(ctx, verbose):
    """Show complete workspace state in one scan.

    Reads cached state from .grain/ when available (<5 min for workflow,
    <10 min for docs audit). Falls back to live computation if stale.

    \b
    Examples:
      grain status
      grain status --verbose
      grain status --format json
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    state = _gather_state(root)

    if fmt == "json":
        click.echo(json.dumps(state, indent=2))
        return

    _print_text(state, verbose=verbose)


def _gather_state(root: Path) -> dict:
    now = datetime.now(tz=timezone.utc)

    # ── Workflow state (cached or live) ───────────────────────────────────────
    workflow_state = _read_workflow_cache(root, now)
    if workflow_state is None:
        workflow_state = _compute_workflow_state(root)

    # ── Docs audit (cached or live) ────────────────────────────────────────────
    health = _read_audit_cache(root, now)
    if health is None:
        health = _compute_health(root)

    # ── Task counts from backlog ───────────────────────────────────────────────
    tasks = _count_tasks(root, workflow_state.get("active_phase", ""))

    # ── Install mode ──────────────────────────────────────────────────────────
    from grain.services.doctor_service import detect_install_mode, _installed_version
    install_mode = detect_install_mode()
    version = _installed_version()

    # ── Current task ─────────────────────────────────────────────────────────
    current_task = _read_current_task(root)

    # ── Phase info ────────────────────────────────────────────────────────────
    phase = _phase_info(root, workflow_state)

    return {
        "run_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "phase": phase,
        "tasks": tasks,
        "current_task": current_task,
        "workflow": {
            "stop_reason": workflow_state.get("stop_reason", ""),
            "next_action": workflow_state.get("next_action", ""),
            "ok": workflow_state.get("ok", True),
        },
        "health": health,
        "install": {
            "version": version,
            "mode": install_mode,
        },
    }


def _read_workflow_cache(root: Path, now: datetime) -> dict | None:
    cache = root / ".grain" / "last_workflow_state.json"
    if not cache.exists():
        return None
    try:
        mtime = datetime.fromtimestamp(cache.stat().st_mtime, tz=timezone.utc)
        age_seconds = (now - mtime).total_seconds()
        if age_seconds > 300:  # 5 minutes
            return None
        data = json.loads(cache.read_text(encoding="utf-8"))
        ev = data.get("evaluation", {})
        return {
            "stop_reason": ev.get("stop_reason", ""),
            "next_action": ev.get("next_action", ""),
            "active_phase": ev.get("active_phase", ""),
            "active_task_id": ev.get("active_task_id", ""),
            "ok": ev.get("ok", True),
        }
    except Exception:
        return None


def _compute_workflow_state(root: Path) -> dict:
    try:
        from grain.services.workflow_service import evaluate_workflow_state
        _, evaluation = evaluate_workflow_state(root)
        if evaluation is None:
            return {}
        return {
            "stop_reason": evaluation.stop_reason,
            "next_action": evaluation.next_action,
            "active_phase": evaluation.active_phase,
            "active_task_id": evaluation.active_task_id,
            "ok": evaluation.ok,
        }
    except Exception:
        return {}


def _read_audit_cache(root: Path, now: datetime) -> dict | None:
    cache = root / ".grain" / "last_docs_audit.json"
    if not cache.exists():
        return None
    try:
        mtime = datetime.fromtimestamp(cache.stat().st_mtime, tz=timezone.utc)
        age_seconds = (now - mtime).total_seconds()
        if age_seconds > 600:  # 10 minutes
            return None
        data = json.loads(cache.read_text(encoding="utf-8"))
        return {
            "overall": data.get("overall", "ok"),
            "error_count": data.get("summary", {}).get("error", 0),
            "warning_count": data.get("summary", {}).get("warning", 0),
        }
    except Exception:
        return None


def _compute_health(root: Path) -> dict:
    try:
        from grain.services.docs_audit_service import run_audit, save_audit_cache
        result = run_audit(root, severity_filter="medium")
        save_audit_cache(root, result)
        return {
            "overall": result.overall,
            "error_count": result.summary.get("error", 0),
            "warning_count": result.summary.get("warning", 0),
        }
    except Exception:
        return {"overall": "unknown", "error_count": 0, "warning_count": 0}


def _count_tasks(root: Path, active_phase: str) -> dict:
    backlog_path = root / "docs/working/backlog.md"
    if not backlog_path.exists():
        return {"total": 0, "done": 0, "ready": 0, "in_progress": 0, "blocked": 0}

    text = backlog_path.read_text(encoding="utf-8")
    _STATUS_RE = re.compile(r"^-\s+\*\*Status:\*\*\s*(\S+)")
    _PHASE_RE = re.compile(r"^##\s+\d+\.\s+Phase\s+(\d+)\s+—")
    _TASK_RE = re.compile(r"^###\s+P\d+-T\d+")

    counts: dict = {"total": 0, "done": 0, "ready": 0, "in_progress": 0, "blocked": 0}
    in_task = False
    in_active_phase = not active_phase  # if no active_phase, count all

    for line in text.splitlines():
        pm = _PHASE_RE.match(line)
        if pm:
            in_active_phase = not active_phase or pm.group(1) == active_phase
            in_task = False
            continue
        if not in_active_phase:
            continue
        if _TASK_RE.match(line):
            in_task = True
            continue
        if in_task:
            sm = _STATUS_RE.match(line)
            if sm:
                status = sm.group(1).lower().rstrip(".,")
                counts["total"] += 1
                if status in counts:
                    counts[status] += 1

    return counts


def _read_current_task(root: Path) -> dict | None:
    path = root / "docs/working/current_task.md"
    if not path.exists():
        return None
    result: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task ID:"):
            result["task_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("Task Path:"):
            result["task_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Status:"):
            result["status"] = line.split(":", 1)[1].strip()
    task_id = result.get("task_id", "none")
    if not task_id or task_id == "none":
        return None
    return result


def _phase_info(root: Path, workflow_state: dict) -> dict:
    active_phase = workflow_state.get("active_phase", "")
    path = root / "docs/working/current_focus.md"
    name = ""
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^Phase\s+\d+\s+—\s+(.+)$", line.strip())
            if m:
                name = m.group(1).strip()
                break
    return {
        "number": active_phase,
        "name": name,
    }


def _print_text(state: dict, verbose: bool) -> None:
    from datetime import date
    today = date.today().isoformat()
    click.echo(f"Grain Status — {today}")
    click.echo("")

    # Phase
    phase = state.get("phase", {})
    phase_str = f"Phase {phase.get('number', '?')}"
    if phase.get("name"):
        phase_str += f" — {phase['name']}"
    click.echo(f"{'Phase:':<12}{phase_str}")

    # Tasks
    t = state.get("tasks", {})
    tasks_str = (
        f"{t.get('total', 0)} total · {t.get('done', 0)} done · "
        f"{t.get('ready', 0)} ready · {t.get('in_progress', 0)} in_progress · "
        f"{t.get('blocked', 0)} blocked"
    )
    click.echo(f"{'Tasks:':<12}{tasks_str}")
    click.echo("")

    # Current task
    ct = state.get("current_task")
    if ct:
        click.echo(f"{'Current:':<12}{ct.get('task_id', '?')}  ({ct.get('status', '')})")
    else:
        click.echo(f"{'Current:':<12}no active task")

    # Workflow
    wf = state.get("workflow", {})
    stop = wf.get("stop_reason", "")
    wf_str = stop if stop else wf.get("next_action", "ok")
    click.echo(f"{'Workflow:':<12}{wf_str}")
    click.echo("")

    # Health
    health = state.get("health", {})
    overall = health.get("overall", "ok")
    errors = health.get("error_count", 0)
    warnings = health.get("warning_count", 0)
    if overall == "ok":
        health_str = "✓ all checks pass"
    elif overall == "error":
        health_str = f"✗ {errors} error(s)"
    else:
        health_str = f"⚠ {warnings} warning(s)"
    click.echo(f"{'Health:':<12}{health_str}")

    # Install
    inst = state.get("install", {})
    click.echo(f"{'Install:':<12}grain {inst.get('version', '?')} ({inst.get('mode', '?')})")
    click.echo("")

    # Recommended action
    wf_stop = wf.get("stop_reason", "")
    if wf_stop == "packet_required":
        click.echo("→ grain workflow next")
    elif wf_stop == "execution_in_flight":
        click.echo("→ grain workflow next  (task in progress)")
    elif wf_stop:
        click.echo("→ grain workflow next")
