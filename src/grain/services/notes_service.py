# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Notes service — read/write the queryable friction inbox.

Backs ``grain notes`` against the single human-readable file
``docs/working/tooling_notes.md``. Rows are stored as markdown table rows with
an auto-incremented ID, timestamp, and a default ``open`` status. Legacy rows
written before IDs existed are normalized on read so they remain addressable
without ever being dropped.
"""

from __future__ import annotations

import atexit
import hashlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _dist_version
from pathlib import Path

from grain.domain.notes import (
    TABLE_HEADER,
    TABLE_SEP,
    Note,
    parse_note_line,
)

_NOTES_PATH = "docs/working/tooling_notes.md"

_FILE_PREAMBLE = (
    "# Tooling Notes\n\n"
    "Lightweight inbox for workflow friction, tool bugs, or observations noticed mid-session.\n"
    "Agents write here; user reviews and escalates to the appropriate tracker.\n\n"
)


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class NoteAddResult:
    ok: bool
    note: Note | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class NoteListResult:
    ok: bool
    notes: list[Note] = field(default_factory=list)
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class NoteShowResult:
    ok: bool
    note: Note | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class NoteResolveResult:
    ok: bool
    note: Note | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class NoteStatusResult:
    ok: bool
    note: Note | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


# ── Public API ────────────────────────────────────────────────────────────────

def add_note(
    root: Path,
    body: str,
    *,
    note_type: str = "friction",
    command: str = "",
    severity: str = "low",
) -> NoteAddResult:
    """Append a structured note with an auto ID, timestamp, and ``open`` status."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))

    text = body.strip()
    if not text:
        return NoteAddResult(ok=False, path=rel, errors=["note body is empty"])

    existing = _read_notes(path)
    next_id = (max((n.id for n in existing), default=0)) + 1

    note = Note(
        id=next_id,
        created_at=date.today().isoformat(),
        type=note_type,
        command=command,
        body=text,
        severity=severity,
        status="open",
    )

    # Persist the new row alongside the normalized existing rows. Rewriting (vs a
    # blind append) gives any legacy rows the synthesized IDs they were already
    # being shown under, so a row's ID stays stable across subsequent adds and
    # remains addressable via show/resolve. Original row order is preserved.
    if existing:
        _rewrite_notes(path, existing + [note])
    else:
        _ensure_table(path)
        _append_row(path, note.to_row())
    return NoteAddResult(ok=True, note=note, path=rel)


def list_notes(
    root: Path,
    *,
    type_filter: str | None = None,
    status_filter: str | None = None,
) -> NoteListResult:
    """Return notes filtered by type and/or status (default: open only)."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))
    if not path.exists():
        return NoteListResult(ok=True, notes=[], path=rel)

    notes = _read_notes(path)
    effective_status = "open" if status_filter is None else status_filter

    selected: list[Note] = []
    for n in notes:
        if type_filter and n.type != type_filter:
            continue
        if effective_status != "all" and n.status != effective_status:
            continue
        selected.append(n)
    return NoteListResult(ok=True, notes=selected, path=rel)


def show_note(root: Path, note_id: int) -> NoteShowResult:
    """Return a single note by ID."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))
    if not path.exists():
        return NoteShowResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    for n in _read_notes(path):
        if n.id == note_id:
            return NoteShowResult(ok=True, note=n, path=rel)
    return NoteShowResult(ok=False, path=rel, errors=[f"note {note_id} not found"])


