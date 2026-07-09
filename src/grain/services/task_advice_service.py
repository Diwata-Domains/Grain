# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Proposal-only ranked task-advice helpers."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from grain.domain.embedding import ScoredCandidate
from grain.domain.ranking import RankedCandidate
from grain.services.embedding_resolver import EmbeddingProviderResolver
from grain.services.ranking_service import RankingCandidateInput, rank_candidates
from grain.services.workflow_service import _read_current_phase

_BACKLOG_DOC = "docs/working/backlog.md"
_CURRENT_FOCUS_DOC = "docs/working/current_focus.md"
_PHASE_HEADING = re.compile(r"^##\s+(?:\d+\.\s+)?Phase\s+(\d+)\s+—")
_TASK_HEADING = re.compile(r"^###\s+(P(\d+)-T(\d+))\s+—\s+(.+)$")
_BACKLOG_STATUS = re.compile(r"^- \*\*Status:\*\*\s*(\S+)")


@dataclass
class AdvisoryTaskCandidate:
    task_ref: str
    title: str
    status: str
    backlog_index: int


def advise_next_tasks(
    root: Path,
    scope_summary: str,
    *,
    embedding_resolver: EmbeddingProviderResolver | None = None,
) -> dict[str, object]:
    """Return ranked proposal-only task suggestions for the active phase."""
    current_focus_path = root / _CURRENT_FOCUS_DOC
    backlog_path = root / _BACKLOG_DOC
    if not current_focus_path.exists() or not backlog_path.exists():
        return {}

    current_phase = _read_current_phase(current_focus_path)
    if not current_phase:
        return {}

    tasks = _read_phase_task_candidates(backlog_path, current_phase)
    if not tasks:
        return {}

    ready = [task for task in tasks if task.status == "ready"]
    draft = [task for task in tasks if task.status == "draft"]
    eligible = ready if ready else draft
    if not eligible:
        return {}

    resolver = embedding_resolver or EmbeddingProviderResolver()
    provider, resolved = resolver.resolve_root(root)

    candidate_texts = {
        task.task_ref: f"{task.task_ref} {task.title}".strip()
        for task in eligible
    }
    text_to_ref = {text: task_ref for task_ref, text in candidate_texts.items()}
    semantic_ranked = provider.score(scope_summary, list(candidate_texts.values()))
    semantic_scores = _serialize_scored_candidates(semantic_ranked, text_to_ref)
    semantic_by_ref = {item["task_ref"]: item["score"] for item in semantic_scores}
    ranked = rank_candidates(
        [
            RankingCandidateInput(
                candidate=task.task_ref,
                graph_depth=task.backlog_index,
                semantic_score=float(semantic_by_ref.get(task.task_ref, 0.0)),
                authority="secondary",
                packet_priority=1.0 if task.status == "ready" else 0.6,
                metadata={"title": task.title, "status": task.status},
            )
            for task in eligible
        ]
    )

    provider_status = asdict(resolved.provider_status) if resolved.provider_status is not None else None
    return {
        "phase": current_phase,
        "candidate_pool_status": "ready" if ready else "draft",
        "configured_provider": resolved.configured_provider,
        "active_provider": resolved.active_provider,
        "configured_model": resolved.configured_model,
        "active_model": resolved.active_model,
        "fallback_active": resolved.fallback_active,
        "fallback_reason": resolved.fallback_reason,
        "provider_status": provider_status,
        "semantic_scores": semantic_scores,
        "ranked_tasks": _serialize_ranked_tasks(ranked, {task.task_ref: task for task in eligible}),
    }


def _read_phase_task_candidates(backlog_path: Path, phase_number: str) -> list[AdvisoryTaskCandidate]:
    if not backlog_path.exists():
        return []

    lines = backlog_path.read_text(encoding="utf-8").splitlines()
    current_phase = ""
    current_task_ref = ""
    current_title = ""
    current_status = ""
    backlog_index = 0
    tasks: list[AdvisoryTaskCandidate] = []

    for line in lines:
        phase_match = _PHASE_HEADING.match(line)
        if phase_match:
            if current_phase == phase_number and current_task_ref and current_status:
                tasks.append(
                    AdvisoryTaskCandidate(
                        task_ref=current_task_ref,
                        title=current_title,
                        status=current_status,
                        backlog_index=backlog_index,
                    )
                )
                backlog_index += 1
            current_phase = phase_match.group(1)
            current_task_ref = ""
            current_title = ""
            current_status = ""
            continue

        heading_match = _TASK_HEADING.match(line)
        if heading_match:
            if current_phase == phase_number and current_task_ref and current_status:
                tasks.append(
                    AdvisoryTaskCandidate(
                        task_ref=current_task_ref,
                        title=current_title,
                        status=current_status,
                        backlog_index=backlog_index,
                    )
                )
                backlog_index += 1
            current_task_ref = heading_match.group(1)
            current_title = heading_match.group(4)
            current_status = ""
            continue

        if current_phase != phase_number or not current_task_ref:
            continue

        status_match = _BACKLOG_STATUS.match(line)
        if status_match:
            current_status = status_match.group(1)

    if current_phase == phase_number and current_task_ref and current_status:
        tasks.append(
            AdvisoryTaskCandidate(
                task_ref=current_task_ref,
                title=current_title,
                status=current_status,
                backlog_index=backlog_index,
            )
        )

    return tasks


def _serialize_scored_candidates(
    ranked: list[ScoredCandidate],
    text_to_ref: dict[str, str],
) -> list[dict[str, object]]:
    return [
        {
            "task_ref": text_to_ref[item.candidate],
            "score": item.score,
            "provider_id": item.provider_id,
            "metadata": item.metadata,
        }
        for item in ranked
        if item.candidate in text_to_ref
    ]


def _serialize_ranked_tasks(
    ranked: list[RankedCandidate],
    candidates: dict[str, AdvisoryTaskCandidate],
) -> list[dict[str, object]]:
    payload: list[dict[str, object]] = []
    for item in ranked:
        candidate = candidates[item.candidate]
        payload.append(
            {
                "task_ref": item.candidate,
                "title": candidate.title,
                "status": candidate.status,
                "total_score": item.total_score,
                "components": [
                    {
                        "signal_id": component.signal_id,
                        "raw_score": component.raw_score,
                        "weight": component.weight,
                        "weighted_score": component.weighted_score,
                        "detail": component.detail,
                    }
                    for component in item.components
                ],
            }
        )
    return payload
