# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Handoff service - packet handoff artifact generation and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from grain.cli.output import CommandResult
from grain.domain.packets import find_packet_dir, parse_task_metadata
from grain.domain.review_bundle import parse_results_sections, parse_review_bundle

_REQUIRED_HEADINGS = (
    "# Handoff:",
    "## Final State",
    "## Review Bundle",
    "### Packet Identity",
    "### Outcome",
    "## What Was Built",
    "## What Review Should Check",
    "## What Was Not Done",
    "## Known Issues or Follow-ups",
    "## Files Changed",
    "## Reviewer Notes",
    "## Closeout Intake",
)


@dataclass
class HandoffArtifact:
    """Structured handoff artifact for one packet."""

    task_id: str
    packet_dir: Path
    phase: str
    packet_status: str
    title: str
    ready_for_handoff: bool
    recommended_next_status: str
    summary: str
    what_was_built: list[str] = field(default_factory=list)
    what_was_not_done: list[str] = field(default_factory=list)
    known_issues_or_followups: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    reviewer_notes: list[str] = field(default_factory=list)
    open_questions_to_log: list[str] = field(default_factory=list)
    proposal_candidates_to_log: list[str] = field(default_factory=list)
    followups_to_log: list[str] = field(default_factory=list)
    review_readiness: str = ""
    user_review_state: str = ""
    verification_state: str = ""


def build_handoff_artifact(
    root: Path,
    task_id: str,
) -> tuple[CommandResult, HandoffArtifact | None]:
    """Build a structured handoff artifact for a review-ready or done packet."""
    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="review handoff",
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
        )

    task_md = packet_dir / "task.md"
    results_md = packet_dir / "results.md"
    if not task_md.exists():
        return (
            CommandResult(
                ok=False,
                command="review handoff",
                errors=["task.md not found"],
            ),
            None,
        )
    if not results_md.exists():
        return (
            CommandResult(
                ok=False,
                command="review handoff",
                errors=["results.md is required for handoff support"],
            ),
            None,
        )

    metadata = parse_task_metadata(task_md)
    packet_status = metadata.get("status", "")
    packet_phase = metadata.get("phase", "")
    title = _parse_task_title(task_md.read_text(encoding="utf-8"))
    results_text = results_md.read_text(encoding="utf-8")
    results_sections = parse_results_sections(results_text)
    bundle = parse_review_bundle(results_text)

    ready_for_handoff = packet_status in {"review", "done"} and bool(results_text.strip())
    if not ready_for_handoff:
        return (
            CommandResult(
                ok=False,
                command="review handoff",
                repo=str(root),
                task_id=task_id,
                status=packet_status,
                errors=[
                    "packet must be in review or done status with non-empty results.md to build handoff",
                ],
            ),
            None,
        )

    summary_lines = results_sections.get("Summary", [])
    summary = "\n".join(summary_lines).strip() if isinstance(summary_lines, list) else ""
    if isinstance(summary, list):
        summary = "\n".join(summary).strip()
    elif not isinstance(summary, str):
        summary = ""
    files_changed = results_sections.get("Files Changed", [])
    review_notes = results_sections.get("Review Notes", [])
    artifact = HandoffArtifact(
        task_id=task_id,
        packet_dir=packet_dir,
        phase=packet_phase,
        packet_status=packet_status,
        title=title,
        ready_for_handoff=True,
        recommended_next_status="done" if packet_status == "done" else "review",
        summary=summary or "Handoff artifact generated from packet results.",
        what_was_built=_summarize_what_was_built(files_changed),
        what_was_not_done=bundle.followups_to_log if bundle.followups_to_log else [],
        known_issues_or_followups=bundle.residual_risks,
        files_changed=files_changed,
        reviewer_notes=review_notes,
        open_questions_to_log=bundle.open_questions_to_log,
        proposal_candidates_to_log=bundle.proposal_candidates_to_log,
        followups_to_log=bundle.followups_to_log,
        review_readiness=_handoff_review_readiness(packet_status, bundle.user_review_state),
        user_review_state=bundle.user_review_state,
        verification_state=bundle.verification_state,
    )

    return (
        CommandResult(
            ok=True,
            command="review handoff",
            repo=str(root),
            task_id=task_id,
            status=packet_status,
        ),
        artifact,
    )


def materialize_handoff_artifact(
    root: Path,
    task_id: str,
    output_path: Path | None = None,
) -> tuple[CommandResult, HandoffArtifact | None, Path | None]:
    """Build, validate, and write a handoff artifact to disk."""
    result, artifact = build_handoff_artifact(root, task_id)
    if not result.ok or artifact is None:
        return result, artifact, None

    content = render_handoff_markdown(root, artifact)
    validation_errors = validate_handoff_markdown(content)
    if validation_errors:
        return (
            CommandResult(
                ok=False,
                command="review handoff",
                repo=str(root),
                task_id=task_id,
                status=artifact.packet_status,
                errors=validation_errors,
            ),
            None,
            None,
        )

    resolved = write_handoff_markdown(root, artifact, output_path=output_path)
    try:
        recorded_path = str(resolved.relative_to(root))
    except ValueError:
        recorded_path = str(resolved)
    return (
        CommandResult(
            ok=True,
            command="review handoff",
            repo=str(root),
            task_id=task_id,
            status=artifact.packet_status,
            files_updated=[recorded_path],
        ),
        artifact,
        resolved,
    )


