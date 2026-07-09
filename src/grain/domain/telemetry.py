# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Telemetry domain model — the Grain-side emission contract for Pulse.

Pulse is the planned Diwata-wide telemetry layer; Grain only emits typed,
versioned :class:`TelemetryEvent` objects at key workflow moments. Transport and
aggregation are Pulse's responsibility. Events are versioned so the contract can
evolve without breaking downstream consumers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Event type identifiers — never rename without bumping the event version, since
# Pulse consumers key off these strings.
EVENT_PHASE_CLOSE = "phase.close"
EVENT_TASK_CLOSE = "task.close"
EVENT_SUGGEST_ACCEPT = "suggest.accept"
EVENT_WORKFLOW_NEXT_STOP = "workflow.next.stop_reason"

# Current schema version for emitted events. Bump on any breaking payload change.
TELEMETRY_EVENT_VERSION = 1


@dataclass
class TelemetryEvent:
    """A single typed, versioned telemetry event.

    ``event_type`` is one of the module-level ``EVENT_*`` constants, ``version``
    is the schema version, ``timestamp`` is an ISO-8601 UTC string, and
    ``payload`` carries event-specific fields (no PII; identifiers and reasons
    only).
    """

    event_type: str
    version: int = TELEMETRY_EVENT_VERSION
    timestamp: str = ""
    payload: dict = field(default_factory=dict)