def resolve_note(root: Path, note_id: int, resolution: str = "") -> NoteResolveResult:
    """Flip a note to ``resolved`` and optionally append a resolution note."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))
    if not path.exists():
        return NoteResolveResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    notes = _read_notes(path)
    target = next((n for n in notes if n.id == note_id), None)
    if target is None:
        return NoteResolveResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    if target.status == "resolved":
        return NoteResolveResult(
            ok=False, note=target, path=rel,
            errors=[f"note {note_id} is already resolved"],
        )

    target.status = "resolved"
    if resolution.strip():
        suffix = f" — resolved: {resolution.strip()}"
        if suffix not in target.body:
            target.body = f"{target.body}{suffix}"

    _rewrite_notes(path, notes)
    return NoteResolveResult(ok=True, note=target, path=rel)


def set_note_status(root: Path, note_id: int, status: str) -> NoteStatusResult:
    """Flip a note to an arbitrary status (e.g. ``reported``, ``published``).

    Used by ``grain report`` (URL path) and ``grain notes publish`` (API path) to
    mark a row after it has been escalated upstream. Returns ``ok=False`` with an
    error if the note does not exist.
    """
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))
    if not path.exists():
        return NoteStatusResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    notes = _read_notes(path)
    target = next((n for n in notes if n.id == note_id), None)
    if target is None:
        return NoteStatusResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    target.status = status
    _rewrite_notes(path, notes)
    return NoteStatusResult(ok=True, note=target, path=rel)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_notes(path: Path) -> list[Note]:
    """Parse every data row from the notes file, normalizing legacy rows.

    Rows are returned in their ORIGINAL file order so the human-readable inbox
    is never silently reordered (e.g. by a resolve). Legacy (un-IDed) rows are
    assigned synthesized IDs above the explicit max so they do not collide with
    explicit IDs already present in the file.
    """
    if not path.exists():
        return []

    parsed: list[Note] = []
    legacy_idx: list[int] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        note = parse_note_line(line, fallback_id=-1)
        if note is None:
            continue
        if note.id == -1:
            legacy_idx.append(len(parsed))
        parsed.append(note)

    # Allocate synthesized IDs for legacy rows above the explicit max, in file
    # order, without moving any row out of its original position.
    next_synth = (
        max((n.id for n in parsed if n.id != -1), default=0)
    ) + 1
    for idx in legacy_idx:
        parsed[idx].id = next_synth
        next_synth += 1

    return parsed


def _ensure_table(path: Path) -> None:
    """Create the file (or append a structured header) if needed."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{_FILE_PREAMBLE}{TABLE_HEADER}\n{TABLE_SEP}\n", encoding="utf-8")
        return

    content = path.read_text(encoding="utf-8")
    if TABLE_HEADER not in content:
        path.write_text(
            content.rstrip("\n") + f"\n\n{TABLE_HEADER}\n{TABLE_SEP}\n",
            encoding="utf-8",
        )


def _append_row(path: Path, row: str) -> None:
    content = path.read_text(encoding="utf-8")
    sep_pos = content.find(TABLE_SEP)
    if sep_pos != -1:
        insert_pos = sep_pos + len(TABLE_SEP)
        content = content[:insert_pos] + "\n" + row + content[insert_pos:]
    else:
        content = content.rstrip("\n") + "\n" + row + "\n"
    path.write_text(content, encoding="utf-8")


def _rewrite_notes(path: Path, notes: list[Note]) -> None:
    """Rewrite the file: preserve the preamble, regenerate the table.

    Every prose/blank line before the first table line is kept verbatim; the
    table itself is rebuilt from ``notes`` (in their normalized, ID'd form) so
    resolves and legacy-row normalization persist. This collapses any legacy
    six-column rows into the canonical seven-column schema.
    """
    preamble: list[str] = []
    seen_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("|"):
            seen_table = True
            break
        preamble.append(line)

    out_lines: list[str] = []
    out_lines.extend(preamble)
    if not seen_table and preamble and preamble[-1].strip():
        out_lines.append("")
    out_lines.append(TABLE_HEADER)
    out_lines.append(TABLE_SEP)
    for n in notes:
        out_lines.append(n.to_row())

    path.write_text("\n".join(out_lines).rstrip("\n") + "\n", encoding="utf-8")


# ── Triage & fleet (P38-T10) ──────────────────────────────────────────────────
#
# The inbox is only useful if it drains. `triage` replays each open note's
# recorded command in a *throwaway* workspace and classifies it; `--fleet` rolls
# many workspaces up into one finding per defect. Replay is deliberately a
# HEURISTIC and conservative: a note becomes a closure candidate only when its
# command now exits 0. Anything that still errors — for ANY reason — stays open,
# so an unrelated failure can never silently close a real note.

