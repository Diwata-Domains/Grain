# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""The current-phase parser must tolerate hand-edited separators.

A `## Current Phase` line reading `Phase 1 - Foundation` (hyphen), an en dash,
or a colon must still parse. Before this, only an em dash was accepted, so a
hand-edited focus doc hard-blocked `grain workflow next` with
`required_docs_invalid` / "unable to parse current phase".
"""

from pathlib import Path

import pytest

from grain.services.workflow_service import _read_current_phase


def _write_focus(tmp_path: Path, phase_line: str) -> Path:
    focus = tmp_path / "current_focus.md"
    focus.write_text(
        f"# Current Focus\n\n## Current Phase\n{phase_line}\n",
        encoding="utf-8",
    )
    return focus


@pytest.mark.parametrize(
    "phase_line",
    [
        "Phase 1 — Foundation",  # em dash (canonical)
        "Phase 1 – Foundation",  # en dash
        "Phase 1 - Foundation",  # hyphen
        "Phase 1: Foundation",   # colon
        "Phase 1—Foundation",    # em dash, no spaces
    ],
)
def test_read_current_phase_accepts_separators(tmp_path, phase_line):
    focus = _write_focus(tmp_path, phase_line)
    assert _read_current_phase(focus) == "1"
