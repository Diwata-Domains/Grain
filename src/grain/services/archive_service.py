# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Archive service — working doc snapshots, phase close archives, milestone archives."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from grain.domain.packets import TASK_ID_PATTERN

# ── Archive directory roots ───────────────────────────────────────────────────

_ARCHIVE_ROOT = "docs/archive"
_PHASES_ROOT = "docs/archive/phases"
_MILESTONES_ROOT = "docs/archive/milestones"
_SNAPSHOTS_ROOT = "docs/archive/snapshots"
_PROPOSALS_ROOT = "docs/archive/proposals"

# Working docs captured at phase close
_PHASE_SNAPSHOT_DOCS = [
    "docs/working/backlog.md",
    "docs/working/current_focus.md",
    "docs/working/open_questions.md",
    "docs/working/tooling_notes.md",
]

# Where archived task packets live, relative to the repo root.
_TASKS_ARCHIVE_ROOT = "tasks/archive"

# task.md packet title line, e.g. "# Task: Add foo".
_TASK_TITLE_RE = re.compile(r"^# Task:\s*(.+)$", re.MULTILINE)


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class PhaseArchiveResult:
    ok: bool
    archive_path: str = ""
    files_written: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


@dataclass
class SnapshotResult:
    ok: bool
    archive_path: str = ""
    files_written: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


@dataclass
class MilestoneResult:
    ok: bool
    archive_path: str = ""
    files_written: list[str] = field(default_factory=list)
    tasks_count: int = 0
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


@dataclass
class PhasePacketsResult:
    ok: bool
    phase: str = ""
    archive_path: str = ""
    moved: list[str] = field(default_factory=list)
    tasks_done: int = 0
    packets_archived: int = 0
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False
    skipped: bool = False


@dataclass
class ArchivedPacket:
    task_id: str
    title: str
    path: str


@dataclass
class ArchiveEntry:
    type: str       # "phase" | "milestone" | "snapshot" | "proposals"
    name: str
    path: str
    date: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ArchiveShowResult:
    ok: bool
    name: str = ""
    archive_type: str = ""
    files: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    packets: list[ArchivedPacket] = field(default_factory=list)
    packets_note: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class PruneResult:
    ok: bool
    pruned: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


# ── Phase close snapshot ──────────────────────────────────────────────────────

def archive_phase_docs(
    root: Path,
    phase_num: str,
    tasks_done: int,
    *,
    dry_run: bool = False,
) -> PhaseArchiveResult:
    """Snapshot key working docs to docs/archive/phases/phase-{N}/ at phase close."""
    archive_dir = root / _PHASES_ROOT / f"phase-{phase_num}"

    if dry_run:
        files = [p for p in _PHASE_SNAPSHOT_DOCS if (root / p).exists()]
        return PhaseArchiveResult(
            ok=True,
            archive_path=str(archive_dir.relative_to(root)),
            files_written=files + ["metadata.json"],
            dry_run=True,
        )

    archive_dir.mkdir(parents=True, exist_ok=True)
    files_written: list[str] = []

    for rel in _PHASE_SNAPSHOT_DOCS:
        src = root / rel
        if src.exists():
            dest = archive_dir / src.name
            shutil.copy2(src, dest)
            files_written.append(rel)

    grain_version = _grain_version()
    metadata = {
        "phase": int(phase_num) if phase_num.isdigit() else phase_num,
        "closed_at": date.today().isoformat(),
        "tasks_done": tasks_done,
        "grain_version": grain_version,
    }
    meta_path = archive_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    files_written.append("metadata.json")

    rel_archive = str(archive_dir.relative_to(root))
    return PhaseArchiveResult(
        ok=True,
        archive_path=rel_archive,
        files_written=files_written,
    )


# ── Phase close packet archive ─────────────────────────────────────────────────