# Triage verdicts for one replayed note.
TRIAGE_STALE = "stale"   # command replayed clean (exit 0) — candidate for closure
TRIAGE_OPEN = "open"     # command still errors — stays open (conservative)
TRIAGE_HUMAN = "human"   # not replayable (no command / free prose / unsafe)

# Observation prefixes are compared over this many normalized characters when
# deciding whether two rows describe the same defect.
_OBS_PREFIX_LEN = 60

_ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# Shell plumbing we refuse to replay because we cannot reproduce it faithfully.
_SHELL_META = re.compile(r"&&|\|\||[;|<>`]|\$\(")
# Interactive / agent- or server-spawning subcommands: unsafe and pointless to
# replay headlessly, so they route to a human instead.
_UNSAFE_SINGLE: frozenset[str] = frozenset({"tui", "mcp", "orchestrate"})
_UNSAFE_PAIR: frozenset[tuple[str, str]] = frozenset(
    {("workflow", "run"), ("recipe", "run")}
)
# Global options that consume the following token (so it is not a subcommand).
_GLOBAL_VALUE_OPTS: frozenset[str] = frozenset({"--repo", "--format"})

_REPLAY_BOOTSTRAP = "import sys; from grain.cli import cli; cli()"
_MARKER_REL = ("docs", "runtime", "PROJECT_RULES.md")


@dataclass
class ReplayOutcome:
    """Outcome of replaying one note's command in a throwaway workspace."""

    replayable: bool
    exit_code: int | None = None
    command: str = ""   # the normalized `grain …` actually run, or "" if none
    detail: str = ""    # why it was not replayable / any diagnostic


@dataclass
class TriageItem:
    """One triaged note (local) or one deduped finding (fleet)."""

    note: Note
    verdict: str
    replay: ReplayOutcome
    workspaces: list[str] = field(default_factory=list)
    note_refs: list[tuple[str, int]] = field(default_factory=list)
    resolved: int = 0


@dataclass
class TriageResult:
    ok: bool
    items: list[TriageItem] = field(default_factory=list)
    version: str = ""
    dry_run: bool = True
    fleet: bool = False
    resolved_count: int = 0
    path: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def stale(self) -> list[TriageItem]:
        return [i for i in self.items if i.verdict == TRIAGE_STALE]

    @property
    def still_open(self) -> list[TriageItem]:
        return [i for i in self.items if i.verdict == TRIAGE_OPEN]

    @property
    def needs_human(self) -> list[TriageItem]:
        return [i for i in self.items if i.verdict == TRIAGE_HUMAN]


@dataclass
class FleetFinding:
    """One defect, normalized across every workspace it was seen in."""

    command: str
    observation: str
    type: str
    severity: str
    count: int
    workspaces: list[str]
    note_refs: list[tuple[str, int]] = field(default_factory=list)


@dataclass
class FleetResult:
    ok: bool
    findings: list[FleetFinding] = field(default_factory=list)
    discovered: int = 0        # inbox files found in a canonical location
    workspaces: int = 0        # distinct workspaces kept after exclusions
    skipped_archive: int = 0   # docs/archive/** snapshots
    skipped_template: int = 0  # untouched template inboxes (no data rows)
    skipped_worktree: int = 0  # identical-content copies collapsed
    errors: list[str] = field(default_factory=list)


# ── Command replay ────────────────────────────────────────────────────────────

def _subcommand_head(argv: list[str]) -> tuple[str, ...]:
    """Return up to the first two positional tokens (the subcommand path).

    Global options and the values they consume (``--repo X``, ``--format X``)
    are skipped so ``grain --format json workflow next`` yields
    ``("workflow", "next")``.
    """
    positionals: list[str] = []
    skip_next = False
    for tok in argv:
        if skip_next:
            skip_next = False
            continue
        if tok.startswith("-"):
            if "=" not in tok and tok in _GLOBAL_VALUE_OPTS:
                skip_next = True
            continue
        positionals.append(tok)
        if len(positionals) == 2:
            break
    return tuple(positionals)


