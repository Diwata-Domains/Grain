# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from grain.cli.output import CommandResult
from grain.domain.packets import find_packet_dir, parse_task_metadata

SUPPORTED_VERIFICATION_PROVIDERS = {"assay"}
VERIFICATION_REQUEST_FILENAME = "verification_request.json"
VERIFICATION_RESULT_FILENAME = "verification_result.json"
_VERIFY_ID_RE = re.compile(r"VERIFY-(\d+)-(\d+)")


@dataclass(frozen=True)
class VerificationRequestRecord:
    verification_id: str
    task_id: str
    packet_dir: str
    provider: str
    status: str
    artifact_paths: list[str]
    submitted_at: str


@dataclass(frozen=True)
class VerificationResultRecord:
    verification_id: str
    task_id: str
    outcome: str
    severity: str
    summary: str
    issue_type: str
    artifact_refs: list[str]
    followup_candidates: list[dict]
    verified_at: str


def get_verification_request_status(
    root: Path,
    verification_id: str,
) -> tuple[CommandResult, VerificationRequestRecord | None]:
    path, payload = _find_verification_request(root, verification_id)
    if path is None or payload is None:
        return (
            CommandResult(
                ok=False,
                command="verify status",
                repo=str(root),
                errors=[f"verification request '{verification_id}' not found"],
            ),
            None,
        )

    return (
        CommandResult(
            ok=True,
            command="verify status",
            repo=str(root),
            task_id=str(payload.get("task_id", "")),
            files_updated=[str(path.relative_to(root))],
        ),
        VerificationRequestRecord(
            verification_id=str(payload.get("verification_id", verification_id)),
            task_id=str(payload.get("task_id", "")),
            packet_dir=str(payload.get("packet_dir", "")),
            provider=str(payload.get("provider", "")),
            status=str(payload.get("status", "")),
            artifact_paths=list(payload.get("artifact_paths", [])),
            submitted_at=str(payload.get("submitted_at", "")),
        ),
    )


def submit_verification_request(
    root: Path,
    task_id: str,
    *,
    provider: str = "assay",
) -> tuple[CommandResult, VerificationRequestRecord | None]:
    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="verify submit",
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
        )

    provider_normalized = provider.strip().lower()
    if provider_normalized not in SUPPORTED_VERIFICATION_PROVIDERS:
        return (
            CommandResult(
                ok=False,
                command="verify submit",
                repo=str(root),
                task_id=task_id,
                errors=[f"unsupported verification provider: {provider}"],
            ),
            None,
        )

    metadata = parse_task_metadata(packet_dir / "task.md")
    packet_status = metadata.get("status", "")
    if packet_status not in {"review", "done"}:
        return (
            CommandResult(
                ok=False,
                command="verify submit",
                repo=str(root),
                task_id=task_id,
                errors=["packet must be in review or done status before verification submission"],
            ),
            None,
        )

    results_path = packet_dir / "results.md"
    if not results_path.exists() or not results_path.read_text(encoding="utf-8").strip():
        return (
            CommandResult(
                ok=False,
                command="verify submit",
                repo=str(root),
                task_id=task_id,
                errors=["results.md is required before verification submission"],
            ),
            None,
        )

    request_path = packet_dir / VERIFICATION_REQUEST_FILENAME
    verification_id = _next_verification_id(root, packet_dir)
    artifact_paths = _verification_artifact_paths(root, packet_dir)
    submitted_at = _now_iso()

    record = VerificationRequestRecord(
        verification_id=verification_id,
        task_id=task_id,
        packet_dir=str(packet_dir.relative_to(root)),
        provider=provider_normalized,
        status="pending",
        artifact_paths=artifact_paths,
        submitted_at=submitted_at,
    )
    request_path.write_text(json.dumps(asdict(record), indent=2) + "\n", encoding="utf-8")
    _mark_results_verification_pending(results_path, verification_id)

    return (
        CommandResult(
            ok=True,
            command="verify submit",
            repo=str(root),
            task_id=task_id,
            files_created=[str(request_path.relative_to(root))],
            files_updated=[str(results_path.relative_to(root))],
        ),
        record,
    )