def move_phase_packets(
    root: Path,
    phase: str,
    *,
    keep_tasks: bool = False,
    dry_run: bool = False,
) -> PhasePacketsResult:
    """Move active ``tasks/P{N}-*`` packets to ``tasks/archive/phase-{N}/``.

    Records the archive location (``tasks_archive``) and a count of archived
    packet directories (``packets_archived_count``) on the phase metadata.json
    that ``archive_phase_docs`` writes — it never touches the canonical
    backlog-derived ``tasks_done`` that ``archive_phase_docs`` already set
    (the two counts are independent: a done task may have no packet dir, and
    stale/duplicate packet dirs may exist, so the packet count is a poor proxy
    for completed tasks). Moves (never copies) so the active ``tasks/``
    directory stays clean, and is idempotent: re-running after a successful
    move is a no-op. ``keep_tasks=True`` leaves packets in place. Degrades
    gracefully when no packets match (pre-v0.4.0 or empty phase).
    """
    phase_num = str(phase)
    tasks_dir = root / "tasks"
    archive_dir = root / _TASKS_ARCHIVE_ROOT / f"phase-{phase_num}"
    rel_archive = str(archive_dir.relative_to(root))

    if keep_tasks:
        return PhasePacketsResult(
            ok=True,
            phase=phase_num,
            archive_path=rel_archive,
            moved=[],
            tasks_done=0,
            packets_archived=0,
            dry_run=dry_run,
            skipped=True,
        )

    packets = _find_phase_packets(tasks_dir, phase_num)

    # Already-archived packets count toward the archived-packet tally for
    # idempotent re-runs.
    already_archived = _find_phase_packets(archive_dir, phase_num) if archive_dir.exists() else []
    packets_count = len(packets) + len(already_archived)

    if dry_run:
        moved = [str(p.relative_to(root)) for p in sorted(packets)]
        return PhasePacketsResult(
            ok=True,
            phase=phase_num,
            archive_path=rel_archive,
            moved=moved,
            tasks_done=packets_count,
            packets_archived=packets_count,
            dry_run=True,
        )

    # Build the moved list incrementally so a mid-loop collision reports only
    # the packets actually moved (the unprocessed tail still sits in tasks/).
    moved: list[str] = []
    if packets:
        archive_dir.mkdir(parents=True, exist_ok=True)
        for packet_dir in sorted(packets):
            dest = archive_dir / packet_dir.name
            rel_packet = str(packet_dir.relative_to(root))
            if dest.exists():
                # Never lose a packet: refuse to clobber an existing archive entry.
                return PhasePacketsResult(
                    ok=False,
                    phase=phase_num,
                    archive_path=rel_archive,
                    moved=moved,
                    tasks_done=packets_count,
                    packets_archived=len(moved) + len(already_archived),
                    errors=[
                        f"archive destination already exists: {dest.relative_to(root)} "
                        f"— refusing to overwrite {packet_dir.relative_to(root)}"
                    ],
                )
            shutil.move(str(packet_dir), str(dest))
            moved.append(rel_packet)

    _update_phase_metadata_tasks(root, phase_num, packets_count, rel_archive)

    return PhasePacketsResult(
        ok=True,
        phase=phase_num,
        archive_path=rel_archive,
        moved=moved,
        tasks_done=packets_count,
        packets_archived=packets_count,
    )


def _find_phase_packets(parent: Path, phase_num: str) -> list[Path]:
    """Return ``P{N}-T*`` packet directories that are immediate children of parent."""
    if not parent.exists():
        return []
    prefix = f"P{phase_num}-T"
    return [p for p in parent.iterdir() if p.is_dir() and p.name.startswith(prefix)]


def _update_phase_metadata_tasks(
    root: Path,
    phase_num: str,
    packets_archived: int,
    tasks_archive: str,
) -> None:
    """Record tasks_archive + packets_archived_count on the phase metadata.json.

    Best effort. Crucially this never overwrites the canonical, backlog-derived
    ``tasks_done`` that ``archive_phase_docs`` wrote — that value drives the
    metrics service's closure_rate and total_tasks_done. The packet-directory
    tally is recorded under a distinct ``packets_archived_count`` field.
    """
    meta_path = root / _PHASES_ROOT / f"phase-{phase_num}" / "metadata.json"
    meta = _read_metadata(meta_path.parent)
    meta["tasks_archive"] = tasks_archive
    meta["packets_archived_count"] = packets_archived
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


# ── Snapshot ──────────────────────────────────────────────────────────────────