def parse_replay_command(raw: str) -> list[str] | None:
    """Return the ``grain`` argv to replay, or ``None`` if not replayable.

    Replayable means the cell reduces to a single ``grain <args>`` invocation
    with no shell plumbing. We refuse anything we cannot reproduce faithfully —
    empty cells, free prose, ``a | b`` pipelines, and interactive/agent-spawning
    subcommands — so triage routes them to a human rather than guessing.
    """
    text = (raw or "").strip()
    if not text or text == "—":
        return None
    # A cell may record equivalent alternatives ("`a` / `b`"); replay the first.
    if " / " in text:
        text = text.split(" / ", 1)[0]
    text = text.strip().strip("`").strip()
    if not text or _SHELL_META.search(text):
        return None
    try:
        tokens = shlex.split(text)
    except ValueError:
        return None
    idx = 0
    while idx < len(tokens) and _ENV_ASSIGN.match(tokens[idx]):
        idx += 1
    tokens = tokens[idx:]
    if not tokens or tokens[0] != "grain":
        return None
    argv = tokens[1:]
    head = _subcommand_head(argv)
    if head and head[0] in _UNSAFE_SINGLE:
        return None
    if tuple(head[:2]) in _UNSAFE_PAIR:
        return None
    return argv


class _ThrowawayReplayer:
    """Replay commands in throwaway grain workspaces.

    ``grain init`` runs once (≈0.5s) to build a template; each replay then runs
    in a fresh copy so a mutating command (``phase close``) cannot leak state
    into the next replay. The template is removed at interpreter exit.
    """

    def __init__(self, *, timeout: int = 45) -> None:
        self._template: Path | None = None
        self._failed = False
        self._timeout = timeout

    def _ensure_template(self) -> Path | None:
        if self._template is not None or self._failed:
            return self._template
        try:
            base = Path(tempfile.mkdtemp(prefix="grain-triage-tpl-"))
            proc = subprocess.run(
                [
                    sys.executable, "-c", _REPLAY_BOOTSTRAP, "--repo", str(base),
                    "init", "--name", "triage-replay", "--type", "cli_tool",
                ],
                capture_output=True, text=True, timeout=120,
            )
            if proc.returncode != 0 or not base.joinpath(*_MARKER_REL).exists():
                shutil.rmtree(base, ignore_errors=True)
                self._failed = True
                return None
            atexit.register(shutil.rmtree, str(base), ignore_errors=True)
            self._template = base
        except Exception:
            self._failed = True
        return self._template

    def __call__(self, command: str) -> ReplayOutcome:
        argv = parse_replay_command(command)
        if argv is None:
            return ReplayOutcome(
                replayable=False, command=command,
                detail="no replayable grain command",
            )
        template = self._ensure_template()
        if template is None:
            return ReplayOutcome(
                replayable=False, command=command,
                detail="could not initialize a throwaway workspace",
            )
        workspace = Path(tempfile.mkdtemp(prefix="grain-triage-ws-"))
        shutil.rmtree(workspace, ignore_errors=True)
        pretty = "grain " + " ".join(argv)
        try:
            shutil.copytree(template, workspace)
            proc = subprocess.run(
                [sys.executable, "-c", _REPLAY_BOOTSTRAP, *argv],
                cwd=str(workspace), capture_output=True, text=True,
                timeout=self._timeout,
            )
            return ReplayOutcome(
                replayable=True, exit_code=proc.returncode, command=pretty,
            )
        except subprocess.TimeoutExpired:
            return ReplayOutcome(
                replayable=True, exit_code=124, command=pretty,
                detail="timed out",
            )
        except Exception as exc:  # pragma: no cover - defensive
            return ReplayOutcome(
                replayable=False, command=command, detail=f"replay error: {exc}",
            )
        finally:
            shutil.rmtree(workspace, ignore_errors=True)


