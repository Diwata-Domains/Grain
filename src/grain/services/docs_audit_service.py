# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Docs audit service — read-only workspace health checks across 6 document types."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

_CURRENT_TASK_PATH = "docs/working/current_task.md"
_BACKLOG_PATH = "docs/working/backlog.md"
_CURRENT_FOCUS_PATH = "docs/working/current_focus.md"
_OQ_PATH = "docs/working/open_questions.md"
_TOOLING_NOTES_PATH = "docs/working/tooling_notes.md"
_PROPOSALS_PATH = "docs/working/change_proposals.md"
_MANIFEST_PATH = "docs/runtime/docs_manifest.yaml"

_TASK_REF_RE = re.compile(r"P\d+-T\d+")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


# ── Domain objects ─────────────────────────────────────────────────────────────

@dataclass
class AuditFinding:
    doc: str
    check_id: str
    severity: str   # "error" | "warning" | "pass"
    message: str
    remediation: str = ""


@dataclass
class AuditResult:
    run_at: str
    summary: dict
    overall: str    # "ok" | "warning" | "error"
    findings: list[AuditFinding] = field(default_factory=list)


@dataclass
class AuditConfig:
    current_task_idle_days: int = 14
    current_focus_stale_days: int = 30
    oq_blocking_max: int = 3
    oq_stale_open_days: int = 60
    tooling_notes_high_severity_aging_days: int = 14
    tooling_notes_overdue_triage_max: int = 5
    proposal_aging_days: int = 30


# ── Check group filters ────────────────────────────────────────────────────────

_DOC_FILTER_MAP = {
    "current_task": _CURRENT_TASK_PATH,
    "backlog": _BACKLOG_PATH,
    "current_focus": _CURRENT_FOCUS_PATH,
    "open_questions": _OQ_PATH,
    "tooling_notes": _TOOLING_NOTES_PATH,
    "change_proposals": _PROPOSALS_PATH,
    "structural": "structural",
}


# ── Public API ─────────────────────────────────────────────────────────────────

def run_audit(
    root: Path,
    doc_filter: str | None = None,
    severity_filter: str | None = None,
) -> AuditResult:
    """Run all checks (or filtered subset) and return structured results."""
    config = _load_config(root)
    all_findings: list[AuditFinding] = []

    groups = _resolve_groups(doc_filter)

    if "current_task" in groups:
        all_findings.extend(_check_current_task(root, config))
    if "backlog" in groups:
        all_findings.extend(_check_backlog(root))
    if "current_focus" in groups:
        all_findings.extend(_check_current_focus(root, config))
    if "open_questions" in groups:
        all_findings.extend(_check_open_questions(root, config))
    if "tooling_notes" in groups:
        all_findings.extend(_check_tooling_notes(root, config))
    if "change_proposals" in groups:
        all_findings.extend(_check_change_proposals(root, config))
    if "structural" in groups:
        all_findings.extend(_check_structural(root))

    if severity_filter == "high":
        visible = [f for f in all_findings if f.severity == "error"]
    elif severity_filter == "medium":
        visible = [f for f in all_findings if f.severity in ("error", "warning")]
    else:
        visible = all_findings

    errors = [f for f in visible if f.severity == "error"]
    warnings = [f for f in visible if f.severity == "warning"]
    passes = [f for f in all_findings if f.severity == "pass"]

    if errors:
        overall = "error"
    elif warnings:
        overall = "warning"
    else:
        overall = "ok"

    return AuditResult(
        run_at=datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        summary={"pass": len(passes), "warning": len(warnings), "error": len(errors)},
        overall=overall,
        findings=visible,
    )


