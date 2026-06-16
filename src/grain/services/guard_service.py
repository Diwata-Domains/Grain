# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Workflow guard service — point-in-time enforcement checks.

All checks are read-only. Returns a structured list of findings that
the caller can render as text or JSON. Zero AI involvement required.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from grain.services.workflow_service import (
    _read_current_phase,
    _read_current_task,
    _resolve_packet_dir,
)
_STUB_MARKER = "TASK-####"


def _is_stub_text(text: str) -> bool:
    return _STUB_MARKER in text


_DEFAULT_CURRENT_TASK_DOC = "docs/working/current_task.md"
_DEFAULT_PHASE_DOC = "docs/working/current_focus.md"


@dataclass
class GuardFinding:
    id: str
    result: str        # "pass" | "warn" | "fail"
    severity: str      # "info" | "warning" | "error"
    message: str
    remediation: str = ""


@dataclass
class GuardResult:
    ok: bool
    status: str        # "ok" | "warning" | "violation"
    checks: list[GuardFinding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def run_guard(
    root: Path,
    strict: bool = False,
    check_docs: bool = False,
    check_dev_alignment: bool = False,
) -> GuardResult:
    """Run all workflow guard checks and return structured findings."""
    current_task_path = root / _DEFAULT_CURRENT_TASK_DOC
    current_focus_path = root / _DEFAULT_PHASE_DOC

    if not current_task_path.exists():
        return GuardResult(
            ok=False,
            status="violation",
            errors=[f"missing required doc: {_DEFAULT_CURRENT_TASK_DOC}"],
        )

    current_task = _read_current_task(current_task_path)
    if current_task is None:
        return GuardResult(
            ok=False,
            status="violation",
            errors=["current_task.md is missing required fields"],
        )

    findings: list[GuardFinding] = []

    # Check 1 — packet_open
    findings.append(_check_packet_open(root, current_task))

    # Check 2 — results_not_stub
    findings.append(_check_results_not_stub(root, current_task))

    # Check 3 — phase_alignment
    if current_focus_path.exists():
        findings.append(_check_phase_alignment(root, current_task, current_focus_path))

    # Check 4 — implementation_ahead_of_packet
    findings.append(_check_implementation_ahead(root, current_task))

    # Check 5 — branch_policy
    findings.append(_check_branch_policy(root, current_task))

    # Optional check — dev_alignment
    if check_dev_alignment:
        findings.append(_check_dev_alignment(root))

    # Optional check — docs_health via grain docs audit
    if check_docs:
        findings.extend(_check_docs_health(root))

    violations = [f for f in findings if f.result == "fail"]
    warnings = [f for f in findings if f.result == "warn"]

    if strict:
        violations = violations + warnings
        warnings = []

    if violations:
        status = "violation"
        ok = False
    elif warnings:
        status = "warning"
        ok = True
    else:
        status = "ok"
        ok = True

    return GuardResult(ok=ok, status=status, checks=findings)


def _check_packet_open(root: Path, current_task: dict) -> GuardFinding:
    task_id = current_task.get("task_id", "none")
    if task_id == "none" or not task_id:
        return GuardFinding(
            id="packet_open",
            result="fail",
            severity="error",
            message="current_task.md is unset; no in_progress packet",
            remediation="grain task create --id <TASK-ID>",
        )
    packet_dir = _resolve_packet_dir(root, task_id, current_task.get("task_path", ""))
    if packet_dir is None:
        return GuardFinding(
            id="packet_open",
            result="fail",
            severity="error",
            message=f"packet directory not found for {task_id}",
            remediation=f"grain task create --id {task_id}",
        )
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return GuardFinding(
            id="packet_open",
            result="fail",
            severity="error",
            message=f"task.md missing in packet for {task_id}",
            remediation=f"restore or recreate the packet at {packet_dir.relative_to(root)}",
        )
    from grain.domain.packets import parse_task_metadata
    metadata = parse_task_metadata(task_md)
    status = metadata.get("status", "")
    if status != "in_progress":
        return GuardFinding(
            id="packet_open",
            result="fail",
            severity="error",
            message=f"{task_id} packet status is '{status}', expected 'in_progress'",
            remediation=f"set status to in_progress in {packet_dir.relative_to(root)}/task.md",
        )
    return GuardFinding(
        id="packet_open",
        result="pass",
        severity="info",
        message=f"{task_id} is in_progress",
    )


def _check_results_not_stub(root: Path, current_task: dict) -> GuardFinding:
    task_id = current_task.get("task_id", "none")
    if task_id == "none" or not task_id:
        return GuardFinding(
            id="results_not_stub",
            result="pass",
            severity="info",
            message="no active task — skipped",
        )
    packet_dir = _resolve_packet_dir(root, task_id, current_task.get("task_path", ""))
    if packet_dir is None:
        return GuardFinding(
            id="results_not_stub",
            result="pass",
            severity="info",
            message="packet not found — skipped",
        )
    results_md = packet_dir / "results.md"
    if not results_md.exists():
        return GuardFinding(
            id="results_not_stub",
            result="warn",
            severity="warning",
            message="results.md is absent — task has no recorded execution artifacts yet",
            remediation="write execution results before closing",
        )
    if _is_stub_text(results_md.read_text(encoding="utf-8")):
        return GuardFinding(
            id="results_not_stub",
            result="warn",
            severity="warning",
            message="results.md is stub-only (contains unresolved placeholders)",
            remediation="replace placeholders with actual execution results",
        )
    return GuardFinding(
        id="results_not_stub",
        result="pass",
        severity="info",
        message="results.md has content",
    )


def _check_phase_alignment(root: Path, current_task: dict, current_focus_path: Path) -> GuardFinding:
    task_id = current_task.get("task_id", "none")
    if task_id == "none" or not task_id:
        return GuardFinding(
            id="phase_alignment",
            result="pass",
            severity="info",
            message="no active task — skipped",
        )
    packet_dir = _resolve_packet_dir(root, task_id, current_task.get("task_path", ""))
    if packet_dir is None:
        return GuardFinding(
            id="phase_alignment",
            result="pass",
            severity="info",
            message="packet not found — skipped",
        )
    from grain.domain.packets import parse_task_metadata
    task_metadata = parse_task_metadata(packet_dir / "task.md") if (packet_dir / "task.md").exists() else {}
    packet_phase = task_metadata.get("phase", "")

    current_phase = _read_current_phase(current_focus_path)

    if current_phase and packet_phase:
        # packet_phase is like "Phase 31 — DX Hardening..."
        if f"Phase {current_phase}" not in packet_phase and current_phase not in packet_phase:
            return GuardFinding(
                id="phase_alignment",
                result="fail",
                severity="error",
                message=f"packet phase '{packet_phase}' does not match active phase {current_phase}",
                remediation="update current_focus.md or switch to the correct packet",
            )
    return GuardFinding(
        id="phase_alignment",
        result="pass",
        severity="info",
        message="current task matches current phase",
    )


def _check_implementation_ahead(root: Path, current_task: dict) -> GuardFinding:
    """Check for staged implementation files outside docs/ and tasks/ with no open packet."""
    task_id = current_task.get("task_id", "none")
    if task_id != "none" and task_id:
        # Packet is open — this check is about un-packetted work; skip.
        return GuardFinding(
            id="implementation_ahead_of_packet",
            result="pass",
            severity="info",
            message="no implementation files ahead of packet",
        )
    # No open packet — check for staged non-doc/non-task files.
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        staged = result.stdout.strip().splitlines()
    except Exception:
        return GuardFinding(
            id="implementation_ahead_of_packet",
            result="pass",
            severity="info",
            message="git not available — skipped",
        )

    impl_files = [
        f for f in staged
        if not f.startswith("docs/working/")
        and not f.startswith("tasks/")
        and not f.startswith("docs/canonical/")
        and not f.startswith("docs/runtime/")
    ]
    if impl_files:
        return GuardFinding(
            id="implementation_ahead_of_packet",
            result="fail",
            severity="error",
            message=f"{len(impl_files)} staged implementation file(s) with no open packet: {', '.join(impl_files[:3])}{'...' if len(impl_files) > 3 else ''}",
            remediation="create a task packet before staging implementation files",
        )
    return GuardFinding(
        id="implementation_ahead_of_packet",
        result="pass",
        severity="info",
        message="no implementation files ahead of packet",
    )


def _check_branch_policy(root: Path, current_task: dict) -> GuardFinding:
    """Check that the current git branch satisfies branch_policy in docs_manifest.yaml."""
    import os
    from grain.adapters.manifest import load_branch_policy
    from grain.services.workflow_service import (
        _read_current_branch,
        _branch_matches,
        _suggest_branch,
    )

    try:
        policy = load_branch_policy(root)
    except Exception:
        return GuardFinding(
            id="branch_policy",
            result="pass",
            severity="info",
            message="branch_policy: skipped (manifest unavailable)",
        )

    if policy.mode == "off":
        return GuardFinding(
            id="branch_policy",
            result="pass",
            severity="info",
            message="branch_policy: off",
        )

    branch = _read_current_branch(root)
    phase = ""
    try:
        from grain.services.workflow_service import _read_current_phase
        cf = root / "docs" / "working" / "current_focus.md"
        if cf.exists():
            phase = _read_current_phase(cf)
    except Exception:
        pass

    task_id = current_task.get("task_id", "none") or "none"

    if os.environ.get("GRAIN_SKIP_BRANCH_CHECK") == "1":
        from grain.services.workflow_service import _log_branch_skip_to_tooling_notes
        _log_branch_skip_to_tooling_notes(root, branch, policy.mode)
        return GuardFinding(
            id="branch_policy",
            result="pass",
            severity="info",
            message=f"branch_policy: skipped via GRAIN_SKIP_BRANCH_CHECK (branch: {branch!r})",
        )

    if not branch:
        return GuardFinding(
            id="branch_policy",
            result="warn",
            severity="warning",
            message="branch_policy: branch could not be determined (detached HEAD or not a git repo)",
            remediation=f"checkout a branch matching policy mode '{policy.mode}'",
        )

    if _branch_matches(branch, policy.mode, policy.pattern, phase, task_id):
        return GuardFinding(
            id="branch_policy",
            result="pass",
            severity="info",
            message=f"branch_policy: {branch!r} satisfies mode '{policy.mode}'",
        )

    suggested = _suggest_branch(policy.mode, phase, task_id)
    msg = (
        f"branch '{branch}' does not satisfy branch_policy (mode: {policy.mode})"
        + (f" — suggested: {suggested}" if suggested else "")
    )
    if policy.message:
        msg += f" — {policy.message}"

    if policy.enforce:
        return GuardFinding(
            id="branch_policy",
            result="fail",
            severity="error",
            message=msg,
            remediation=f"git checkout -b {suggested}" if suggested else "switch to a compliant branch",
        )
    return GuardFinding(
        id="branch_policy",
        result="warn",
        severity="warning",
        message=msg,
        remediation=f"git checkout -b {suggested}" if suggested else "switch to a compliant branch",
    )


def _check_docs_health(root: Path) -> list[GuardFinding]:
    """Run grain docs audit (errors → violations, warnings → guard warnings)."""
    try:
        from grain.services.docs_audit_service import run_audit
        audit_result = run_audit(root, severity_filter="medium")
    except Exception as exc:
        return [GuardFinding(
            id="docs_health",
            result="warn",
            severity="warning",
            message=f"docs audit failed to run: {exc}",
        )]

    findings: list[GuardFinding] = []
    for f in audit_result.findings:
        if f.severity == "error":
            findings.append(GuardFinding(
                id=f"docs:{f.check_id}",
                result="fail",
                severity="error",
                message=f.message,
                remediation=f.remediation,
            ))
        elif f.severity == "warning":
            findings.append(GuardFinding(
                id=f"docs:{f.check_id}",
                result="warn",
                severity="warning",
                message=f.message,
                remediation=f.remediation,
            ))

    if not findings:
        findings.append(GuardFinding(
            id="docs_health",
            result="pass",
            severity="info",
            message=f"docs audit: {audit_result.overall} ({audit_result.summary['pass']} pass, "
                    f"{audit_result.summary['warning']} warning, {audit_result.summary['error']} error)",
        ))
    return findings


def _check_dev_alignment(root: Path) -> GuardFinding:
    """Check whether Grain is running from source vs. installed (stub — full impl in T06)."""
    return GuardFinding(
        id="dev_alignment",
        result="pass",
        severity="info",
        message="dev alignment check deferred to grain doctor (T06)",
    )
