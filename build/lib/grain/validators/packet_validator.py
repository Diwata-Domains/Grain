from pathlib import Path

from grain.domain.packets import (
    ALLOWED_TRANSITIONS,
    VALID_STATUSES,
    parse_task_metadata,
)

_REQUIRED_FILES = ("task.md", "context.md", "plan.md", "deliverable_spec.md")


def validate_status_value(status: str) -> list[str]:
    """Return errors if status is not a valid canonical status value."""
    if status not in VALID_STATUSES:
        return [
            f"invalid status '{status}': must be one of {sorted(VALID_STATUSES)}"
        ]
    return []


def validate_status_transition(from_status: str, to_status: str) -> list[str]:
    """Return errors if the transition from_status -> to_status is not allowed."""
    errors = validate_status_value(from_status)
    if errors:
        return errors
    errors = validate_status_value(to_status)
    if errors:
        return errors

    allowed = ALLOWED_TRANSITIONS.get(from_status, frozenset())
    if to_status not in allowed:
        return [
            f"transition '{from_status}' -> '{to_status}' is not allowed"
        ]
    return []


def validate_packet_files(packet_dir: Path) -> list[str]:
    """Return errors for any required packet files that are missing."""
    return [
        f"missing required file: {name}"
        for name in _REQUIRED_FILES
        if not (packet_dir / name).exists()
    ]


def validate_packet_metadata(packet_dir: Path) -> list[str]:
    """Validate the ## Metadata block in task.md: id, status, and phase present and valid.

    Per Q4 decision: parse id, status, and phase only.
    """
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return ["task.md not found — cannot validate metadata"]

    metadata = parse_task_metadata(task_md)
    errors: list[str] = []

    if not metadata.get("id"):
        errors.append("task.md metadata missing required field: id")

    status = metadata.get("status", "")
    if not status:
        errors.append("task.md metadata missing required field: status")
    else:
        errors.extend(validate_status_value(status))

    if not metadata.get("phase"):
        errors.append("task.md metadata missing required field: phase")

    return errors


def validate_packet(packet_dir: Path) -> list[str]:
    """Run all packet validators: required file presence and metadata fields."""
    errors = validate_packet_files(packet_dir)
    errors.extend(validate_packet_metadata(packet_dir))
    return errors


def validate_closure(packet_dir: Path) -> list[str]:
    """Validate that a packet meets the machine-checkable requirements for closure to done.

    v1 rules:
    - all four required files must be present
    - results.md must exist and be non-empty
    - current status must be 'review' (the only allowed predecessor to 'done')
    """
    errors: list[str] = []

    errors.extend(validate_packet_files(packet_dir))

    results_md = packet_dir / "results.md"
    if not results_md.exists():
        errors.append("results.md is required for closure but is missing")
    elif not results_md.read_text(encoding="utf-8").strip():
        errors.append("results.md exists but is empty — closure requires recorded results")

    task_md = packet_dir / "task.md"
    if task_md.exists():
        metadata = parse_task_metadata(task_md)
        status = metadata.get("status", "")
        if status != "review":
            errors.append(
                f"packet status is '{status}' — must be 'review' before closing to 'done'"
            )

    return errors