def save_audit_cache(root: Path, result: AuditResult) -> None:
    """Write result to .grain/last_docs_audit.json."""
    grain_dir = root / ".grain"
    grain_dir.mkdir(exist_ok=True)
    cache_path = grain_dir / "last_docs_audit.json"
    data = {
        "run_at": result.run_at,
        "summary": result.summary,
        "overall": result.overall,
        "findings": [
            {
                "doc": f.doc,
                "check_id": f.check_id,
                "severity": f.severity,
                "message": f.message,
                "remediation": f.remediation,
            }
            for f in result.findings
            if f.severity != "pass"
        ],
    }
    cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def apply_fixes(root: Path, result: AuditResult, *, confirm: bool = True) -> list[str]:
    """Apply safe auto-fixes. Returns list of applied fix descriptions."""
    applied: list[str] = []
    for finding in result.findings:
        if finding.check_id == "current_task_stale_pointer":
            if confirm:
                import click
                if not click.confirm(f"  Clear stale pointer in {_CURRENT_TASK_PATH}?", default=False):
                    continue
            _clear_current_task(root)
            applied.append("cleared stale pointer in current_task.md")
    return applied


# ── Config ────────────────────────────────────────────────────────────────────

def _load_config(root: Path) -> AuditConfig:
    manifest_path = root / _MANIFEST_PATH
    if not manifest_path.exists():
        return AuditConfig()
    try:
        import yaml  # type: ignore
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        thresholds = manifest.get("audit_thresholds", {}) if manifest else {}
        return AuditConfig(
            current_task_idle_days=thresholds.get("current_task_idle_days", 14),
            current_focus_stale_days=thresholds.get("current_focus_stale_days", 30),
            oq_blocking_max=thresholds.get("oq_blocking_max", 3),
            oq_stale_open_days=thresholds.get("oq_stale_open_days", 60),
            tooling_notes_high_severity_aging_days=thresholds.get(
                "tooling_notes_high_severity_aging_days", 14
            ),
            tooling_notes_overdue_triage_max=thresholds.get("tooling_notes_overdue_triage_max", 5),
            proposal_aging_days=thresholds.get("proposal_aging_days", 30),
        )
    except Exception:
        return AuditConfig()


def _resolve_groups(doc_filter: str | None) -> set[str]:
    all_groups = {
        "current_task", "backlog", "current_focus",
        "open_questions", "tooling_notes", "change_proposals", "structural",
    }
    if not doc_filter:
        return all_groups
    key = doc_filter.replace(".md", "")
    return {key} if key in all_groups else all_groups


# ── current_task.md checks ────────────────────────────────────────────────────

def _check_current_task(root: Path, config: AuditConfig) -> list[AuditFinding]:
    doc = _CURRENT_TASK_PATH
    path = root / doc
    if not path.exists():
        return [AuditFinding(doc=doc, check_id="current_task_stale_pointer",
                             severity="error", message=f"{doc} is missing",
                             remediation="grain init")]

    findings: list[AuditFinding] = []
    ct = _parse_current_task(path)
    task_id = ct.get("task_id", "none")

    # current_task_stale_pointer
    if task_id and task_id != "none":
        task_path = ct.get("task_path", "")
        packet_dir = _resolve_packet(root, task_id, task_path)
        if packet_dir and (packet_dir / "task.md").exists():
            from grain.domain.packets import parse_task_metadata
            meta = parse_task_metadata(packet_dir / "task.md")
            if meta.get("status") == "done":
                findings.append(AuditFinding(
                    doc=doc, check_id="current_task_stale_pointer", severity="error",
                    message=f"current_task.md points to completed packet: {task_id}",
                    remediation="grain docs audit --fix  (or set 'Task ID: none' manually)",
                ))
            else:
                findings.append(AuditFinding(
                    doc=doc, check_id="current_task_stale_pointer", severity="pass",
                    message=f"no stale pointer ({task_id} is {meta.get('status', 'unknown')})",
                ))
        else:
            findings.append(AuditFinding(
                doc=doc, check_id="current_task_stale_pointer", severity="pass",
                message="no stale pointer",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="current_task_stale_pointer", severity="pass",
            message="no active task pointer",
        ))

    # current_task_missing_packet
    if task_id and task_id != "none":
        task_path = ct.get("task_path", "")
        packet_dir = _resolve_packet(root, task_id, task_path)
        if packet_dir is None:
            findings.append(AuditFinding(
                doc=doc, check_id="current_task_missing_packet", severity="error",
                message=f"current_task.md references {task_id} but no packet directory found",
                remediation=f"grain task create --id {task_id}",
            ))
        else:
            findings.append(AuditFinding(
                doc=doc, check_id="current_task_missing_packet", severity="pass",
                message=f"packet {task_id} exists",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="current_task_missing_packet", severity="pass",
            message="no active task pointer",
        ))

    # current_task_idle
    if config.current_task_idle_days > 0:
        if not task_id or task_id == "none":
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            age = datetime.now(tz=timezone.utc) - mtime
            if age > timedelta(days=config.current_task_idle_days):
                findings.append(AuditFinding(
                    doc=doc, check_id="current_task_idle", severity="warning",
                    message=f"no active task for {age.days} days (threshold: {config.current_task_idle_days})",
                    remediation="grain workflow next",
                ))
            else:
                findings.append(AuditFinding(
                    doc=doc, check_id="current_task_idle", severity="pass",
                    message=f"workspace active ({age.days} days since last change)",
                ))
        else:
            findings.append(AuditFinding(
                doc=doc, check_id="current_task_idle", severity="pass",
                message="task is active",
            ))
    return findings