def snapshot_working_docs(
    root: Path,
    label: str | None = None,
    *,
    dry_run: bool = False,
) -> SnapshotResult:
    """Copy docs/working/ to docs/archive/snapshots/<YYYYMMDD>-<label|seq>/."""
    today = date.today().strftime("%Y%m%d")
    snapshots_root = root / _SNAPSHOTS_ROOT

    if label:
        dir_name = f"{today}-{label}"
    else:
        # auto-increment sequence
        seq = _next_snapshot_seq(snapshots_root, today)
        dir_name = f"{today}-{seq:03d}"

    archive_dir = snapshots_root / dir_name
    working_dir = root / "docs" / "working"

    if dry_run:
        files = [str(p.relative_to(root)) for p in working_dir.rglob("*") if p.is_file()] if working_dir.exists() else []
        return SnapshotResult(
            ok=True,
            archive_path=str(archive_dir.relative_to(root)),
            files_written=files,
            dry_run=True,
        )

    if not working_dir.exists():
        return SnapshotResult(ok=False, errors=["docs/working/ does not exist"])

    archive_dir.mkdir(parents=True, exist_ok=True)
    files_written: list[str] = []

    for src in working_dir.rglob("*"):
        if src.is_file():
            rel = src.relative_to(working_dir)
            dest = archive_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            files_written.append(str(src.relative_to(root)))

    return SnapshotResult(
        ok=True,
        archive_path=str(archive_dir.relative_to(root)),
        files_written=files_written,
    )


def _next_snapshot_seq(snapshots_root: Path, today: str) -> int:
    if not snapshots_root.exists():
        return 1
    existing = [d.name for d in snapshots_root.iterdir() if d.is_dir() and d.name.startswith(today)]
    if not existing:
        return 1
    nums: list[int] = []
    for name in existing:
        m = re.search(r"-(\d{3})$", name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums, default=0) + 1


# ── Milestone archive ─────────────────────────────────────────────────────────

def archive_milestone(
    root: Path,
    version: str,
    *,
    dry_run: bool = False,
) -> MilestoneResult:
    """Create docs/archive/milestones/<version>/ with working/, canonical/, tasks_index, metadata."""
    archive_dir = root / _MILESTONES_ROOT / version
    working_dir = root / "docs" / "working"
    canonical_dir = root / "docs" / "canonical"

    if archive_dir.exists() and not dry_run:
        return MilestoneResult(
            ok=False,
            errors=[f"milestone archive already exists: {archive_dir.relative_to(root)}"],
        )

    tasks_index = _build_tasks_index(root)

    if dry_run:
        files = (
            [str(p.relative_to(root)) for p in working_dir.rglob("*") if p.is_file()]
            + [str(p.relative_to(root)) for p in canonical_dir.rglob("*") if p.is_file()]
            + ["tasks_index.json", "metadata.json"]
        ) if working_dir.exists() else ["tasks_index.json", "metadata.json"]
        return MilestoneResult(
            ok=True,
            archive_path=str(archive_dir.relative_to(root)),
            files_written=files,
            tasks_count=len(tasks_index),
            dry_run=True,
        )

    archive_dir.mkdir(parents=True, exist_ok=True)
    files_written: list[str] = []

    for src_dir, dest_name in [(working_dir, "working"), (canonical_dir, "canonical")]:
        if src_dir.exists():
            dest = archive_dir / dest_name
            dest.mkdir(exist_ok=True)
            for src in src_dir.rglob("*"):
                if src.is_file():
                    rel = src.relative_to(src_dir)
                    target = dest / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)
                    files_written.append(str(src.relative_to(root)))

    idx_path = archive_dir / "tasks_index.json"
    idx_path.write_text(json.dumps(tasks_index, indent=2), encoding="utf-8")
    files_written.append("tasks_index.json")

    metadata = {
        "version": version,
        "archived_at": date.today().isoformat(),
        "tasks_count": len(tasks_index),
        "grain_version": _grain_version(),
    }
    meta_path = archive_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    files_written.append("metadata.json")

    return MilestoneResult(
        ok=True,
        archive_path=str(archive_dir.relative_to(root)),
        files_written=files_written,
        tasks_count=len(tasks_index),
    )


