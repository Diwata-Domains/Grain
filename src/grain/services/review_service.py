"""Review service - packet readiness and completion-precondition validation."""

from dataclasses import dataclass, field
from pathlib import Path

from grain.cli.output import CommandResult
from grain.domain.packets import find_packet_dir, parse_task_metadata
from grain.validators.packet_validator import validate_closure, validate_packet


@dataclass
class ReviewReport:
    """Structured review-readiness report for one packet."""

    task_id: str
    packet_dir: Path
    packet_status: str
    review_ready: bool
    completion_ready: bool
    warnings: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)


@dataclass
class ReviewSummary:
    """Structured summary of packet state for final inspection."""

    task_id: str
    packet_dir: Path
    phase: str
    packet_status: str
    review_ready: bool
    completion_ready: bool
    recommended_next_status: str
    packet_summary: str
    validation_findings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)


def check_packet_review_readiness(
    root: Path,
    task_id: str,
) -> tuple[CommandResult, ReviewReport | None]:
    """Validate whether a packet is ready for review and closure.

    The service checks:
    - packet directory exists
    - packet file and metadata validity
    - closure prerequisites needed before a packet can move to done

    Review readiness is true only when the packet is structurally valid,
    in review status, and closure prerequisites pass.
    """
    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="review check",
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
        )

    packet_errors = validate_packet(packet_dir)
    closure_errors = validate_closure(packet_dir)
    metadata = parse_task_metadata(packet_dir / "task.md") if (packet_dir / "task.md").exists() else {}
    packet_status = metadata.get("status", "")

    missing_files = [
        error.replace("missing required file: ", "")
        for error in packet_errors
        if error.startswith("missing required file: ")
    ]

    blockers = list(packet_errors)
    for error in closure_errors:
        if error not in blockers:
            blockers.append(error)

    completion_ready = not closure_errors
    review_ready = completion_ready and not packet_errors and packet_status == "review"

    warnings: list[str] = []
    if packet_status and packet_status != "review":
        warnings.append(f"packet status is '{packet_status}' — review readiness expects 'review'")
    if not packet_status:
        warnings.append("packet status is missing from task.md metadata")

    report = ReviewReport(
        task_id=task_id,
        packet_dir=packet_dir,
        packet_status=packet_status,
        review_ready=review_ready,
        completion_ready=completion_ready,
        warnings=warnings,
        blockers=blockers,
        missing_files=missing_files,
    )

    result = CommandResult(
        ok=review_ready,
        command="review check",
        repo=str(root),
        task_id=task_id,
        status="review" if review_ready else packet_status,
        warnings=warnings,
        errors=[],
    )
    return result, report


def build_packet_review_summary(
    root: Path,
    task_id: str,
) -> tuple[CommandResult, ReviewSummary | None]:
    """Build a structured packet summary for final inspection.

    The summary is read-only and succeeds whenever the packet exists.
    Validation findings are surfaced as part of the summary instead of
    turning the command into a hard failure.
    """
    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="review summary",
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
        )

    review_result, report = check_packet_review_readiness(root, task_id)
    metadata = parse_task_metadata(packet_dir / "task.md") if (packet_dir / "task.md").exists() else {}
    packet_status = metadata.get("status", "")
    packet_phase = metadata.get("phase", "")
    packet_summary = _read_results_summary(packet_dir / "results.md")
    if not packet_summary:
        packet_summary = _fallback_summary(packet_status, report)

    summary = ReviewSummary(
        task_id=task_id,
        packet_dir=packet_dir,
        phase=packet_phase,
        packet_status=packet_status,
        review_ready=report.review_ready,
        completion_ready=report.completion_ready,
        recommended_next_status=_recommended_next_status(packet_status, report),
        packet_summary=packet_summary,
        validation_findings=list(report.blockers),
        warnings=list(report.warnings),
        next_actions=_next_actions(packet_status, report),
    )

    return (
        CommandResult(
            ok=True,
            command="review summary",
            repo=str(root),
            task_id=task_id,
            status=packet_status,
            warnings=list(review_result.warnings),
        ),
        summary,
    )


def _read_results_summary(results_md_path: Path) -> str:
    if not results_md_path.exists():
        return ""

    text = results_md_path.read_text(encoding="utf-8")
    if not text.strip():
        return ""

    in_summary = False
    summary_lines: list[str] = []
    for line in text.splitlines():
        if line.strip() == "## Summary":
            in_summary = True
            continue
        if in_summary:
            if line.startswith("## "):
                break
            summary_lines.append(line)

    return "\n".join(summary_lines).strip()


def _fallback_summary(packet_status: str, report: ReviewReport) -> str:
    if packet_status == "done":
        return "Packet is already closed."
    if report.review_ready:
        return "Packet is ready for handoff."
    if report.blockers:
        return "Packet has validation findings that need attention."
    if report.completion_ready:
        return "Packet is complete and should be moved to review."
    return "Packet is not yet ready for review."


def _recommended_next_status(packet_status: str, report: ReviewReport) -> str:
    if packet_status == "done":
        return "done"
    if report.review_ready:
        return "done"
    if report.blockers:
        return "blocked"
    if report.completion_ready:
        return "review"
    return "in_progress"


def _next_actions(packet_status: str, report: ReviewReport) -> list[str]:
    if packet_status == "done":
        return ["Packet is already closed; no further review action required."]
    if report.review_ready:
        return [
            "Run `forge review handoff` to generate or validate the handoff artifact.",
            "After reviewer approval, move the packet to `done`.",
        ]
    if report.blockers:
        return [
            "Resolve the validation findings listed above.",
            "Re-run `forge review check` after updating the packet.",
        ]
    if report.completion_ready:
        return [
            "Transition the packet to `review` status.",
            "Run `forge review handoff` once the packet is review-ready.",
        ]
    return [
        "Fill in the missing packet details or results.",
        "Re-run `forge review check` before handoff.",
    ]
