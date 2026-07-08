# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Intake service — imports promoted Assay tickets as Grain task packets.

This is the "pull" side of the Assay-to-Grain seam: Assay's Task-5 API exposes
``GET /promotions`` (tickets a human has promoted out of triage) and
``POST /promotions/{verification_id}/ack`` (marks one imported). This module
GETs the list, mints a real Grain ``TASK-####`` packet for each ticket not
already imported, seeds the packet's ``task.md`` with the ticket's fields, and
then acks it.

Idempotency is by ``assay_vid``: a ticket whose ``verification_id`` already
appears as ``assay_vid:`` in any existing ``tasks/**/task.md`` is skipped, so a
retried pull never creates a duplicate packet.

Packets are created *before* the ack call. If the ack request fails, the
packet still exists on disk (nothing is lost) and the assay_vid dedup guard
means a retried pull will not create a second packet for the same ticket — it
will just retry the ack.

HTTP is funneled through the injectable ``_urllib_get`` / ``_urllib_post``
module functions (mirroring ``github_service``'s ``_urllib_post``) so tests
can monkeypatch them without touching the network or adding a new HTTP-mocking
dependency.
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from grain.services import task_service

_VID_LINE = re.compile(r"^assay_vid:\s*(\S+)\s*$", re.MULTILINE)
_TASK_NUM_IN_DIR = re.compile(r"-T(\d+)-")


@dataclass
class IntakeResult:
    """Outcome of one ``intake pull`` run."""

    ok: bool = True
    imported: list[dict] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _existing_assay_vids(root: Path) -> set[str]:
    """Scan tasks/**/task.md for already-imported assay_vid values."""
    tasks_root = root / "tasks"
    vids: set[str] = set()
    if not tasks_root.exists():
        return vids
    for task_md in tasks_root.glob("**/task.md"):
        try:
            text = task_md.read_text(encoding="utf-8")
        except OSError:
            continue
        vids.update(_VID_LINE.findall(text))
    return vids


def _next_task_num(root: Path, phase: int) -> int:
    """Return the next available within-phase T-number (max existing + 1, else 1)."""
    tasks_root = root / "tasks"
    if not tasks_root.exists():
        return 1
    max_num = 0
    for entry in tasks_root.glob(f"P{phase}-T*"):
        if not entry.is_dir():
            continue
        match = _TASK_NUM_IN_DIR.search(entry.name)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def _seed_task_md(packet_dir: Path, ticket: dict) -> None:
    """Append assay front-matter + body to a freshly created packet's task.md.

    Appends rather than overwriting so the template's required sections
    (``## Metadata`` etc., which ``grain task validate`` parses) stay intact.
    """
    task_md = packet_dir / "task.md"
    existing = task_md.read_text(encoding="utf-8")
    addendum = (
        "\n---\n"
        f"assay_vid: {ticket.get('verification_id', '')}\n"
        f"source_url: {ticket.get('url', '')}\n"
        f"severity: {ticket.get('severity', '')}\n"
        f"priority: {ticket.get('priority', '')}\n"
        "---\n"
        f"{ticket.get('summary', '')}\n\n"
        f"Reported: {ticket.get('user_comment', '')}\n"
        f"Remediation: {ticket.get('remediation', '')}\n"
        f"Screenshot: {ticket.get('screenshot_ref', '')}\n"
    )
    task_md.write_text(existing + addendum, encoding="utf-8")


def pull_promotions(
    root: Path,
    phase: int,
    task_num: int | None,
    endpoint: str,
    key: str,
    *,
    http_get: Callable[..., dict] | None = None,
    http_post: Callable[..., dict] | None = None,
) -> IntakeResult:
    """Pull promoted Assay tickets and mint Grain task packets for the new ones.

    ``task_num`` is the starting within-phase T-number; when ``None`` it is
    computed as the next available number for ``phase``. When a pull imports
    multiple tickets, the T-number is incremented for each new packet so they
    don't collide.
    """
    getter = http_get if http_get is not None else _urllib_get
    poster = http_post if http_post is not None else _urllib_post
    headers = {"X-Assay-Key": key}

    result = IntakeResult()

    try:
        response = getter(f"{endpoint.rstrip('/')}/promotions", headers)
    except Exception as exc:  # noqa: BLE001 — surfaced as an expected failure
        result.ok = False
        result.errors.append(f"failed to fetch promotions from Assay: {exc}")
        return result

    tickets = response.get("promotions", []) if isinstance(response, dict) else []
    existing_vids = _existing_assay_vids(root)
    next_num = task_num if task_num is not None else _next_task_num(root, phase)

    for ticket in tickets:
        vid = str(ticket.get("verification_id") or "")
        if not vid:
            result.errors.append("promotion missing verification_id; skipped")
            continue
        if vid in existing_vids:
            # A packet for this vid already exists, so don't create another
            # one — but GET /promotions only ever returns tickets Assay still
            # considers `promoted` (not `imported`), so if the vid shows up
            # here AND is already on disk, the ack from whatever pull created
            # the packet must never have landed. Retry it now: it's always
            # safe (idempotent on Assay's side) and this is the only way a
            # stuck-`promoted` ticket ever self-heals.
            result.skipped.append(vid)
            try:
                poster(f"{endpoint.rstrip('/')}/promotions/{vid}/ack", headers)
            except Exception as exc:  # noqa: BLE001 — surfaced as an expected failure
                result.errors.append(f"ack retry failed for {vid}: {exc}")
            continue

        create_result = task_service.create_packet_directory(
            root, phase, next_num, title=ticket.get("summary", "")
        )
        if not create_result.ok:
            result.errors.append(
                f"failed to create packet for {vid}: {'; '.join(create_result.errors)}"
            )
            continue

        packet_dir = root / create_result.files_created[0]
        _seed_task_md(packet_dir, ticket)
        existing_vids.add(vid)
        next_num += 1

        try:
            poster(f"{endpoint.rstrip('/')}/promotions/{vid}/ack", headers)
        except Exception as exc:  # noqa: BLE001 — surfaced as an expected failure
            result.errors.append(f"ack failed for {vid}: {exc}")

        result.imported.append({
            "task_id": create_result.task_id,
            "assay_vid": vid,
            "packet_dir": str(packet_dir.relative_to(root)),
        })

    result.ok = not result.errors
    return result


# ── HTTP wrappers (injectable; mocked in tests) ────────────────────────────────

def _urllib_get(url: str, headers: dict[str, str]) -> dict:
    """GET JSON from Assay and return the parsed response dict.

    Kept tiny and dependency-free (stdlib urllib) so it can be monkeypatched in
    tests. Raises on transport/HTTP errors; ``pull_promotions`` converts those
    into an expected failure result.
    """
    request = urllib.request.Request(url, method="GET")
    for name, value in headers.items():
        request.add_header(name, value)
    with urllib.request.urlopen(request) as resp:  # noqa: S310 — endpoint is operator-configured
        return json.loads(resp.read().decode("utf-8"))


def _urllib_post(url: str, headers: dict[str, str]) -> dict:
    """POST (empty body) to Assay and return the parsed response dict."""
    request = urllib.request.Request(url, data=b"", method="POST")
    for name, value in headers.items():
        request.add_header(name, value)
    with urllib.request.urlopen(request) as resp:  # noqa: S310 — endpoint is operator-configured
        return json.loads(resp.read().decode("utf-8"))