def _build_tasks_index(root: Path) -> list[dict]:
    tasks_root = root / "tasks"
    if not tasks_root.exists():
        return []
    index: list[dict] = []
    _PACKET_RE = re.compile(r"^(P\d+-T\d+)-(TASK-\d+)$")
    for d in sorted(tasks_root.iterdir()):
        if not d.is_dir():
            continue
        m = _PACKET_RE.match(d.name)
        if not m:
            continue
        task_ref, task_id = m.group(1), m.group(2)
        task_md = d / "task.md"
        status = ""
        if task_md.exists():
            from grain.domain.packets import parse_task_metadata
            meta = parse_task_metadata(task_md)
            status = meta.get("status", "")
        index.append({
            "task_ref": task_ref,
            "task_id": task_id,
            "packet_path": f"tasks/{d.name}/",
            "status": status,
            "has_results": (d / "results.md").exists(),
        })
    return index


# ── List archives ─────────────────────────────────────────────────────────────

def list_archives(
    root: Path,
    type_filter: str | None = None,
) -> list[ArchiveEntry]:
    """Return all archive entries sorted by date descending."""
    entries: list[ArchiveEntry] = []
    archive_root = root / _ARCHIVE_ROOT

    if not archive_root.exists():
        return []

    # Phases
    if not type_filter or type_filter == "phase":
        phases_dir = archive_root / "phases"
        if phases_dir.exists():
            for d in sorted(phases_dir.iterdir()):
                if d.is_dir():
                    meta = _read_metadata(d)
                    entries.append(ArchiveEntry(
                        type="phase",
                        name=d.name,
                        path=str(d.relative_to(root)),
                        date=meta.get("closed_at", ""),
                        metadata=meta,
                    ))

    # Milestones
    if not type_filter or type_filter == "milestone":
        milestones_dir = archive_root / "milestones"
        if milestones_dir.exists():
            for d in sorted(milestones_dir.iterdir()):
                if d.is_dir():
                    meta = _read_metadata(d)
                    entries.append(ArchiveEntry(
                        type="milestone",
                        name=d.name,
                        path=str(d.relative_to(root)),
                        date=meta.get("archived_at", ""),
                        metadata=meta,
                    ))

    # Snapshots
    if not type_filter or type_filter == "snapshot":
        snapshots_dir = archive_root / "snapshots"
        if snapshots_dir.exists():
            for d in sorted(snapshots_dir.iterdir()):
                if d.is_dir():
                    date_str = d.name[:8] if len(d.name) >= 8 else ""
                    label = d.name[9:] if len(d.name) > 9 else ""
                    entries.append(ArchiveEntry(
                        type="snapshot",
                        name=d.name,
                        path=str(d.relative_to(root)),
                        date=_format_date(date_str),
                        metadata={"label": label},
                    ))

    entries.sort(key=lambda e: e.date or "0000-00-00", reverse=True)
    return entries


def _read_metadata(archive_dir: Path) -> dict:
    meta_file = archive_dir / "metadata.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _format_date(yyyymmdd: str) -> str:
    if len(yyyymmdd) == 8:
        return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}"
    return yyyymmdd


# ── Show archive ──────────────────────────────────────────────────────────────

def show_archive(root: Path, target: str) -> ArchiveShowResult:
    """Show contents and metadata of an archive by name or path."""
    archive_dir, archive_type = _resolve_archive_target(root, target)
    if archive_dir is None:
        return ArchiveShowResult(
            ok=False,
            errors=[f"archive not found: {target!r}"],
        )

    files = [str(p.relative_to(archive_dir)) for p in sorted(archive_dir.rglob("*")) if p.is_file()]
    metadata = _read_metadata(archive_dir)

    packets: list[ArchivedPacket] = []
    packets_note = ""
    if archive_type == "phase":
        packets, packets_note = _read_archived_packets(root, metadata)

    return ArchiveShowResult(
        ok=True,
        name=archive_dir.name,
        archive_type=archive_type,
        files=files,
        metadata=metadata,
        packets=packets,
        packets_note=packets_note,
    )


def _read_archived_packets(root: Path, metadata: dict) -> tuple[list[ArchivedPacket], str]:
    """Enumerate archived task packets for a phase from its tasks_archive path.

    Returns (packets, note). Degrades gracefully for phases closed before
    v0.4.0 (no ``tasks_archive`` in metadata, or the directory is absent),
    returning an empty list plus an explanatory note rather than erroring.
    """
    tasks_archive = metadata.get("tasks_archive")
    if not tasks_archive:
        return [], "no task archive (phase closed before packet archiving)"

    archive_dir = root / tasks_archive
    if not archive_dir.exists():
        return [], f"task archive not found: {tasks_archive}"

    packets: list[ArchivedPacket] = []
    for packet_dir in sorted(archive_dir.iterdir()):
        if not packet_dir.is_dir():
            continue
        m = TASK_ID_PATTERN.search(packet_dir.name)
        task_id = f"TASK-{m.group(1)}" if m else packet_dir.name
        title = _read_task_title(packet_dir / "task.md")
        packets.append(ArchivedPacket(
            task_id=task_id,
            title=title,
            path=str(packet_dir.relative_to(root)),
        ))
    return packets, ""