def make_default_replayer(*, timeout: int = 45) -> Callable[[str], ReplayOutcome]:
    """Return a replay callable backed by a reusable throwaway workspace."""
    return _ThrowawayReplayer(timeout=timeout)


def _current_version() -> str:
    try:
        return _dist_version("grain-kit")
    except PackageNotFoundError:
        return "unknown"


def _verdict_for(outcome: ReplayOutcome) -> str:
    if not outcome.replayable:
        return TRIAGE_HUMAN
    return TRIAGE_STALE if outcome.exit_code == 0 else TRIAGE_OPEN


def _stale_resolution(version: str) -> str:
    return f"stale on replay — command no longer errors as of grain {version}"


# ── Local triage ──────────────────────────────────────────────────────────────

def triage_notes(
    root: Path,
    *,
    replay: Callable[[str], ReplayOutcome] | None = None,
    resolve_stale: bool = False,
    type_filter: str | None = None,
    status_filter: str | None = None,
    version: str | None = None,
) -> TriageResult:
    """Replay every open note's command and classify it stale/open/human.

    ``replay`` defaults to a real throwaway-workspace replayer; tests inject a
    deterministic stub. Triage is DRY-RUN by default — ``resolve_stale`` flips
    the stale candidates to ``resolved`` via the normal resolve path, recording
    the grain version that no longer reproduces them.
    """
    rel = str(Path(_NOTES_PATH))
    listed = list_notes(root, type_filter=type_filter, status_filter=status_filter)
    ver = version if version is not None else _current_version()
    if replay is None:
        replay = make_default_replayer()

    items: list[TriageItem] = []
    resolved_total = 0
    for note in listed.notes:
        outcome = replay(note.command)
        verdict = _verdict_for(outcome)
        item = TriageItem(
            note=note, verdict=verdict, replay=outcome,
            workspaces=[root.as_posix()], note_refs=[(root.as_posix(), note.id)],
        )
        if resolve_stale and verdict == TRIAGE_STALE:
            res = resolve_note(root, note.id, _stale_resolution(ver))
            if res.ok:
                item.resolved = 1
                resolved_total += 1
        items.append(item)

    return TriageResult(
        ok=True, items=items, version=ver, dry_run=not resolve_stale,
        fleet=False, resolved_count=resolved_total, path=rel,
    )


# ── Fleet scan & fleet triage ─────────────────────────────────────────────────

def _norm_command(command: str) -> str:
    return " ".join(command.replace("`", " ").split()).lower()


def _obs_prefix(body: str) -> str:
    return " ".join(body.split()).lower()[:_OBS_PREFIX_LEN]


def _note_selected(
    note: Note, type_filter: str | None, status_filter: str | None,
) -> bool:
    effective_status = "open" if status_filter is None else status_filter
    if type_filter and note.type != type_filter:
        return False
    if effective_status != "all" and note.status != effective_status:
        return False
    return True


def _discover_inboxes(roots: list[Path]) -> tuple[list[Path], int]:
    """Return (kept-inbox-paths, skipped_archive_count).

    Only files at the canonical ``<ws>/docs/working/tooling_notes.md`` location
    are considered; ``docs/archive/**`` snapshots are counted and excluded.
    Paths are de-duplicated across overlapping roots and returned sorted so the
    lexicographically-smallest workspace becomes the canonical worktree copy.
    """
    found: dict[str, Path] = {}
    for root in roots:
        base = Path(root)
        if not base.exists():
            continue
        for path in base.rglob("tooling_notes.md"):
            if path.parent.name != "working" or path.parent.parent.name != "docs":
                continue
            resolved = path.resolve()
            found.setdefault(resolved.as_posix(), resolved)

    kept: list[Path] = []
    skipped_archive = 0
    for path in sorted(found.values(), key=lambda p: p.as_posix()):
        if "/docs/archive/" in path.as_posix():
            skipped_archive += 1
            continue
        kept.append(path)
    return kept, skipped_archive


