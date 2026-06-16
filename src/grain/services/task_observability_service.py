# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from grain.domain.packets import find_packet_dir

OBSERVABILITY_FILENAME = "observability.json"
VALID_TASK_STAGES = {"execute", "review", "close"}


@dataclass
class TaskObservabilityRecord:
    task_id: str
    packet_dir: str
    executor_identity: str = ""
    model_class: str = ""
    last_stage: str = ""
    last_stage_at: str = ""
    last_workflow_action: str = ""
    last_workflow_action_at: str = ""
    started_at: str = ""
    updated_at: str = ""
    stage_timestamps: dict[str, str] = field(default_factory=dict)


def read_task_observability(root: Path, task_id: str) -> tuple[TaskObservabilityRecord | None, Path | None]:
    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return None, None

    path = packet_dir / OBSERVABILITY_FILENAME
    if not path.exists():
        return TaskObservabilityRecord(task_id=task_id, packet_dir=str(packet_dir.relative_to(root))), path

    payload = json.loads(path.read_text(encoding="utf-8"))
    record = TaskObservabilityRecord(
        task_id=payload.get("task_id", task_id),
        packet_dir=payload.get("packet_dir", str(packet_dir.relative_to(root))),
        executor_identity=payload.get("executor_identity", ""),
        model_class=payload.get("model_class", ""),
        last_stage=payload.get("last_stage", ""),
        last_stage_at=payload.get("last_stage_at", ""),
        last_workflow_action=payload.get("last_workflow_action", ""),
        last_workflow_action_at=payload.get("last_workflow_action_at", ""),
        started_at=payload.get("started_at", ""),
        updated_at=payload.get("updated_at", ""),
        stage_timestamps=dict(payload.get("stage_timestamps", {})),
    )
    return record, path


def update_task_observability(
    root: Path,
    task_id: str,
    *,
    executor_identity: str | None = None,
    model_class: str | None = None,
    stage: str | None = None,
    workflow_action: str | None = None,
    event_timestamp: str | None = None,
) -> tuple[TaskObservabilityRecord, Path]:
    record, path = read_task_observability(root, task_id)
    if record is None or path is None:
        raise FileNotFoundError(f"packet '{task_id}' not found")

    if stage and stage not in VALID_TASK_STAGES:
        raise ValueError(f"invalid stage: {stage}")

    now = event_timestamp or _now_iso()

    if executor_identity is not None:
        record.executor_identity = executor_identity
    if model_class is not None:
        record.model_class = model_class
    if stage:
        record.last_stage = stage
        record.last_stage_at = now
        record.stage_timestamps[f"{stage}_at"] = now
        if not record.started_at and stage == "execute":
            record.started_at = now
    if workflow_action:
        record.last_workflow_action = workflow_action
        record.last_workflow_action_at = now
        if not record.started_at:
            record.started_at = now

    record.updated_at = now
    path.write_text(json.dumps(_record_to_dict(record), indent=2) + "\n", encoding="utf-8")
    return record, path


def _record_to_dict(record: TaskObservabilityRecord) -> dict:
    return {
        "task_id": record.task_id,
        "packet_dir": record.packet_dir,
        "executor_identity": record.executor_identity,
        "model_class": record.model_class,
        "last_stage": record.last_stage,
        "last_stage_at": record.last_stage_at,
        "last_workflow_action": record.last_workflow_action,
        "last_workflow_action_at": record.last_workflow_action_at,
        "started_at": record.started_at,
        "updated_at": record.updated_at,
        "stage_timestamps": dict(record.stage_timestamps),
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