def _read_task_title(task_md: Path) -> str:
    """Return the ``# Task: <title>`` heading from a task.md ('' if absent)."""
    if not task_md.exists():
        return ""
    m = _TASK_TITLE_RE.search(task_md.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else ""


def _resolve_archive_target(root: Path, target: str) -> tuple[Path | None, str]:
    """Try to find archive dir by target name across all archive surfaces."""
    searches = [
        (root / _PHASES_ROOT / target, "phase"),
        (root / _MILESTONES_ROOT / target, "milestone"),
        (root / _SNAPSHOTS_ROOT / target, "snapshot"),
    ]
    for d, archive_type in searches:
        if d.exists() and d.is_dir():
            return d, archive_type
    # Try prefix match on snapshots
    snapshots_root = root / _SNAPSHOTS_ROOT
    if snapshots_root.exists():
        for d in snapshots_root.iterdir():
            if d.is_dir() and (d.name.startswith(target) or target in d.name):
                return d, "snapshot"
    return None, ""


# ── Prune archived proposals ──────────────────────────────────────────────────

def prune_archived_proposals(
    root: Path,
    older_than_days: int,
    *,
    dry_run: bool = False,
) -> PruneResult:
    """Remove files from docs/archive/proposals/ older than N days."""
    proposals_dir = root / _PROPOSALS_ROOT
    if not proposals_dir.exists():
        return PruneResult(ok=True, pruned=[])

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=older_than_days)
    pruned: list[str] = []

    for f in sorted(proposals_dir.iterdir()):
        if f.is_file():
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                pruned.append(str(f.relative_to(root)))
                if not dry_run:
                    f.unlink()

    return PruneResult(ok=True, pruned=pruned, dry_run=dry_run)


def move_working_proposals_to_archive(
    root: Path,
    older_than_days: int = 30,
    *,
    dry_run: bool = False,
) -> PruneResult:
    """Move dismissed/expired proposals from docs/working/proposals/ to docs/archive/proposals/."""
    working_proposals = root / "docs" / "working" / "proposals"
    archive_proposals = root / _PROPOSALS_ROOT

    if not working_proposals.exists():
        return PruneResult(ok=True, pruned=[])

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=older_than_days)
    pruned: list[str] = []

    for f in sorted(working_proposals.iterdir()):
        if not f.is_file() or f.name == ".gitkeep":
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        status = _parse_proposal_status(f.read_text(encoding="utf-8"))
        # Lifecycle: expired proposals are always eligible; dismissed ones only
        # once they have aged past the cutoff. Pending/accepted stay in place.
        eligible = status == "expired" or (status == "dismissed" and mtime < cutoff)
        if eligible:
            pruned.append(str(f.relative_to(root)))
            if not dry_run:
                archive_proposals.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f), archive_proposals / f.name)

    return PruneResult(ok=True, pruned=pruned, dry_run=dry_run)


_PROPOSAL_STATUS_RE = re.compile(r"^\**Status:\**\s*(\w+)", re.IGNORECASE)


def _parse_proposal_status(text: str) -> str:
    """Return the lowercased Status field from a proposal file ('' if absent).

    Matches both '**Status:** dismissed' and plain 'Status: dismissed'.
    """
    for line in text.splitlines():
        m = _PROPOSAL_STATUS_RE.match(line.strip())
        if m:
            return m.group(1).lower()
    return ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _grain_version() -> str:
    try:
        from importlib.metadata import version
        return version("grain-kit")
    except Exception:
        try:
            import tomllib
            pyproject = Path(__file__).resolve().parents[3] / "pyproject.toml"
            with pyproject.open("rb") as f:
                return tomllib.load(f)["project"]["version"]
        except Exception:
            return "0.0.0"
