# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Suggest service — deterministic, file-backed, proposal-only suggestion engine.

Reads local workspace signals (ready backlog tasks, blocking/decision_needed open
questions, aging high-severity tooling notes, last 3 git commits, phase boundary)
and emits ranked SuggestionProposal objects. Generation writes only SUG-*.md files
under docs/working/proposals/. No network, no LLM — fully deterministic.

Nothing is acted on without an explicit accept/dismiss (the CLI calls accept/dismiss).
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

from grain.domain.suggest import (
    KIND_NEW_TASK,
    KIND_PICK_UP,
    STATUS_ACCEPTED,
    STATUS_DISMISSED,
    STATUS_EXPIRED,
    STATUS_PENDING,
    SuggestionProposal,
    parse_proposal_id,
)

# ── Paths ─────────────────────────────────────────────────────────────────────

_PROPOSALS_DIR = "docs/working/proposals"
_BACKLOG_PATH = "docs/working/backlog.md"
_CURRENT_FOCUS_PATH = "docs/working/current_focus.md"
_CURRENT_TASK_PATH = "docs/working/current_task.md"
_OQ_PATH = "docs/working/open_questions.md"
_TOOLING_NOTES_PATH = "docs/working/tooling_notes.md"

_GRAIN_CMD_RE = re.compile(r"grain\s+[a-z][a-z0-9 _-]*", re.IGNORECASE)
_WORD_RE = re.compile(r"[a-z0-9]+")

# Token-similarity threshold for new-task dedupe (suggest_spec section 4).
_DEDUPE_SIMILARITY = 0.70


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class GenerateResult:
    ok: bool
    proposals: list[SuggestionProposal] = field(default_factory=list)
    written: list[str] = field(default_factory=list)        # repo-relative paths
    pruned: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ListResult:
    ok: bool
    proposals: list[SuggestionProposal] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ShowResult:
    ok: bool
    proposal: SuggestionProposal | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class AcceptResult:
    ok: bool
    proposal_id: str = ""
    kind: str = ""
    expired: bool = False
    needs_confirm: bool = False
    proposed_task_md: str = ""      # new-task: rendered task.md preview for confirm
    task_ref: str = ""
    task_id: str = ""
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DismissResult:
    ok: bool
    proposal_id: str = ""
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class PruneResult:
    ok: bool
    moved: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


# ── Proposal file I/O ─────────────────────────────────────────────────────────

def render_proposal_md(proposal: SuggestionProposal) -> str:
    """Render a SuggestionProposal to the suggest_spec section 6.1 markdown template."""
    lines = [f"# Suggestion {proposal.id}", ""]
    lines.append(f"**Type:** {proposal.kind}")
    lines.append(f"**Status:** {proposal.status}")
    lines.append(f"**Generated:** {proposal.created_at}")
    lines.append(f"**Signal:** {proposal.signal}")
    if proposal.signal_ref:
        lines.append(f"**Signal-Ref:** {proposal.signal_ref}")
    if proposal.task_ref:
        lines.append(f"**Task-Ref:** {proposal.task_ref}")
    if proposal.task_id:
        lines.append(f"**Task-ID:** {proposal.task_id}")
    if proposal.phase:
        lines.append(f"**Phase:** {proposal.phase}")
    if proposal.suggested_phase:
        lines.append(f"**Suggested-Phase:** {proposal.suggested_phase}")
    lines.append("")
    lines.append("## Suggested Action")
    if proposal.kind == KIND_NEW_TASK and proposal.objective:
        lines.append(proposal.objective)
    else:
        lines.append(proposal.title)
    lines.append("")
    if proposal.rationale:
        lines.append("## Rationale")
        lines.append(proposal.rationale)
        lines.append("")
    lines.append("## Source Signals")
    if proposal.source_signals:
        for s in proposal.source_signals:
            lines.append(f"- {s}")
    else:
        lines.append(f"- {proposal.signal}")
    lines.append("")
    lines.append("## Accept Command")
    lines.append(f"grain suggest accept {proposal.id}")
    lines.append("")
    lines.append("## Dismiss Command")
    lines.append(f"grain suggest dismiss {proposal.id}")
    lines.append("")
    return "\n".join(lines)