def scan_fleet(
    roots: list[Path],
    *,
    type_filter: str | None = None,
    status_filter: str | None = None,
) -> FleetResult:
    """Walk each root and roll notes up into one finding per defect.

    Excludes docs/archive snapshots, collapses identical-content (worktree)
    copies by hash, and drops untouched template inboxes. Findings are keyed by
    (normalized command, observation prefix) and carry the distinct set of
    workspaces the defect was seen in.
    """
    result = FleetResult(ok=True)
    inboxes, result.skipped_archive = _discover_inboxes(roots)
    result.discovered = len(inboxes) + result.skipped_archive

    kept: list[tuple[Path, list[Note]]] = []
    seen_hash: set[str] = set()
    for path in inboxes:
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        notes = _read_notes(path)
        if not notes:
            result.skipped_template += 1
            continue
        digest = hashlib.sha256(raw).hexdigest()
        if digest in seen_hash:
            result.skipped_worktree += 1
            continue
        seen_hash.add(digest)
        workspace = path.parent.parent.parent  # working -> docs -> workspace
        kept.append((workspace, notes))

    result.workspaces = len(kept)

    groups: dict[tuple[str, str], FleetFinding] = {}
    order: list[tuple[str, str]] = []
    for workspace, notes in kept:
        ws_id = workspace.as_posix()
        for note in notes:
            if not _note_selected(note, type_filter, status_filter):
                continue
            key = (_norm_command(note.command), _obs_prefix(note.body))
            finding = groups.get(key)
            if finding is None:
                finding = FleetFinding(
                    command=note.command or "—",
                    observation=note.body,
                    type=note.type,
                    severity=note.severity,
                    count=0,
                    workspaces=[],
                )
                groups[key] = finding
                order.append(key)
            if ws_id not in finding.workspaces:
                finding.workspaces.append(ws_id)
            finding.note_refs.append((ws_id, note.id))

    findings: list[FleetFinding] = []
    for key in order:
        finding = groups[key]
        finding.workspaces = sorted(finding.workspaces)
        finding.count = len(finding.workspaces)
        findings.append(finding)
    findings.sort(key=lambda f: (-f.count, f.command.lower(), f.observation.lower()))
    result.findings = findings
    return result


def triage_fleet(
    roots: list[Path],
    *,
    replay: Callable[[str], ReplayOutcome] | None = None,
    resolve_stale: bool = False,
    type_filter: str | None = None,
    status_filter: str | None = None,
    version: str | None = None,
) -> TriageResult:
    """Fleet rollup + replay: classify each deduped finding exactly once.

    Replaying once per defect (not once per workspace) is the whole point of the
    dedup. ``resolve_stale`` resolves the underlying note in EVERY workspace the
    stale finding was seen in.
    """
    scan = scan_fleet(roots, type_filter=type_filter, status_filter=status_filter)
    ver = version if version is not None else _current_version()
    if replay is None:
        replay = make_default_replayer()

    items: list[TriageItem] = []
    resolved_total = 0
    for finding in scan.findings:
        outcome = replay(finding.command)
        verdict = _verdict_for(outcome)
        rep = Note(
            id=finding.note_refs[0][1] if finding.note_refs else 0,
            created_at="", type=finding.type, command=finding.command,
            body=finding.observation, severity=finding.severity, status="open",
        )
        item = TriageItem(
            note=rep, verdict=verdict, replay=outcome,
            workspaces=list(finding.workspaces),
            note_refs=list(finding.note_refs),
        )
        if resolve_stale and verdict == TRIAGE_STALE:
            for ws_id, note_id in finding.note_refs:
                res = resolve_note(Path(ws_id), note_id, _stale_resolution(ver))
                if res.ok:
                    item.resolved += 1
                    resolved_total += 1
        items.append(item)

    return TriageResult(
        ok=True, items=items, version=ver, dry_run=not resolve_stale,
        fleet=True, resolved_count=resolved_total, path="",
        errors=list(scan.errors),
    )
