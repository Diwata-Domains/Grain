# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReviewBundle:
    user_review_state: str = "pending"
    user_review_summary: str = ""
    resolution_mode: str = ""
    required_fixes: list[str] = field(default_factory=list)
    open_questions_to_log: list[str] = field(default_factory=list)
    proposal_candidates_to_log: list[str] = field(default_factory=list)
    followups_to_log: list[str] = field(default_factory=list)
    residual_risks: list[str] = field(default_factory=list)
    verification_state: str = "not_run"
    verification_summary: str = ""
    verification_findings: list[str] = field(default_factory=list)
    closure_decision: str = ""
    closure_reason: str = ""
    closure_blockers: list[str] = field(default_factory=list)
    legacy_review_decision: str = ""
    legacy_recommended_next_status: str = ""


def parse_results_sections(text: str) -> dict[str, object]:
    lines = text.splitlines()
    sections: dict[str, object] = {}
    current_heading: str | None = None
    current_lines: list[str] = []
    current_subsection: str | None = None
    subsection_lines: list[str] = []
    subsection_map: dict[str, list[str]] = {}

    def flush_section() -> None:
        nonlocal current_heading, current_lines, current_subsection, subsection_lines, subsection_map
        if current_heading is None:
            return
        if subsection_map or current_subsection is not None:
            if current_subsection is not None:
                subsection_map[current_subsection] = list(subsection_lines)
            sections[current_heading] = {
                "__lines__": list(current_lines),
                **subsection_map,
            }
        else:
            sections[current_heading] = list(current_lines)
        current_heading = None
        current_lines = []
        current_subsection = None
        subsection_lines = []
        subsection_map = {}

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("## "):
            flush_section()
            current_heading = line[3:].strip()
            continue
        if current_heading is None:
            continue
        if line.startswith("### "):
            if current_subsection is not None:
                subsection_map[current_subsection] = list(subsection_lines)
            current_subsection = line[4:].strip()
            subsection_lines = []
            continue
        if current_subsection is None:
            current_lines.append(line)
        else:
            subsection_lines.append(line)

    flush_section()
    return sections


def parse_review_bundle(results_text: str) -> ReviewBundle:
    sections = parse_results_sections(results_text)

    user_review = _as_section_map(sections.get("User Review"))
    verification_review = _as_section_map(sections.get("Verification Review"))
    closure_decision = _as_section_map(sections.get("Closure Decision"))
    legacy_review = _as_section_map(sections.get("Review Intake"))

    user_scalars = _parse_key_value_lines(user_review.get("__lines__", []))
    verification_scalars = _parse_key_value_lines(verification_review.get("__lines__", []))
    closure_scalars = _parse_key_value_lines(closure_decision.get("__lines__", []))
    legacy_scalars = _parse_key_value_lines(legacy_review.get("__lines__", []))

    user_state = _normalize_user_review_state(
        user_scalars.get("State", "")
        or legacy_scalars.get("Review Decision", "")
    )
    resolution_mode = _normalize_resolution_mode(
        user_scalars.get("Resolution Mode", ""),
        user_state,
    )
    verification_state = _normalize_verification_state(
        verification_scalars.get("State", "")
    )

    return ReviewBundle(
        user_review_state=user_state,
        user_review_summary=user_scalars.get("Summary", ""),
        resolution_mode=resolution_mode,
        required_fixes=_bullets(user_review.get("Required Fixes", [])) or _bullets(legacy_review.get("Required Fixes", [])),
        open_questions_to_log=_bullets(user_review.get("Open Questions To Log", [])) or _bullets(legacy_review.get("Open Questions To Log", [])),
        proposal_candidates_to_log=_bullets(user_review.get("Proposal Candidates To Log", [])) or _bullets(legacy_review.get("Proposal Candidates To Log", [])),
        followups_to_log=_bullets(user_review.get("Follow-Ups To Log", [])) or _bullets(legacy_review.get("Follow-Ups To Log", [])),
        residual_risks=_bullets(user_review.get("Residual Risks", [])) or _bullets(legacy_review.get("Residual Risks", [])),
        verification_state=verification_state,
        verification_summary=verification_scalars.get("Summary", ""),
        verification_findings=_bullets(verification_review.get("Findings", [])),
        closure_decision=_normalize_closure_decision(closure_scalars.get("Decision", "")),
        closure_reason=closure_scalars.get("Reason", ""),
        closure_blockers=_bullets(closure_decision.get("Closure Blockers", [])),
        legacy_review_decision=legacy_scalars.get("Review Decision", ""),
        legacy_recommended_next_status=legacy_scalars.get("Recommended Next Status", ""),
    )


def _as_section_map(value: object) -> dict[str, list[str]]:
    if isinstance(value, dict):
        result: dict[str, list[str]] = {}
        for key, entry in value.items():
            if isinstance(entry, list):
                result[key] = entry
        return result
    if isinstance(value, list):
        return {"__lines__": value}
    return {"__lines__": []}


def _parse_key_value_lines(lines: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in lines:
        line = raw.strip()
        if not (line.startswith("- **") and ":**" in line):
            continue
        body = line[4:]
        key, value = body.split(":**", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _bullets(lines: list[str]) -> list[str]:
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if value not in {"None", "None."}:
                items.append(value)
        elif stripped and items:
            items[-1] = f"{items[-1]} {stripped}"
    return items


def _normalize_user_review_state(raw: str) -> str:
    lowered = raw.strip().lower().replace(" ", "_")
    mapping = {
        "approved": "approved",
        "ready": "approved",
        "rejected": "rejected",
        "needs_fix": "needs_fix",
        "needs_fixes": "needs_fix",
        "misunderstood": "misunderstood",
        "followup_requested": "followup_requested",
        "follow_up_requested": "followup_requested",
        "pending": "pending",
        "": "pending",
        "[reviewer_fills]": "pending",
    }
    return mapping.get(lowered, "pending")


def _normalize_verification_state(raw: str) -> str:
    lowered = raw.strip().lower().replace(" ", "_")
    allowed = {"not_run", "pending", "passed", "failed", "inconclusive", "waived"}
    return lowered if lowered in allowed else "not_run"


def _normalize_resolution_mode(raw: str, user_state: str) -> str:
    lowered = raw.strip().lower().replace(" ", "_")
    allowed = {"revise_current_task", "replan_current_task", "create_followup_task", "close_task"}
    if lowered in allowed:
        return lowered
    defaults = {
        "approved": "close_task",
        "needs_fix": "revise_current_task",
        "misunderstood": "replan_current_task",
        "followup_requested": "create_followup_task",
    }
    return defaults.get(user_state, "")


def _normalize_closure_decision(raw: str) -> str:
    lowered = raw.strip().lower().replace(" ", "_")
    allowed = {"pending", "keep_open", "close_task", "closed"}
    return lowered if lowered in allowed else ""