def ingest_verification_result(
    root: Path,
    verification_id: str,
    payload_path: Path,
) -> tuple[CommandResult, VerificationResultRecord | None]:
    request_path, request_payload = _find_verification_request(root, verification_id)
    if request_path is None or request_payload is None:
        return (
            CommandResult(
                ok=False,
                command="verify ingest",
                repo=str(root),
                errors=[f"verification request '{verification_id}' not found"],
            ),
            None,
        )

    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return (
            CommandResult(
                ok=False,
                command="verify ingest",
                repo=str(root),
                errors=[f"payload file not found: {payload_path}"],
            ),
            None,
        )
    except json.JSONDecodeError as exc:
        return (
            CommandResult(
                ok=False,
                command="verify ingest",
                repo=str(root),
                errors=[f"payload is not valid JSON: {exc.msg}"],
            ),
            None,
        )

    validation_errors = _validate_ingest_payload(payload, verification_id)
    if validation_errors:
        return (
            CommandResult(
                ok=False,
                command="verify ingest",
                repo=str(root),
                errors=validation_errors,
            ),
            None,
        )

    task_id = str(payload["task_id"])
    if str(request_payload.get("task_id", "")) != task_id:
        return (
            CommandResult(
                ok=False,
                command="verify ingest",
                repo=str(root),
                errors=[f"payload task_id '{task_id}' does not match request task_id '{request_payload.get('task_id', '')}'"],
            ),
            None,
        )

    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="verify ingest",
                repo=str(root),
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
        )

    record = VerificationResultRecord(
        verification_id=verification_id,
        task_id=task_id,
        outcome=str(payload["outcome"]),
        severity=str(payload["severity"]),
        summary=str(payload["summary"]),
        issue_type=str(payload["issue_type"]),
        artifact_refs=list(payload.get("artifact_refs", [])),
        followup_candidates=list(payload.get("followup_candidates", [])),
        verified_at=str(payload.get("verified_at", _now_iso())),
    )
    result_path = packet_dir / VERIFICATION_RESULT_FILENAME
    result_path.write_text(json.dumps(asdict(record), indent=2) + "\n", encoding="utf-8")
    _update_verification_request_status(request_path, record.outcome)
    _apply_results_verification_outcome(packet_dir / "results.md", record)

    return (
        CommandResult(
            ok=True,
            command="verify ingest",
            repo=str(root),
            task_id=task_id,
            files_created=[str(result_path.relative_to(root))],
            files_updated=[
                str(request_path.relative_to(root)),
                str((packet_dir / "results.md").relative_to(root)),
            ],
        ),
        record,
    )


def _next_verification_id(root: Path, packet_dir: Path) -> str:
    task_md = parse_task_metadata(packet_dir / "task.md")
    task_id = task_md.get("id", "")
    digits = "".join(ch for ch in task_id if ch.isdigit()) or "0000"

    max_suffix = 0
    for path in (root / "tasks").rglob(VERIFICATION_REQUEST_FILENAME):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        existing_id = str(payload.get("verification_id", ""))
        match = _VERIFY_ID_RE.fullmatch(existing_id)
        if not match:
            continue
        if match.group(1) != digits:
            continue
        max_suffix = max(max_suffix, int(match.group(2)))
    return f"VERIFY-{digits}-{max_suffix + 1:03d}"


def _find_verification_request(root: Path, verification_id: str) -> tuple[Path | None, dict | None]:
    for path in (root / "tasks").rglob(VERIFICATION_REQUEST_FILENAME):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if str(payload.get("verification_id", "")) == verification_id:
            return path, payload
    return None, None