# ── backlog.md checks ─────────────────────────────────────────────────────────

def _check_backlog(root: Path) -> list[AuditFinding]:
    doc = _BACKLOG_PATH
    path = root / doc
    if not path.exists():
        return [AuditFinding(doc=doc, check_id="backlog_inprogress_no_packet",
                             severity="error", message=f"{doc} is missing",
                             remediation="grain upgrade --add-missing")]

    findings: list[AuditFinding] = []
    tasks_root = root / "tasks"
    phases = _parse_backlog_phases(path.read_text(encoding="utf-8"))

    inprogress_no_packet: list[str] = []
    done_no_results: list[str] = []

    for phase in phases:
        for task in phase["tasks"]:
            task_ref = task["ref"]
            task_id = task.get("task_id", "")
            status = task.get("status", "")

            if status == "in_progress":
                packet_ok = False
                if task_id:
                    packet_dir = _find_packet_by_id(tasks_root, task_id)
                    if packet_dir and (packet_dir / "task.md").exists():
                        from grain.domain.packets import parse_task_metadata
                        meta = parse_task_metadata(packet_dir / "task.md")
                        if meta.get("status") == "in_progress":
                            packet_ok = True
                if not packet_ok:
                    inprogress_no_packet.append(task_ref)

            elif status == "done":
                if task_id:
                    packet_dir = _find_packet_by_id(tasks_root, task_id)
                    if packet_dir and not (packet_dir / "results.md").exists():
                        done_no_results.append(task_ref)

    if inprogress_no_packet:
        for ref in inprogress_no_packet:
            findings.append(AuditFinding(
                doc=doc, check_id="backlog_inprogress_no_packet", severity="error",
                message=f"{ref} is in_progress in backlog but has no open packet",
                remediation=f"grain task create  (or check tasks/ for {ref})",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="backlog_inprogress_no_packet", severity="pass",
            message="all in_progress tasks have open packets",
        ))

    if done_no_results:
        for ref in done_no_results:
            findings.append(AuditFinding(
                doc=doc, check_id="backlog_done_no_results", severity="warning",
                message=f"{ref} is done but has no results.md in its packet",
                remediation=f"add results.md to the {ref} packet",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="backlog_done_no_results", severity="pass",
            message="all done tasks with packets have results.md",
        ))

    # phase drift: phase in_progress but all tasks done
    phase_drift: list[str] = []
    for phase in phases:
        if not phase["tasks"]:
            continue
        phase_status = phase.get("status", "")
        if phase_status == "in_progress":
            all_done = all(t.get("status") == "done" for t in phase["tasks"])
            if all_done:
                phase_drift.append(phase["name"])

    if phase_drift:
        for name in phase_drift:
            findings.append(AuditFinding(
                doc=doc, check_id="backlog_phase_status_drift", severity="warning",
                message=f"Phase {name!r} is in_progress but all tasks are done",
                remediation="grain phase close (when ready)",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="backlog_phase_status_drift", severity="pass",
            message="no in_progress phases with all tasks done",
        ))

    # closed phase with open tasks
    closed_with_open: list[str] = []
    for phase in phases:
        if phase.get("closed"):
            non_done = [t for t in phase["tasks"] if t.get("status") not in ("done", "")]
            if non_done:
                closed_with_open.append(phase["name"])

    if closed_with_open:
        for name in closed_with_open:
            findings.append(AuditFinding(
                doc=doc, check_id="backlog_phase_closed_with_open_tasks", severity="error",
                message=f"Phase {name!r} is marked CLOSED but has non-done tasks",
                remediation="review and resolve open tasks before closing phase",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="backlog_phase_closed_with_open_tasks", severity="pass",
            message="no closed phases have open tasks",
        ))

    return findings


