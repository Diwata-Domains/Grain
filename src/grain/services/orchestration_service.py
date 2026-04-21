"""Orchestration service for proposal generation (task and phase level)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from grain.adapters.adapter_config import load_adapter_profiles
from grain.domain.adapters import AdapterProfile
from grain.domain.errors import ConfigError, MissingPathError
from grain.domain.orchestrator import (
    CrossDomainDependency,
    OrchestratorPlan,
    PacketCandidate,
)
from grain.services.impact_ranking_service import rank_impacted_files

_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")
_PHASE_SPLIT_PATTERN = re.compile(r"\s*(?:,| and )\s*", re.IGNORECASE)

if TYPE_CHECKING:
    from grain.cli.output import CommandResult


def build_task_level_plan(
    root: Path,
    scope_summary: str,
    *,
    adapter_ids: list[str] | None = None,
    produced_by: str = "orchestration_service",
    plan_id: str | None = None,
) -> tuple[CommandResult, OrchestratorPlan | None]:
    """Build a task-level OrchestratorPlan proposal for one scope description.

    This function is read-only and proposal-only. It must never create packets.
    """
    if not scope_summary.strip():
        return (
            _command_result(
                ok=False,
                command="orchestration task-plan",
                errors=["scope_summary is required"],
            ),
            None,
        )

    try:
        profiles = load_adapter_profiles(root)
    except (MissingPathError, ConfigError) as exc:
        return (
            _command_result(
                ok=False,
                command="orchestration task-plan",
                errors=[exc.message] + ([exc.detail] if exc.detail else []),
            ),
            None,
        )

    filter_error, profiles = _filter_profiles(profiles, adapter_ids)
    if filter_error:
        return (
            _command_result(
                ok=False,
                command="orchestration task-plan",
                errors=[filter_error],
            ),
            None,
        )

    ranked_profiles = _rank_profiles_for_scope(profiles, scope_summary)
    active = [profile for profile, score in ranked_profiles if score > 0]

    if not active:
        candidates = [
            PacketCandidate(
                candidate_id="C-001",
                title=f"Implement scope: {scope_summary}",
                scope_summary=scope_summary,
                primary_adapter=None,
            )
        ]
        plan = OrchestratorPlan(
            plan_id=plan_id or _generate_plan_id(),
            scope_summary=scope_summary,
            produced_by=produced_by,
            status="draft",
            active_adapters=[],
            packet_candidates=candidates,
            dependency_links=[],
            cross_domain_flags=[],
            split_recommendations=[],
        )
        return _command_result(ok=True, command="orchestration task-plan", repo=str(root)), plan

    candidates = _build_packet_candidates(active, scope_summary)
    links = _build_dependency_links(active, candidates)
    cross_domain_flags = _cross_domain_flags(active)
    split_recommendations = _split_recommendations(scope_summary, active, candidates)

    plan = OrchestratorPlan(
        plan_id=plan_id or _generate_plan_id(),
        scope_summary=scope_summary,
        produced_by=produced_by,
        status="draft",
        active_adapters=[profile.adapter_id for profile in active],
        packet_candidates=candidates,
        dependency_links=links,
        cross_domain_flags=cross_domain_flags,
        split_recommendations=split_recommendations,
    )
    return _command_result(ok=True, command="orchestration task-plan", repo=str(root)), plan


def analyze_scope_signals(
    root: Path,
    scope_summary: str,
    *,
    adapter_ids: list[str] | None = None,
) -> tuple[CommandResult, dict[str, object] | None]:
    """Analyze adapter/domain signals for one scope description.

    This function is read-only and proposal-only. It does not create plans.
    """
    if not scope_summary.strip():
        return (
            _command_result(
                ok=False,
                command="orchestration scope-signals",
                errors=["scope_summary is required"],
            ),
            None,
        )

    try:
        profiles = load_adapter_profiles(root)
    except (MissingPathError, ConfigError) as exc:
        return (
            _command_result(
                ok=False,
                command="orchestration scope-signals",
                errors=[exc.message] + ([exc.detail] if exc.detail else []),
            ),
            None,
        )

    filter_error, profiles = _filter_profiles(profiles, adapter_ids)
    if filter_error:
        return (
            _command_result(
                ok=False,
                command="orchestration scope-signals",
                errors=[filter_error],
            ),
            None,
        )

    ranked_profiles = _rank_profiles_for_scope(profiles, scope_summary)
    active_profiles = [profile for profile, score in ranked_profiles if score > 0]

    signals = []
    for profile, score in ranked_profiles:
        capability = profile.get_capabilities()
        detect_signal = capability.detect_scope(scope_summary)
        impact_signal = capability.analyze_impact(detect_signal.file_patterns)
        impact_ranking = rank_impacted_files(
            root,
            detect_signal.file_patterns,
            impact_signal.affected_files,
        )
        signals.append(
            {
                "adapter_id": profile.adapter_id,
                "domain_type": profile.domain_type,
                "score": score,
                "file_patterns": detect_signal.file_patterns,
                "relevant_areas": detect_signal.relevant_areas,
                "impact": {
                    "affected_files": impact_signal.affected_files,
                    "downstream_areas": impact_signal.downstream_areas,
                    "ranking": impact_ranking,
                },
                "active": score > 0,
            }
        )

    domains = sorted({profile.domain_type for profile in active_profiles})
    payload = {
        "scope_summary": scope_summary,
        "adapter_filter": adapter_ids or [],
        "adapter_signals": signals,
        "active_adapters": [profile.adapter_id for profile in active_profiles],
        "active_domains": domains,
        "cross_domain_flags": domains if len(domains) > 1 else [],
    }
    return (
        _command_result(ok=True, command="orchestration scope-signals", repo=str(root)),
        payload,
    )




def build_phase_level_plan(
    root: Path,
    phase_summary: str,
    *,
    adapter_ids: list[str] | None = None,
    phase_candidates: list[str] | None = None,
    produced_by: str = "orchestration_service.phase",
    plan_id: str | None = None,
) -> tuple[CommandResult, OrchestratorPlan | None]:
    """Build a phase-level OrchestratorPlan proposal for phase shaping/replan.

    Phase-level output is proposal-only and read-only; no packet mutation occurs.
    """
    if not phase_summary.strip():
        return (
            _command_result(
                ok=False,
                command="orchestration phase-plan",
                errors=["phase_summary is required"],
            ),
            None,
        )

    try:
        profiles = load_adapter_profiles(root)
    except (MissingPathError, ConfigError) as exc:
        return (
            _command_result(
                ok=False,
                command="orchestration phase-plan",
                errors=[exc.message] + ([exc.detail] if exc.detail else []),
            ),
            None,
        )

    filter_error, profiles = _filter_profiles(profiles, adapter_ids)
    if filter_error:
        return (
            _command_result(
                ok=False,
                command="orchestration phase-plan",
                errors=[filter_error],
            ),
            None,
        )

    segments = _phase_segments(phase_summary, phase_candidates)
    candidates: list[PacketCandidate] = []
    matched_profiles: list[AdapterProfile] = []

    for idx, segment in enumerate(segments, start=1):
        ranked = _rank_profiles_for_scope(profiles, segment)
        profile = ranked[0][0] if ranked and ranked[0][1] > 0 else None
        depends_on = [f"C-{idx - 1:03d}"] if idx > 1 else []
        candidates.append(
            PacketCandidate(
                candidate_id=f"C-{idx:03d}",
                title=segment,
                scope_summary=segment,
                primary_adapter=profile.adapter_id if profile else None,
                depends_on=depends_on,
            )
        )
        if profile:
            matched_profiles.append(profile)

    links = _build_phase_dependency_links(candidates, matched_profiles)
    cross_domain_flags = _cross_domain_flags(matched_profiles)
    split_recommendations = _phase_split_recommendations(phase_summary, candidates)

    plan = OrchestratorPlan(
        plan_id=plan_id or _generate_plan_id(),
        scope_summary=phase_summary,
        produced_by=produced_by,
        status="draft",
        active_adapters=sorted({p.adapter_id for p in matched_profiles}),
        packet_candidates=candidates,
        dependency_links=links,
        cross_domain_flags=cross_domain_flags,
        split_recommendations=split_recommendations,
    )
    return _command_result(ok=True, command="orchestration phase-plan", repo=str(root)), plan


def _generate_plan_id() -> str:
    return f"OP-{uuid4().hex[:8].upper()}"


def _command_result(**kwargs):
    from grain.cli.output import CommandResult

    return CommandResult(**kwargs)


def _filter_profiles(
    profiles: list[AdapterProfile], adapter_ids: list[str] | None
) -> tuple[str | None, list[AdapterProfile]]:
    if not adapter_ids:
        return None, profiles

    wanted = [item.strip() for item in adapter_ids if item and item.strip()]
    if not wanted:
        return None, profiles

    by_id = {profile.adapter_id: profile for profile in profiles}
    missing = [adapter_id for adapter_id in wanted if adapter_id not in by_id]
    if missing:
        if len(missing) == 1:
            return f"Unknown adapter id: {missing[0]}", []
        return f"Unknown adapter ids: {', '.join(missing)}", []

    filtered = [by_id[adapter_id] for adapter_id in wanted]
    return None, filtered


def _tokenize(value: str) -> set[str]:
    return {token.lower() for token in _TOKEN_PATTERN.findall(value.lower())}


def _rank_profiles_for_scope(
    profiles: list[AdapterProfile], scope_summary: str
) -> list[tuple[AdapterProfile, int]]:
    scope_tokens = _tokenize(scope_summary)
    ranked: list[tuple[AdapterProfile, int]] = []

    for profile in profiles:
        profile_text = " ".join(
            [
                profile.adapter_id,
                profile.domain_type,
                *profile.applies_to,
            ]
        )
        profile_tokens = _tokenize(profile_text)
        score = len(scope_tokens & profile_tokens)

        capability = profile.get_capabilities()
        detect_signal = capability.detect_scope(scope_summary)
        signal_tokens = _tokenize(
            " ".join([*detect_signal.file_patterns, *detect_signal.relevant_areas])
        )
        score += len(scope_tokens & signal_tokens)
        impact_signal = capability.analyze_impact(detect_signal.file_patterns)
        impact_tokens = _tokenize(
            " ".join([*impact_signal.affected_files, *impact_signal.downstream_areas])
        )
        score += len(scope_tokens & impact_tokens)

        ranked.append((profile, score))

    ranked.sort(key=lambda item: (item[1], item[0].adapter_id), reverse=True)
    return ranked


def _build_packet_candidates(
    active_profiles: list[AdapterProfile], scope_summary: str
) -> list[PacketCandidate]:
    candidates: list[PacketCandidate] = []
    for index, profile in enumerate(active_profiles, start=1):
        depends_on = [f"C-{index - 1:03d}"] if index > 1 else []
        candidates.append(
            PacketCandidate(
                candidate_id=f"C-{index:03d}",
                title=f"{profile.adapter_id}: {scope_summary}",
                scope_summary=scope_summary,
                primary_adapter=profile.adapter_id,
                depends_on=depends_on,
            )
        )
    return candidates


def _build_dependency_links(
    active_profiles: list[AdapterProfile],
    candidates: list[PacketCandidate],
) -> list[CrossDomainDependency]:
    if len(candidates) <= 1:
        return []

    links: list[CrossDomainDependency] = []
    for idx in range(1, len(candidates)):
        prev_candidate = candidates[idx - 1]
        curr_candidate = candidates[idx]
        prev_domain = active_profiles[idx - 1].domain_type
        curr_domain = active_profiles[idx].domain_type
        domains = sorted({prev_domain, curr_domain})
        links.append(
            CrossDomainDependency(
                from_candidate=prev_candidate.candidate_id,
                to_candidate=curr_candidate.candidate_id,
                adapter_domains=domains,
            )
        )
    return links


def _cross_domain_flags(active_profiles: list[AdapterProfile]) -> list[str]:
    domains = sorted({profile.domain_type for profile in active_profiles})
    return domains if len(domains) > 1 else []


def _split_recommendations(
    scope_summary: str,
    active_profiles: list[AdapterProfile],
    candidates: list[PacketCandidate],
) -> list[str]:
    if len(active_profiles) > 1:
        return [candidate.candidate_id for candidate in candidates]

    lowered = scope_summary.lower()
    if " and " in lowered and len(scope_summary.split()) > 8 and candidates:
        return [candidates[0].candidate_id]
    return []


def _phase_segments(phase_summary: str, phase_candidates: list[str] | None) -> list[str]:
    if phase_candidates:
        normalized = [item.strip() for item in phase_candidates if item.strip()]
        if normalized:
            return normalized

    split = [segment.strip() for segment in _PHASE_SPLIT_PATTERN.split(phase_summary) if segment.strip()]
    return split if len(split) > 1 else [phase_summary.strip()]


def _build_phase_dependency_links(
    candidates: list[PacketCandidate],
    matched_profiles: list[AdapterProfile],
) -> list[CrossDomainDependency]:
    if len(candidates) <= 1:
        return []

    domain_by_adapter = {profile.adapter_id: profile.domain_type for profile in matched_profiles}
    links: list[CrossDomainDependency] = []
    for idx in range(1, len(candidates)):
        prev_candidate = candidates[idx - 1]
        curr_candidate = candidates[idx]
        domains = sorted(
            {
                domain_by_adapter.get(prev_candidate.primary_adapter or "", "generic"),
                domain_by_adapter.get(curr_candidate.primary_adapter or "", "generic"),
            }
        )
        links.append(
            CrossDomainDependency(
                from_candidate=prev_candidate.candidate_id,
                to_candidate=curr_candidate.candidate_id,
                adapter_domains=domains,
            )
        )
    return links


def _phase_split_recommendations(
    phase_summary: str, candidates: list[PacketCandidate]
) -> list[str]:
    if len(candidates) > 1:
        return [candidate.candidate_id for candidate in candidates]

    lowered = phase_summary.lower()
    if any(token in lowered for token in ("replan", "reshape", "phase")) and candidates:
        return [candidates[0].candidate_id]
    return []
