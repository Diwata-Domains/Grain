# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

from pathlib import Path

from grain.domain.completion_policy import CompletionPolicy
from grain.domain.packets import (
    ALLOWED_TRANSITIONS,
    VALID_STATUSES,
    parse_task_metadata,
)
from grain.domain.review_bundle import parse_review_bundle

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


_PLANNING_FILES = ("context.md", "plan.md", "deliverable_spec.md")


def _declares_simple_mode(packet_dir: Path) -> bool:
    """Return True when task.md declares itself a simple packet via `- **Mode:** simple`."""
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return False
    return parse_task_metadata(task_md).get("mode", "").lower() == "simple"


def validate_packet_files(packet_dir: Path) -> list[str]:
    """Return errors for any required packet files that are missing.

    Simple packets are exempt from the planning-file requirement.  A packet is
    simple when either (a) its task.md explicitly declares `- **Mode:** simple`
    — in which case the exemption holds regardless of which planning files
    happen to exist, so a partially-migrated legacy packet is not stuck — or
    (b) task.md exists and no planning files exist at all (the inference used
    for packets predating the Mode field).  Otherwise the full set is required,
    preventing partial setups from silently passing.
    """
    has_task_md = (packet_dir / "task.md").exists()
    if has_task_md and _declares_simple_mode(packet_dir):
        return []
    has_any_planning_file = any((packet_dir / f).exists() for f in _PLANNING_FILES)
    if has_task_md and not has_any_planning_file:
        return []
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


def validate_closure(packet_dir: Path, policy: CompletionPolicy | None = None) -> list[str]:
    """Validate that a packet meets the machine-checkable requirements for closure to done.

    v1 rules:
    - all four required files must be present
    - results.md must exist and be non-empty
    - current status must be 'review' (the only allowed predecessor to 'done')
    """
    errors: list[str] = []
    policy = policy or CompletionPolicy()

    errors.extend(validate_packet_files(packet_dir))

    results_md = packet_dir / "results.md"
    if not results_md.exists():
        errors.append("results.md is required for closure but is missing")
    elif not results_md.read_text(encoding="utf-8").strip():
        errors.append("results.md exists but is empty — closure requires recorded results")
    else:
        bundle = parse_review_bundle(results_md.read_text(encoding="utf-8"))
        if policy.require_user_approval and bundle.user_review_state != "approved":
            errors.append(
                "user review state must be 'approved' before closing to 'done'"
            )
        if policy.require_verification_pass:
            if bundle.verification_state not in {"passed", "waived"}:
                errors.append(
                    "verification state must be 'passed' or 'waived' before closing to 'done'"
                )
        elif bundle.verification_state == "pending":
            errors.append(
                "verification state is 'pending' — wait for verification to complete before closing to 'done'"
            )
        elif bundle.verification_state == "failed":
            errors.append(
                "verification state is 'failed' — resolve findings or explicitly waive verification before closing to 'done'"
            )
        elif not policy.allow_close_when_verification_not_run and bundle.verification_state == "not_run":
            errors.append(
                "verification state is 'not_run' — completion policy requires verification before closure"
            )

    task_md = packet_dir / "task.md"
    if task_md.exists():
        metadata = parse_task_metadata(task_md)
        status = metadata.get("status", "")
        if status != "review":
            errors.append(
                f"packet status is '{status}' — must be 'review' before closing to 'done'"
            )

    return errors