_FIELD_RE = re.compile(r"^\*\*([A-Za-z-]+):\*\*\s*(.*)$")
_TITLE_RE = re.compile(r"^#\s+Suggestion\s+(\S+)\s*$")


def parse_proposal_md(text: str) -> SuggestionProposal | None:
    """Parse a proposal markdown file back into a SuggestionProposal."""
    lines = text.splitlines()
    if not lines:
        return None
    m = _TITLE_RE.match(lines[0].strip())
    if not m:
        return None
    proposal_id = m.group(1)

    fields: dict[str, str] = {}
    source_signals: list[str] = []
    section = ""
    rationale_lines: list[str] = []
    action_lines: list[str] = []

    for line in lines[1:]:
        stripped = line.strip()
        fm = _FIELD_RE.match(stripped)
        if fm and not section:
            fields[fm.group(1).lower()] = fm.group(2).strip()
            continue
        if stripped.startswith("## "):
            section = stripped[3:].strip().lower()
            continue
        if section == "source signals" and stripped.startswith("- "):
            source_signals.append(stripped[2:].strip())
        elif section == "rationale" and stripped:
            rationale_lines.append(stripped)
        elif section == "suggested action" and stripped:
            action_lines.append(stripped)

    kind = fields.get("type", "")
    objective = ""
    title = " ".join(action_lines).strip()
    if kind == KIND_NEW_TASK:
        objective = title

    return SuggestionProposal(
        id=proposal_id,
        kind=kind,
        title=title,
        rationale=" ".join(rationale_lines).strip(),
        signal=fields.get("signal", ""),
        signal_ref=fields.get("signal-ref", ""),
        status=fields.get("status", STATUS_PENDING),
        created_at=fields.get("generated", ""),
        source_signals=source_signals,
        task_ref=fields.get("task-ref", ""),
        task_id=fields.get("task-id", ""),
        phase=fields.get("phase", ""),
        objective=objective,
        suggested_phase=fields.get("suggested-phase", ""),
    )


def allocate_proposal_id(root: Path, today: str | None = None) -> str:
    """Return the next SUG-YYYYMMDD-NNN id for today, scanning the proposals dir."""
    today = today or date.today().strftime("%Y%m%d")
    proposals_dir = root / _PROPOSALS_DIR
    seq = 1
    if proposals_dir.exists():
        used: list[int] = []
        for f in proposals_dir.iterdir():
            if not f.is_file() or not f.name.endswith(".md"):
                continue
            parsed = parse_proposal_id(f.stem)
            if parsed and parsed[0] == today:
                used.append(parsed[1])
        seq = max(used, default=0) + 1
    return f"SUG-{today}-{seq:03d}"


def _proposal_path(root: Path, proposal_id: str) -> Path:
    return root / _PROPOSALS_DIR / f"{proposal_id}.md"


def write_proposal(root: Path, proposal: SuggestionProposal) -> Path:
    """Write a proposal file, creating the proposals dir if needed."""
    path = _proposal_path(root, proposal.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_proposal_md(proposal), encoding="utf-8")
    return path


def read_proposal(root: Path, proposal_id: str) -> SuggestionProposal | None:
    path = _proposal_path(root, proposal_id)
    if not path.exists():
        return None
    return parse_proposal_md(path.read_text(encoding="utf-8"))


def set_proposal_status(root: Path, proposal_id: str, status: str) -> bool:
    """Rewrite only the Status field of a proposal file, preserving the body."""
    path = _proposal_path(root, proposal_id)
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    replaced = False
    for line in lines:
        if not replaced and line.strip().startswith("**Status:**"):
            out.append(f"**Status:** {status}")
            replaced = True
        else:
            out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return replaced


def list_existing_proposals(root: Path) -> list[SuggestionProposal]:
    """Return all parseable proposals on disk, sorted by id."""
    proposals_dir = root / _PROPOSALS_DIR
    if not proposals_dir.exists():
        return []
    out: list[SuggestionProposal] = []
    for f in sorted(proposals_dir.iterdir()):
        if not f.is_file() or not f.name.endswith(".md") or f.name == ".gitkeep":
            continue
        parsed = parse_proposal_md(f.read_text(encoding="utf-8"))
        if parsed:
            out.append(parsed)
    return out