def render_handoff_markdown(root: Path, artifact: HandoffArtifact) -> str:
    """Render a structured markdown handoff artifact."""
    lines: list[str] = [
        f"# Handoff: {artifact.task_id}",
        "",
        "## Final State",
        _final_state_line(artifact),
        "",
        "## Review Bundle",
        "",
        "### Packet Identity",
        f"- **Task ID:** {artifact.task_id}",
        f"- **Phase:** {artifact.phase or 'Unknown phase'}",
        f"- **Status:** {artifact.packet_status or 'unknown'}",
        "",
        "### Outcome",
        f"- **Review Readiness:** {artifact.review_readiness or 'unknown'}",
        f"- **User Review State:** {artifact.user_review_state or 'pending'}",
        f"- **Verification State:** {artifact.verification_state or 'not_run'}",
        f"- **Recommended Next Status:** {artifact.recommended_next_status}",
        f"- **Short Summary:** {artifact.summary}",
        "",
        "## What Was Built",
    ]
    lines.extend(_format_bullets(artifact.what_was_built))
    lines.extend(
        [
            "",
            "## What Review Should Check",
        ]
    )
    review_checks = artifact.reviewer_notes or ["Packet-ready summary and review handoff contents."]
    lines.extend(_format_bullets(review_checks))
    lines.extend(
        [
            "",
            "## What Was Not Done",
        ]
    )
    lines.extend(_format_bullets(artifact.what_was_not_done))
    lines.extend(
        [
            "",
            "## Known Issues or Follow-ups",
        ]
    )
    lines.extend(_format_bullets(artifact.known_issues_or_followups))
    lines.extend(
        [
            "",
            "## Files Changed",
        ]
    )
    lines.extend(_format_bullets(artifact.files_changed))
    lines.extend(
        [
            "",
            "## Reviewer Notes",
        ]
    )
    lines.extend(_format_bullets(artifact.reviewer_notes))
    lines.extend(
        [
            "",
            "## Closeout Intake",
            "",
            "### Open Questions To Log",
        ]
    )
    lines.extend(_format_bullets(artifact.open_questions_to_log))
    lines.extend(
        [
            "",
            "### Proposal Candidates To Log",
        ]
    )
    lines.extend(_format_bullets(artifact.proposal_candidates_to_log))
    lines.extend(
        [
            "",
            "### Follow-Ups To Log",
        ]
    )
    lines.extend(_format_bullets(artifact.followups_to_log))

    return "\n".join(lines).strip() + "\n"


def write_handoff_markdown(
    root: Path,
    artifact: HandoffArtifact,
    output_path: Path | None = None,
) -> Path:
    """Write handoff markdown to disk and return the output path."""
    if output_path is None:
        resolved = artifact.packet_dir / "handoff.md"
    elif output_path.is_absolute():
        resolved = output_path
    else:
        resolved = root / output_path

    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(render_handoff_markdown(root, artifact), encoding="utf-8")
    return resolved


def validate_handoff_markdown(content: str) -> list[str]:
    """Validate that a handoff markdown document includes the required headings."""
    errors = []
    for heading in _REQUIRED_HEADINGS:
        if heading not in content:
            errors.append(f"missing required heading: {heading}")
    return errors


def _parse_task_title(text: str) -> str:
    match = re.search(r"^# Task:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""
def _bullets(lines: list[str]) -> list[str]:
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped and stripped not in {"None.", "None"}:
            if items:
                items[-1] = f"{items[-1]} {stripped}"
    return items


def _summarize_what_was_built(files_changed: list[str]) -> list[str]:
    built = [entry for entry in files_changed if entry.startswith(("src/", "tests/"))]
    return built or ["Packet handoff support is ready."]


def _format_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- None"]
    return [f"- {item}" for item in items]


def _final_state_line(artifact: HandoffArtifact) -> str:
    if artifact.packet_status == "done":
        return f"`{artifact.title or artifact.task_id}` is implemented, reviewed, and closed."
    return f"`{artifact.title or artifact.task_id}` is ready for handoff."


def _handoff_review_readiness(packet_status: str, user_review_state: str) -> str:
    if packet_status == "done":
        return "completed"
    if user_review_state == "approved":
        return "ready"
    if user_review_state in {"needs_fix", "misunderstood"}:
        return "needs fixes"
    return "blocked"