# ── current_focus.md checks ───────────────────────────────────────────────────

def _check_current_focus(root: Path, config: AuditConfig) -> list[AuditFinding]:
    doc = _CURRENT_FOCUS_PATH
    path = root / doc
    if not path.exists():
        return [AuditFinding(doc=doc, check_id="current_focus_phase_mismatch",
                             severity="error", message=f"{doc} is missing",
                             remediation="grain upgrade --add-missing")]

    findings: list[AuditFinding] = []
    text = path.read_text(encoding="utf-8")

    # current_focus_phase_mismatch
    phase_line = _extract_current_phase(text)
    if phase_line:
        backlog_path = root / _BACKLOG_PATH
        if backlog_path.exists():
            backlog_text = backlog_path.read_text(encoding="utf-8")
            # Look for the phase number in backlog phase headings
            phase_num_match = re.search(r"Phase\s+(\d+)", phase_line)
            if phase_num_match:
                phase_num = phase_num_match.group(1)
                backlog_phase_re = re.compile(rf"##\s+\d+\.\s+Phase\s+{re.escape(phase_num)}\s+—")
                if backlog_phase_re.search(backlog_text):
                    findings.append(AuditFinding(
                        doc=doc, check_id="current_focus_phase_mismatch", severity="pass",
                        message=f"phase {phase_num} found in backlog",
                    ))
                else:
                    findings.append(AuditFinding(
                        doc=doc, check_id="current_focus_phase_mismatch", severity="warning",
                        message=f"current_focus.md references Phase {phase_num} but it's not in backlog.md",
                        remediation="update current_focus.md or add the phase to backlog.md",
                    ))
            else:
                findings.append(AuditFinding(
                    doc=doc, check_id="current_focus_phase_mismatch", severity="pass",
                    message="current phase format not standard — skipped",
                ))
        else:
            findings.append(AuditFinding(
                doc=doc, check_id="current_focus_phase_mismatch", severity="pass",
                message="backlog.md absent — skipped",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="current_focus_phase_mismatch", severity="pass",
            message="no Current Phase line found — skipped",
        ))

    # current_focus_stale
    if config.current_focus_stale_days > 0:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age = datetime.now(tz=timezone.utc) - mtime
        if age > timedelta(days=config.current_focus_stale_days):
            findings.append(AuditFinding(
                doc=doc, check_id="current_focus_stale", severity="warning",
                message=f"current_focus.md last modified {age.days} days ago (threshold: {config.current_focus_stale_days})",
                remediation="update current_focus.md with the current phase state",
            ))
        else:
            findings.append(AuditFinding(
                doc=doc, check_id="current_focus_stale", severity="pass",
                message=f"recently updated ({age.days} days ago)",
            ))

    # current_focus_priorities_done
    priority_refs = _extract_priority_task_refs(text)
    if priority_refs:
        backlog_path = root / _BACKLOG_PATH
        if backlog_path.exists():
            backlog_text = backlog_path.read_text(encoding="utf-8")
            statuses = {ref: _get_task_status_in_backlog(backlog_text, ref) for ref in priority_refs}
            all_done = all(s == "done" for s in statuses.values() if s)
            known_refs = [r for r, s in statuses.items() if s]
            if known_refs and all_done:
                findings.append(AuditFinding(
                    doc=doc, check_id="current_focus_priorities_done", severity="warning",
                    message=f"all referenced priority tasks are done: {', '.join(priority_refs)}",
                    remediation="update Immediate Priorities in current_focus.md",
                ))
            else:
                findings.append(AuditFinding(
                    doc=doc, check_id="current_focus_priorities_done", severity="pass",
                    message="at least one priority task is not yet done",
                ))
        else:
            findings.append(AuditFinding(
                doc=doc, check_id="current_focus_priorities_done", severity="pass",
                message="backlog.md absent — skipped",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="current_focus_priorities_done", severity="pass",
            message="no task references in Immediate Priorities",
        ))

    return findings