def _validate_ingest_payload(payload: object, verification_id: str) -> list[str]:
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]

    errors: list[str] = []
    required = ("verification_id", "task_id", "issue_type", "severity", "outcome", "summary")
    for field in required:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"payload missing required field: {field}")

    if payload.get("verification_id") != verification_id:
        errors.append(
            f"payload verification_id '{payload.get('verification_id', '')}' does not match requested '{verification_id}'"
        )

    if payload.get("issue_type") not in {
        "test_failure",
        "bug_finding",
        "screenshot_evidence",
        "trace_capture",
        "human_annotation",
        "code_review",
    }:
        errors.append("payload issue_type must be one of: test_failure, bug_finding, screenshot_evidence, trace_capture, human_annotation, code_review")

    if payload.get("severity") not in {"info", "warning", "error", "critical"}:
        errors.append("payload severity must be one of: info, warning, error, critical")

    if payload.get("outcome") not in {"pass", "fail", "inconclusive"}:
        errors.append("payload outcome must be one of: pass, fail, inconclusive")

    artifact_refs = payload.get("artifact_refs", [])
    if artifact_refs and (
        not isinstance(artifact_refs, list) or any(not isinstance(item, str) for item in artifact_refs)
    ):
        errors.append("payload artifact_refs must be a list of strings")

    followup_candidates = payload.get("followup_candidates", [])
    if followup_candidates and not isinstance(followup_candidates, list):
        errors.append("payload followup_candidates must be a list")

    return errors


def _update_verification_request_status(request_path: Path, outcome: str) -> None:
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    payload["status"] = "complete" if outcome in {"pass", "inconclusive"} else "failed"
    request_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _verification_artifact_paths(root: Path, packet_dir: Path) -> list[str]:
    candidates = [
        packet_dir / "task.md",
        packet_dir / "context.md",
        packet_dir / "plan.md",
        packet_dir / "deliverable_spec.md",
        packet_dir / "results.md",
        packet_dir / "handoff.md",
        packet_dir / "office_review.json",
        packet_dir / "observability.json",
    ]
    return [
        str(path.relative_to(root))
        for path in candidates
        if path.exists()
    ]


def _mark_results_verification_pending(results_path: Path, verification_id: str) -> None:
    lines = results_path.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    in_verification_review = False
    for line in lines:
        if line.strip() == "## Verification Review":
            in_verification_review = True
            updated_lines.append(line)
            continue
        if in_verification_review and line.startswith("## "):
            in_verification_review = False
        if in_verification_review and line.startswith("- **State:**"):
            updated_lines.append("- **State:** pending")
            continue
        if in_verification_review and line.startswith("- **Summary:**"):
            updated_lines.append(
                f"- **Summary:** Pending Assay verification request `{verification_id}`."
            )
            continue
        updated_lines.append(line)
    results_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _apply_results_verification_outcome(
    results_path: Path,
    record: VerificationResultRecord,
) -> None:
    outcome_state = {
        "pass": "passed",
        "fail": "failed",
        "inconclusive": "inconclusive",
    }[record.outcome]
    findings = []
    findings.append(f"{record.issue_type} [{record.severity}]: {record.summary}")
    findings.extend(record.artifact_refs)

    lines = results_path.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    in_verification_review = False
    in_findings = False
    findings_written = False

    for line in lines:
        stripped = line.strip()
        if stripped == "## Verification Review":
            in_verification_review = True
            updated_lines.append(line)
            continue
        if in_verification_review and line.startswith("## "):
            if in_findings and not findings_written:
                for item in findings:
                    updated_lines.append(f"- {item}")
                findings_written = True
                in_findings = False
            in_verification_review = False
        if in_verification_review and line.startswith("### Findings"):
            updated_lines.append(line)
            in_findings = True
            continue
        if in_verification_review and line.startswith("- **State:**"):
            updated_lines.append(f"- **State:** {outcome_state}")
            continue
        if in_verification_review and line.startswith("- **Summary:**"):
            updated_lines.append(f"- **Summary:** {record.summary}")
            continue
        if in_findings:
            if stripped.startswith("- "):
                continue
            if stripped:
                continue
            if not findings_written:
                for item in findings:
                    updated_lines.append(f"- {item}")
                findings_written = True
            updated_lines.append(line)
            in_findings = False
            continue
        updated_lines.append(line)

    if in_findings and not findings_written:
        for item in findings:
            updated_lines.append(f"- {item}")

    results_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