# ── Signal readers (deterministic; reuse existing parsers) ─────────────────────

def _active_phase(root: Path) -> str:
    """Return the active phase number (or 'complete'/'') via workflow_service."""
    from grain.services.workflow_service import _read_current_phase

    path = root / _CURRENT_FOCUS_PATH
    if not path.exists():
        return ""
    try:
        return _read_current_phase(path)
    except Exception:
        return ""


def _current_task_id(root: Path) -> str:
    """Return the active task id from current_task.md (or 'none')."""
    from grain.services.workflow_service import _read_current_task

    path = root / _CURRENT_TASK_PATH
    if not path.exists():
        return "none"
    parsed = _read_current_task(path)
    if not parsed:
        return "none"
    return parsed.get("task_id", "none") or "none"


def _backlog_phases(root: Path) -> list[dict]:
    from grain.services.docs_audit_service import _parse_backlog_phases

    path = root / _BACKLOG_PATH
    if not path.exists():
        return []
    try:
        return _parse_backlog_phases(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _phase_number(phase_name: str) -> str:
    m = re.search(r"Phase\s+(\d+)", phase_name)
    return m.group(1) if m else ""


def _tasks_for_phase(phases: list[dict], phase_num: str) -> list[dict]:
    for phase in phases:
        if _phase_number(phase.get("name", "")) == phase_num:
            return phase.get("tasks", [])
    return []


def _next_blocked_phase_num(phases: list[dict], active_phase_num: str) -> str:
    """Return the phase number immediately after the active phase, if defined."""
    try:
        target = int(active_phase_num) + 1
    except ValueError:
        return ""
    for phase in phases:
        if _phase_number(phase.get("name", "")) == str(target):
            return str(target)
    return ""


def read_recent_commits(root: Path, count: int = 3) -> list[dict]:
    """Return the last N commits as {sha, subject, files}. Empty on any failure."""
    try:
        out = subprocess.run(
            ["git", "log", f"-{count}", "--name-only", "--pretty=format:%x01%h%x02%s"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode != 0:
            return []
        raw = out.stdout
    except Exception:
        return []

    commits: list[dict] = []
    for block in raw.split("\x01"):
        block = block.strip("\n")
        if not block:
            continue
        head, _, rest = block.partition("\x02")
        sha = head.strip()
        parts = rest.split("\n", 1)
        subject = parts[0].strip() if parts else ""
        files = [ln.strip() for ln in (parts[1].splitlines() if len(parts) > 1 else []) if ln.strip()]
        commits.append({"sha": sha, "subject": subject, "files": files})
    return commits


def _commit_touched_refs(commits: list[dict]) -> set[str]:
    """Collect task refs (P<N>-T<NN>) and ids (TASK-####) mentioned in recent commits."""
    refs: set[str] = set()
    ref_re = re.compile(r"P\d+-T\d+")
    id_re = re.compile(r"TASK-\d{4,}")
    for c in commits:
        haystack = c["subject"] + " " + " ".join(c["files"])
        refs.update(ref_re.findall(haystack))
        refs.update(id_re.findall(haystack))
    return refs


def _read_blocking_open_questions(root: Path) -> list[dict]:
    """Return blocking/decision_needed open questions as {title, status, ref}."""
    path = root / _OQ_PATH
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    resolved_pos = text.find("## Resolved")
    section = text[:resolved_pos] if resolved_pos != -1 else text

    heading_re = re.compile(r"^###\s+(.+)$")
    status_re = re.compile(r"-\s+\*\*Status:\*\*\s*(\S+)")
    id_re = re.compile(r"-\s+\*\*ID:\*\*\s*(\S+)")

    out: list[dict] = []
    title = ""
    status = ""
    oq_id = ""

    def flush():
        nonlocal title, status, oq_id
        if title and status in ("blocking", "decision_needed"):
            out.append({"title": title, "status": status, "ref": oq_id or title})
        title = ""
        status = ""
        oq_id = ""

    for line in section.splitlines():
        h = heading_re.match(line)
        if h:
            flush()
            title = h.group(1).strip()
            continue
        s = status_re.match(line)
        if s:
            status = s.group(1).lower().rstrip(".,")
            continue
        i = id_re.match(line)
        if i:
            oq_id = i.group(1).strip()
    flush()
    return out


def _read_aging_high_tooling_notes(root: Path) -> list[dict]:
    """Return open high-severity tooling notes aged past threshold as {date, command, message}."""
    path = root / _TOOLING_NOTES_PATH
    if not path.exists():
        return []
    from grain.services.docs_audit_service import _load_config

    config = _load_config(root)
    threshold = config.tooling_notes_high_severity_aging_days
    now = datetime.now(tz=timezone.utc)

    # | Date | Type | Severity | Command | Message | Status |
    row_re = re.compile(
        r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*[^|]*\|\s*(\w+)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*(\w+)\s*\|"
    )
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = row_re.match(line)
        if not m:
            continue
        date_str, severity, command, message, status = (
            m.group(1),
            m.group(2).lower(),
            m.group(3).strip(),
            m.group(4).strip(),
            m.group(5).lower(),
        )
        if severity != "high" or status != "open":
            continue
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if threshold > 0 and (now - entry_date).days <= threshold:
            continue
        out.append({"date": date_str, "command": command, "message": message})
    return out


# ── Token similarity (new-task dedupe) ─────────────────────────────────────────

def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _token_similarity(a: str, b: str) -> float:
    """Overlap coefficient over alphanumeric tokens (0..1). No embeddings."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    overlap = len(ta & tb)
    return overlap / min(len(ta), len(tb))


def _existing_task_titles(root: Path) -> list[str]:
    """Collect all task titles from backlog headings and packet task.md files."""
    titles: list[str] = []
    backlog = root / _BACKLOG_PATH
    if backlog.exists():
        heading_re = re.compile(r"^###\s+P\d+-T\d+\s+—\s+(.+)$")
        for line in backlog.read_text(encoding="utf-8").splitlines():
            m = heading_re.match(line)
            if m:
                titles.append(m.group(1).strip())
    tasks_root = root / "tasks"
    if tasks_root.exists():
        for d in tasks_root.iterdir():
            task_md = d / "task.md"
            if d.is_dir() and task_md.exists():
                for line in task_md.read_text(encoding="utf-8").splitlines():
                    if line.startswith("# Task:"):
                        titles.append(line.split(":", 1)[1].strip())
                        break
    return titles


def _is_duplicate_title(title: str, existing: list[str]) -> bool:
    return any(_token_similarity(title, e) >= _DEDUPE_SIMILARITY for e in existing)


# ── Generation ─────────────────────────────────────────────────────────────────

def _build_suggestions(root: Path) -> list[SuggestionProposal]:
    """Build ranked candidate suggestions (in-memory, no ids/writes yet)."""
    phases = _backlog_phases(root)
    active = _active_phase(root)
    if not active or active in ("complete", "0"):
        return []

    current_task_id = _current_task_id(root)
    commits = read_recent_commits(root)
    touched = _commit_touched_refs(commits)
    today = date.today().isoformat()

    suggestions: list[SuggestionProposal] = []

    # ── Priority 1: pick-up — ready task in active or next-blocked phase ────────
    candidate_phases = [active]
    nxt = _next_blocked_phase_num(phases, active)
    if nxt:
        candidate_phases.append(nxt)

    seen_refs: set[str] = set()
    for phase_num in candidate_phases:
        phase_label = next(
            (p["name"] for p in phases if _phase_number(p.get("name", "")) == phase_num),
            f"Phase {phase_num}",
        )
        is_active = phase_num == active
        for task in _tasks_for_phase(phases, phase_num):
            if task.get("status") != "ready":
                continue
            task_ref = task.get("ref", "")
            task_id = task.get("task_id", "")
            if not task_ref or task_ref in seen_refs:
                continue
            # Quality bar: not the in_progress task; not touched in last 3 commits.
            if task_id and task_id == current_task_id:
                continue
            if task_ref in touched or (task_id and task_id in touched):
                continue
            seen_refs.add(task_ref)
            phase_tag = "active" if is_active else "next-blocked"
            suggestions.append(SuggestionProposal(
                id="",
                kind=KIND_PICK_UP,
                title=f"{task_ref}" + (f" ({task_id})" if task_id else "") + f" — open as current task",
                signal="Ready task in active phase" if is_active else "Ready task in next-blocked phase",
                signal_ref=task_ref,
                rationale=f"Task is ready in {phase_label} ({phase_tag} phase).",
                created_at=today,
                source_signals=[f"backlog.md: {task_ref} status = ready, phase = {phase_label} ({phase_tag})"],
                task_ref=task_ref,
                task_id=task_id,
                phase=phase_label,
            ))

    existing_titles = _existing_task_titles(root)
    active_phase_label = next(
        (p["name"] for p in phases if _phase_number(p.get("name", "")) == active),
        f"Phase {active}",
    )

    # ── Priority 2: new-task — blocking/decision_needed open questions ──────────
    for oq in _read_blocking_open_questions(root):
        objective = f"Resolve open question: {oq['title']}"
        if _is_duplicate_title(objective, existing_titles):
            continue
        suggestions.append(SuggestionProposal(
            id="",
            kind=KIND_NEW_TASK,
            title=objective,
            objective=objective,
            signal=f"open_questions.md ({oq['status']})",
            signal_ref=oq["ref"],
            rationale=(
                f"Open question '{oq['title']}' is {oq['status']} with no linked backlog task; "
                f"a decision task in {active_phase_label} would unblock it."
            ),
            created_at=today,
            source_signals=[f"open_questions.md: {oq['ref']} status = {oq['status']}"],
            suggested_phase=active_phase_label,
        ))

    # ── Priority 3: new-task — aging high-severity tooling notes ───────────────
    for note in _read_aging_high_tooling_notes(root):
        cmd_label = note["command"] or "tooling"
        objective = f"Fix high-severity tooling friction in {cmd_label}"
        if _is_duplicate_title(objective, existing_titles):
            continue
        suggestions.append(SuggestionProposal(
            id="",
            kind=KIND_NEW_TASK,
            title=objective,
            objective=objective,
            signal=f"tooling_notes {note['date']}",
            signal_ref=f"{note['date']} {cmd_label}".strip(),
            rationale=(
                f"High-severity tooling note from {note['date']} ({cmd_label}) is open with no "
                f"linked backlog task: {note['message']}"
            ),
            created_at=today,
            source_signals=[f"tooling_notes.md: {note['date']} | {cmd_label} | {note['message']}"],
            suggested_phase=active_phase_label,
        ))

    return suggestions


def _signal_key(proposal: SuggestionProposal) -> str:
    """Stable identity for a suggestion's underlying signal (for dedupe/resurface)."""
    return f"{proposal.kind}:{proposal.signal_ref}"


def generate(
    root: Path,
    *,
    kind_filter: str | None = None,
    limit: int | None = None,
    auto_prune: bool = True,
) -> GenerateResult:
    """Run the deterministic suggestion cycle and persist pending proposals.

    Steps: expire stale proposals, build new candidates, suppress signals that
    already have a pending/dismissed/accepted proposal, persist new ones, then
    optionally auto-prune expired/old-dismissed proposals out of the working dir.
    """
    # 1. Expire proposals whose underlying signal has resolved.
    _expire_resolved_proposals(root)

    existing = list_existing_proposals(root)
    # Signals already represented by a live proposal must not be re-surfaced.
    suppressed = {
        _signal_key(p)
        for p in existing
        if p.status in (STATUS_PENDING, STATUS_DISMISSED, STATUS_ACCEPTED)
    }

    candidates = _build_suggestions(root)
    if kind_filter:
        candidates = [c for c in candidates if c.kind == kind_filter]

    written: list[str] = []
    fresh: list[SuggestionProposal] = []
    for cand in candidates:
        if _signal_key(cand) in suppressed:
            continue
        suppressed.add(_signal_key(cand))
        cand.id = allocate_proposal_id(root)
        path = write_proposal(root, cand)
        written.append(str(path.relative_to(root)))
        fresh.append(cand)

    # Visible set = freshly-written + already-pending proposals.
    pending_existing = [p for p in existing if p.status == STATUS_PENDING]
    visible = pending_existing + fresh
    if kind_filter:
        visible = [p for p in visible if p.kind == kind_filter]
    visible = _rank(visible)
    if limit is not None and limit >= 0:
        visible = visible[:limit]

    pruned: list[str] = []
    if auto_prune:
        prune_res = prune(root)
        pruned = prune_res.moved

    return GenerateResult(ok=True, proposals=visible, written=written, pruned=pruned)


_RANK_ORDER = {KIND_PICK_UP: 0, KIND_NEW_TASK: 1}


def _rank(proposals: list[SuggestionProposal]) -> list[SuggestionProposal]:
    """Stable deterministic ranking: pick-up before new-task, then by id."""
    return sorted(proposals, key=lambda p: (_RANK_ORDER.get(p.kind, 9), p.signal_ref, p.id))


def top_suggestion(root: Path) -> SuggestionProposal | None:
    """Read-only top suggestion for workflow-next surfacing — writes nothing."""
    try:
        candidates = _build_suggestions(root)
    except Exception:
        return None
    if not candidates:
        return None
    ranked = _rank(candidates)
    return ranked[0]


# ── List / show ────────────────────────────────────────────────────────────────

def list_proposals(root: Path, status: str | None = None) -> ListResult:
    """List proposals, optionally filtered by status. Default: pending only."""
    proposals = list_existing_proposals(root)
    if status == "all":
        visible = proposals
    elif status:
        visible = [p for p in proposals if p.status == status]
    else:
        visible = [p for p in proposals if p.status == STATUS_PENDING]
    return ListResult(ok=True, proposals=_rank(visible))


def show_proposal(root: Path, proposal_id: str) -> ShowResult:
    proposal = read_proposal(root, proposal_id)
    if proposal is None:
        return ShowResult(ok=False, errors=[f"proposal not found: {proposal_id}"])
    return ShowResult(
        ok=True,
        proposal=proposal,
        path=str(_proposal_path(root, proposal_id).relative_to(root)),
    )


# ── Expiry ─────────────────────────────────────────────────────────────────────

def _expire_resolved_proposals(root: Path) -> list[str]:
    """Mark pending proposals expired when their underlying signal has resolved."""
    expired: list[str] = []
    for proposal in list_existing_proposals(root):
        if proposal.status != STATUS_PENDING:
            continue
        if _signal_resolved(root, proposal):
            set_proposal_status(root, proposal.id, STATUS_EXPIRED)
            expired.append(proposal.id)
    return expired


def _signal_resolved(root: Path, proposal: SuggestionProposal) -> bool:
    """Return True if a proposal's signal has materially resolved (so it should expire)."""
    if proposal.kind == KIND_PICK_UP:
        return _task_is_done_or_gone(root, proposal.task_ref)
    if proposal.kind == KIND_NEW_TASK:
        if proposal.signal.startswith("open_questions"):
            return not _oq_still_blocking(root, proposal.signal_ref)
        if proposal.signal.startswith("tooling_notes"):
            return not _tooling_note_still_open(root, proposal.signal_ref)
    return False


def _task_is_done_or_gone(root: Path, task_ref: str) -> bool:
    if not task_ref:
        return False
    for phase in _backlog_phases(root):
        for task in phase.get("tasks", []):
            if task.get("ref") == task_ref:
                return task.get("status") == "done"
    return True  # ref no longer present in backlog


def _oq_still_blocking(root: Path, ref: str) -> bool:
    for oq in _read_blocking_open_questions(root):
        if oq["ref"] == ref:
            return True
    return False


def _tooling_note_still_open(root: Path, ref: str) -> bool:
    for note in _read_aging_high_tooling_notes(root):
        key = f"{note['date']} {note['command']}".strip()
        if key == ref:
            return True
    return False


# ── Accept / dismiss ────────────────────────────────────────────────────────────

def accept(root: Path, proposal_id: str, *, confirmed: bool = False) -> AcceptResult:
    """Accept a proposal.

    pick-up: activate the existing ready task (in_progress in backlog + current_task.md,
    create packet if missing) via the workflow_run activation path.
    new-task: ALWAYS require an explicit confirm before creating the packet (D4).
    Accepting an already-resolved signal expires the proposal instead of mutating state.
    """
    proposal = read_proposal(root, proposal_id)
    if proposal is None:
        return AcceptResult(ok=False, errors=[f"proposal not found: {proposal_id}"])

    if proposal.status in (STATUS_DISMISSED, STATUS_EXPIRED, STATUS_ACCEPTED):
        return AcceptResult(
            ok=False,
            proposal_id=proposal_id,
            kind=proposal.kind,
            errors=[f"proposal is {proposal.status}; cannot accept"],
        )

    # Expired-signal guard: if the signal has resolved, expire rather than act.
    if _signal_resolved(root, proposal):
        set_proposal_status(root, proposal_id, STATUS_EXPIRED)
        return AcceptResult(
            ok=False,
            proposal_id=proposal_id,
            kind=proposal.kind,
            expired=True,
            errors=["underlying signal has resolved; proposal expired"],
        )

    if proposal.kind == KIND_PICK_UP:
        return _accept_pickup(root, proposal)
    if proposal.kind == KIND_NEW_TASK:
        return _accept_new_task(root, proposal, confirmed=confirmed)

    return AcceptResult(ok=False, proposal_id=proposal_id, errors=[f"unknown kind: {proposal.kind}"])


def _accept_pickup(root: Path, proposal: SuggestionProposal) -> AcceptResult:
    import grain.cli.output  # noqa: F401  — fully init the cli package first (avoids import cycle)
    from grain.domain.packets import write_packet_status
    from grain.services.workflow_run_service import (
        _create_packet_for_ref,
        _find_packet_dir_for_ref,
        _read_task_id_from_packet,
        _write_backlog_task_status,
        _write_current_task,
    )

    task_ref = proposal.task_ref
    files_created: list[str] = []
    files_updated: list[str] = []

    packet_dir = _find_packet_dir_for_ref(root, task_ref)
    packet_created = False
    if packet_dir is None:
        packet_dir, err = _create_packet_for_ref(root, task_ref)
        if packet_dir is None:
            return AcceptResult(
                ok=False,
                proposal_id=proposal.id,
                kind=proposal.kind,
                task_ref=task_ref,
                errors=[f"packet create failed for {task_ref}: {err}"],
            )
        packet_created = True
        files_created.append(f"tasks/{packet_dir.name}/")

    task_id = _read_task_id_from_packet(packet_dir)
    if task_id:
        write_packet_status(packet_dir, "in_progress")
        _write_backlog_task_status(root / _BACKLOG_PATH, task_ref, "in_progress")
        files_updated.append(_BACKLOG_PATH)
    task_path = f"tasks/{packet_dir.name}/"
    _write_current_task(root, task_id or task_ref, task_path, "in_progress")
    files_updated.append(_CURRENT_TASK_PATH)

    set_proposal_status(root, proposal.id, STATUS_ACCEPTED)

    return AcceptResult(
        ok=True,
        proposal_id=proposal.id,
        kind=proposal.kind,
        task_ref=task_ref,
        task_id=task_id or task_ref,
        files_created=files_created,
        files_updated=files_updated + ([f"tasks/{packet_dir.name}/" ] if packet_created else []),
    )


def _accept_new_task(root: Path, proposal: SuggestionProposal, *, confirmed: bool) -> AcceptResult:
    objective = proposal.objective or proposal.title
    preview = _render_new_task_preview(proposal)

    # D4: new-task accept ALWAYS requires confirmation before any packet is created.
    if not confirmed:
        return AcceptResult(
            ok=False,
            proposal_id=proposal.id,
            kind=proposal.kind,
            needs_confirm=True,
            proposed_task_md=preview,
            errors=["new-task suggestions require confirmation before the packet is created"],
        )

    from grain.services.task_service import create_packet_directory

    phase_num = _phase_number(proposal.suggested_phase) or _active_phase(root)
    try:
        phase = int(phase_num)
    except (TypeError, ValueError):
        return AcceptResult(
            ok=False,
            proposal_id=proposal.id,
            kind=proposal.kind,
            errors=[f"cannot resolve target phase for new-task: {proposal.suggested_phase!r}"],
        )

    task_num = _next_task_num_for_phase(root, phase)
    create_result = create_packet_directory(root, phase=phase, task_num=task_num, title=objective)
    if not create_result.ok:
        return AcceptResult(
            ok=False,
            proposal_id=proposal.id,
            kind=proposal.kind,
            errors=list(create_result.errors),
        )

    set_proposal_status(root, proposal.id, STATUS_ACCEPTED)
    return AcceptResult(
        ok=True,
        proposal_id=proposal.id,
        kind=proposal.kind,
        task_id=create_result.task_id,
        proposed_task_md=preview,
        files_created=list(create_result.files_created),
    )


def _render_new_task_preview(proposal: SuggestionProposal) -> str:
    objective = proposal.objective or proposal.title
    return (
        f"# Task: {objective}\n\n"
        "## Metadata\n"
        "- **Status:** draft\n"
        f"- **Phase:** {proposal.suggested_phase}\n\n"
        "## Objective\n"
        f"{objective}\n\n"
        "## Why This Task Exists\n"
        f"{proposal.rationale}\n\n"
        "## Source Signal\n"
        f"- {proposal.signal}: {proposal.signal_ref}\n"
    )


def _next_task_num_for_phase(root: Path, phase: int) -> int:
    """Return the next T-number for a phase by scanning existing packet dirs."""
    tasks_root = root / "tasks"
    used: list[int] = []
    prefix_re = re.compile(rf"^P{phase}-T(\d+)-")
    if tasks_root.exists():
        for d in tasks_root.iterdir():
            if d.is_dir():
                m = prefix_re.match(d.name)
                if m:
                    used.append(int(m.group(1)))
    return max(used, default=0) + 1


def dismiss(root: Path, proposal_id: str) -> DismissResult:
    """Set proposal status to dismissed (not re-surfaced for the same signal)."""
    proposal = read_proposal(root, proposal_id)
    if proposal is None:
        return DismissResult(ok=False, errors=[f"proposal not found: {proposal_id}"])
    set_proposal_status(root, proposal_id, STATUS_DISMISSED)
    return DismissResult(
        ok=True,
        proposal_id=proposal_id,
        path=str(_proposal_path(root, proposal_id).relative_to(root)),
    )


# ── Prune ───────────────────────────────────────────────────────────────────────

def prune(root: Path, *, dry_run: bool = False, dismissed_max_age_days: int = 30) -> PruneResult:
    """Move expired (always) and old-dismissed (>N days) proposals to the archive.

    Keys off the parsed Status field. Pending and accepted proposals stay put.
    """
    import shutil
    from datetime import timedelta

    working_dir = root / _PROPOSALS_DIR
    archive_dir = root / "docs" / "archive" / "proposals"
    if not working_dir.exists():
        return PruneResult(ok=True, moved=[], dry_run=dry_run)

    now = datetime.now(tz=timezone.utc)
    moved: list[str] = []
    for f in sorted(working_dir.iterdir()):
        if not f.is_file() or not f.name.endswith(".md") or f.name == ".gitkeep":
            continue
        proposal = parse_proposal_md(f.read_text(encoding="utf-8"))
        if proposal is None:
            continue
        eligible = False
        if proposal.status == STATUS_EXPIRED:
            eligible = True
        elif proposal.status == STATUS_DISMISSED:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if now - mtime > timedelta(days=dismissed_max_age_days):
                eligible = True
        if not eligible:
            continue
        moved.append(str(f.relative_to(root)))
        if not dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(archive_dir / f.name))

    return PruneResult(ok=True, moved=moved, dry_run=dry_run)