# ── open_questions.md checks ──────────────────────────────────────────────────

def _check_open_questions(root: Path, config: AuditConfig) -> list[AuditFinding]:
    doc = _OQ_PATH
    path = root / doc
    if not path.exists():
        return [AuditFinding(doc=doc, check_id="oq_blocking_accumulation",
                             severity="pass", message=f"{doc} absent — skipped")]

    findings: list[AuditFinding] = []
    text = path.read_text(encoding="utf-8")

    # Parse status lines in open questions section (before "## Resolved")
    resolved_pos = text.find("## Resolved")
    open_section = text[:resolved_pos] if resolved_pos != -1 else text

    blocking_count = 0
    stale_open: list[tuple[str, int]] = []
    now = datetime.now(tz=timezone.utc)

    # Track current entry context (title + date + status)
    current_title = ""
    current_date: str | None = None
    current_status = ""

    _OQ_HEADING_RE = re.compile(r"^###\s+(.+)$")
    _STATUS_RE = re.compile(r"-\s+\*\*Status:\*\*\s*(\S+)")
    _RAISED_RE = re.compile(r"-\s+\*\*Raised:\*\*\s*(\d{4}-\d{2}-\d{2})")

    def flush_entry():
        nonlocal blocking_count, current_title, current_date, current_status
        if current_status in ("blocking", "decision_needed"):
            blocking_count += 1
        if current_status == "open" and current_date:
            try:
                raised = datetime.strptime(current_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                age = (now - raised).days
                if age > config.oq_stale_open_days:
                    stale_open.append((current_title or "unknown", age))
            except ValueError:
                pass
        current_title = ""
        current_date = None
        current_status = ""

    for line in open_section.splitlines():
        h = _OQ_HEADING_RE.match(line)
        if h:
            flush_entry()
            current_title = h.group(1).strip()
            continue
        s = _STATUS_RE.match(line)
        if s:
            current_status = s.group(1).lower().rstrip(".,")
            continue
        r = _RAISED_RE.match(line)
        if r:
            current_date = r.group(1)

    flush_entry()

    # oq_blocking_accumulation
    if config.oq_blocking_max > 0 and blocking_count > config.oq_blocking_max:
        findings.append(AuditFinding(
            doc=doc, check_id="oq_blocking_accumulation", severity="warning",
            message=f"{blocking_count} blocking/decision_needed questions (threshold: {config.oq_blocking_max})",
            remediation="resolve or defer blocking questions before they accumulate",
        ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="oq_blocking_accumulation", severity="pass",
            message=f"{blocking_count} blocking question(s) (within threshold)",
        ))

    # oq_stale_open
    if stale_open:
        for title, age in stale_open:
            findings.append(AuditFinding(
                doc=doc, check_id="oq_stale_open", severity="warning",
                message=f"'{title}' has been open for {age} days (threshold: {config.oq_stale_open_days})",
                remediation="resolve, defer, or update the raised date if still active",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="oq_stale_open", severity="pass",
            message="no stale open questions",
        ))

    return findings


# ── tooling_notes.md checks ───────────────────────────────────────────────────

def _check_tooling_notes(root: Path, config: AuditConfig) -> list[AuditFinding]:
    doc = _TOOLING_NOTES_PATH
    path = root / doc
    if not path.exists():
        return [AuditFinding(doc=doc, check_id="tooling_notes_overdue_triage",
                             severity="pass", message=f"{doc} absent — skipped")]

    findings: list[AuditFinding] = []
    text = path.read_text(encoding="utf-8")
    now = datetime.now(tz=timezone.utc)

    # Parse table rows: | Date | Type | Command | Observation | Severity | Status |
    table_re = re.compile(
        r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*[^|]*\|\s*[^|]*\|\s*[^|]*\|\s*(\w+)\s*\|\s*(\w+)\s*\|"
    )
    open_entries: list[tuple[str, str]] = []  # (date, severity)

    for line in text.splitlines():
        m = table_re.match(line)
        if m:
            date_str, severity, status = m.group(1), m.group(2).lower(), m.group(3).lower()
            if status == "open":
                open_entries.append((date_str, severity))

    # tooling_notes_high_severity_aging
    aging_high: list[int] = []
    if config.tooling_notes_high_severity_aging_days > 0:
        for date_str, severity in open_entries:
            if severity == "high":
                try:
                    entry_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    age = (now - entry_date).days
                    if age > config.tooling_notes_high_severity_aging_days:
                        aging_high.append(age)
                except ValueError:
                    pass

    if aging_high:
        findings.append(AuditFinding(
            doc=doc, check_id="tooling_notes_high_severity_aging", severity="warning",
            message=f"{len(aging_high)} high-severity entry(ies) open >{config.tooling_notes_high_severity_aging_days} days",
            remediation="triage or escalate high-severity tooling notes",
        ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="tooling_notes_high_severity_aging", severity="pass",
            message="no aging high-severity entries",
        ))

    # tooling_notes_overdue_triage
    open_count = len(open_entries)
    if config.tooling_notes_overdue_triage_max > 0 and open_count > config.tooling_notes_overdue_triage_max:
        findings.append(AuditFinding(
            doc=doc, check_id="tooling_notes_overdue_triage", severity="warning",
            message=f"{open_count} open entries (threshold: {config.tooling_notes_overdue_triage_max})",
            remediation="review and triage tooling_notes.md",
        ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="tooling_notes_overdue_triage", severity="pass",
            message=f"{open_count} open entries (within threshold)",
        ))

    return findings


# ── change_proposals.md checks ────────────────────────────────────────────────

def _check_change_proposals(root: Path, config: AuditConfig) -> list[AuditFinding]:
    doc = _PROPOSALS_PATH
    path = root / doc
    if not path.exists():
        return [AuditFinding(doc=doc, check_id="proposal_aging",
                             severity="pass", message=f"{doc} absent — skipped")]

    findings: list[AuditFinding] = []
    text = path.read_text(encoding="utf-8")
    now = datetime.now(tz=timezone.utc)

    # Look for proposed-status entries with a Raised date
    aging_proposals: list[tuple[str, int]] = []
    current_title = ""
    current_date: str | None = None
    current_status = ""

    _CP_HEADING_RE = re.compile(r"^###\s+(.+)$")
    _STATUS_RE = re.compile(r"-\s+\*\*Status:\*\*\s*(\S+)")
    _RAISED_RE = re.compile(r"-\s+\*\*Raised:\*\*\s*(\d{4}-\d{2}-\d{2})")

    def flush():
        nonlocal current_title, current_date, current_status
        if current_status == "proposed" and current_date and config.proposal_aging_days > 0:
            try:
                raised = datetime.strptime(current_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                age = (now - raised).days
                if age > config.proposal_aging_days:
                    aging_proposals.append((current_title, age))
            except ValueError:
                pass
        current_title = ""
        current_date = None
        current_status = ""

    for line in text.splitlines():
        h = _CP_HEADING_RE.match(line)
        if h:
            flush()
            current_title = h.group(1).strip()
            continue
        s = _STATUS_RE.match(line)
        if s:
            current_status = s.group(1).lower().rstrip(".,")
            continue
        r = _RAISED_RE.match(line)
        if r:
            current_date = r.group(1)

    flush()

    if aging_proposals:
        for title, age in aging_proposals:
            findings.append(AuditFinding(
                doc=doc, check_id="proposal_aging", severity="warning",
                message=f"'{title}' has been proposed for {age} days (threshold: {config.proposal_aging_days})",
                remediation="approve, reject, or defer the proposal",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="proposal_aging", severity="pass",
            message="no aging proposals",
        ))

    return findings


# ── Structural checks ─────────────────────────────────────────────────────────

def _check_structural(root: Path) -> list[AuditFinding]:
    doc = "structural"
    manifest_path = root / _MANIFEST_PATH
    if not manifest_path.exists():
        return [AuditFinding(doc=doc, check_id="registered_doc_missing",
                             severity="error",
                             message=f"{_MANIFEST_PATH} is missing — cannot run structural checks",
                             remediation="grain init")]

    try:
        import yaml
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return [AuditFinding(doc=doc, check_id="registered_doc_missing",
                             severity="error",
                             message=f"{_MANIFEST_PATH} could not be parsed",
                             remediation="repair docs_manifest.yaml")]

    findings: list[AuditFinding] = []
    all_entries = _collect_manifest_doc_entries(manifest)

    missing: list[str] = []
    empty: list[str] = []

    for entry in all_entries:
        path_str = entry.get("path", "")
        if not path_str or path_str.endswith("/"):
            continue  # skip directory entries
        target = root / path_str
        if not target.exists():
            missing.append(path_str)
        else:
            content = target.read_text(encoding="utf-8")
            if _is_template_only(content):
                empty.append(path_str)

    if missing:
        for path_str in missing:
            findings.append(AuditFinding(
                doc=doc, check_id="registered_doc_missing", severity="error",
                message=f"registered doc missing: {path_str}",
                remediation="grain upgrade --add-missing",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="registered_doc_missing", severity="pass",
            message=f"all {len(all_entries)} registered docs present",
        ))

    if empty:
        for path_str in empty:
            findings.append(AuditFinding(
                doc=doc, check_id="registered_doc_empty", severity="warning",
                message=f"{path_str} has no content beyond template headings",
                remediation=f"add content to {path_str}",
            ))
    else:
        findings.append(AuditFinding(
            doc=doc, check_id="registered_doc_empty", severity="pass",
            message="all registered docs have substantive content",
        ))

    # required_section_missing — only fires if manifest declares required_sections
    section_findings = _check_required_sections(root, all_entries)
    findings.extend(section_findings)

    return findings


def _check_required_sections(root: Path, entries: list[dict]) -> list[AuditFinding]:
    """Check required sections if declared in manifest entries."""
    findings: list[AuditFinding] = []
    sections_checked = 0
    sections_missing = 0
    for entry in entries:
        required_sections = entry.get("required_sections", [])
        if not required_sections:
            continue
        path_str = entry.get("path", "")
        target = root / path_str
        if not target.exists():
            continue
        content = target.read_text(encoding="utf-8")
        headings = {line.lstrip("#").strip() for line in content.splitlines() if line.startswith("#")}
        for section in required_sections:
            sections_checked += 1
            if section not in headings:
                sections_missing += 1
                findings.append(AuditFinding(
                    doc="structural", check_id="required_section_missing", severity="warning",
                    message=f"{path_str} missing required section: '{section}'",
                    remediation=f"add '## {section}' to {path_str}",
                ))

    if sections_checked == 0:
        findings.append(AuditFinding(
            doc="structural", check_id="required_section_missing", severity="pass",
            message="no required sections declared in manifest",
        ))
    elif sections_missing == 0:
        findings.append(AuditFinding(
            doc="structural", check_id="required_section_missing", severity="pass",
            message=f"all {sections_checked} required section(s) present",
        ))
    return findings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_current_task(path: Path) -> dict:
    result: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task ID:"):
            result["task_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("Task Path:"):
            result["task_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Status:"):
            result["status"] = line.split(":", 1)[1].strip()
    return result


def _resolve_packet(root: Path, task_id: str, task_path: str) -> Path | None:
    if task_path and task_path not in ("none", "(unset)"):
        candidate = root / task_path.rstrip("/")
        if candidate.is_dir():
            return candidate
    tasks_root = root / "tasks"
    if not tasks_root.exists():
        return None
    return _find_packet_by_id(tasks_root, task_id)


def _find_packet_by_id(tasks_root: Path, task_id: str) -> Path | None:
    if not tasks_root.exists():
        return None
    for d in tasks_root.iterdir():
        if d.is_dir() and task_id in d.name:
            return d
    return None


def _parse_backlog_phases(text: str) -> list[dict]:
    """Parse backlog.md into a list of phase dicts with task lists."""
    _PHASE_RE = re.compile(r"^##\s+\d+\.\s+(Phase\s+\d+[^#\n]*?)(\s*✓\s*CLOSED)?$")
    _TASK_RE = re.compile(r"^###\s+(P\d+-T\d+)\s+—")
    _STATUS_RE = re.compile(r"^-\s+\*\*Status:\*\*\s*(\S+)")
    _TASK_ID_RE = re.compile(r"^-\s+\*\*TASK-ID:\*\*\s*(TASK-\d+)")
    _PHASE_STATUS_RE = re.compile(r"^>\s+\*\*Status:\*\*\s*(\S+)")

    phases: list[dict] = []
    current_phase: dict | None = None
    current_task: dict | None = None

    def flush_task():
        if current_task and current_phase:
            current_phase["tasks"].append(current_task.copy())

    def flush_phase():
        flush_task()
        if current_phase:
            phases.append(current_phase.copy())

    for line in text.splitlines():
        pm = _PHASE_RE.match(line)
        if pm:
            flush_phase()
            current_phase = {
                "name": pm.group(1).strip(),
                "closed": bool(pm.group(2)),
                "status": "",
                "tasks": [],
            }
            current_task = None
            continue

        if current_phase is None:
            continue

        ps = _PHASE_STATUS_RE.match(line)
        if ps:
            current_phase["status"] = ps.group(1).lower().rstrip(".,")
            continue

        tm = _TASK_RE.match(line)
        if tm:
            flush_task()
            current_task = {"ref": tm.group(1), "status": "", "task_id": ""}
            continue

        if current_task is not None:
            sm = _STATUS_RE.match(line)
            if sm:
                current_task["status"] = sm.group(1).lower().rstrip(".,")
                continue
            id_m = _TASK_ID_RE.match(line)
            if id_m:
                current_task["task_id"] = id_m.group(1)

    flush_phase()
    return phases


def _extract_current_phase(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Phase ") or "Phase " in line:
            m = re.search(r"Phase\s+\d+", line)
            if m:
                return line.strip()
    # also try "## Current Phase" section
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "## Current Phase" in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line:
                return next_line
    return ""


def _extract_priority_task_refs(text: str) -> list[str]:
    priorities_section = ""
    in_section = False
    for line in text.splitlines():
        if "## Immediate Priorities" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("## ") and "Immediate Priorities" not in line:
                break
            priorities_section += line + "\n"
    return _TASK_REF_RE.findall(priorities_section)


def _get_task_status_in_backlog(backlog_text: str, task_ref: str) -> str:
    _TASK_HEADING_RE = re.compile(rf"^###\s+{re.escape(task_ref)}\s+—")
    _STATUS_RE = re.compile(r"^-\s+\*\*Status:\*\*\s*(\S+)")
    found = False
    for line in backlog_text.splitlines():
        if _TASK_HEADING_RE.match(line):
            found = True
            continue
        if found:
            if line.startswith("### ") or line.startswith("## "):
                break
            m = _STATUS_RE.match(line)
            if m:
                return m.group(1).lower().rstrip(".,")
    return ""


def _collect_manifest_doc_entries(manifest: dict) -> list[dict]:
    entries: list[dict] = []
    for layer in ("canonical", "working", "runtime"):
        for entry in manifest.get(layer, []):
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def _is_template_only(content: str) -> bool:
    """Return True if file has no substantive content beyond heading lines."""
    substantive = [
        line for line in content.splitlines()
        if line.strip() and not line.startswith("#") and not line.startswith("<!--")
    ]
    return len(substantive) == 0


def _clear_current_task(root: Path) -> None:
    path = root / _CURRENT_TASK_PATH
    path.write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
        encoding="utf-8",
    )
