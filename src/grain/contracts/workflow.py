# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""Grain's published workflow vocabulary, re-exported from the `grain-contracts` distribution.

Spec §5.1 says Grain publishes `protocol`, `run`, `gate`, `artifact` and `stop_reason` from
`src/grain/contracts/`, and it still does — this module is that address. The definitions live one
package away, in `grain_contracts.workflow`, for one reason:

`grain-kit` mandatorily depends on `networkx`, `textual`, `pdfplumber`, `openpyxl`, `python-docx`
and `tree-sitter-language-pack`. Diwa is a FastAPI service that wants six enums and five dataclasses.
Making it install a TUI framework and a tree-sitter language pack to obtain them would be exactly the
coupling §9 warns against when it says Grain "is a CLI, not a library".

So the vocabulary ships as its own zero-dependency distribution. That is the first slice of the
storage-agnostic `grain-core` §9 names as the exit criterion for Diwa's temporary Missions runtime:
`grain-kit` becomes one consumer of the contract rather than its only shipping vehicle.

Import from wherever suits you — they are the same objects:

    from grain.contracts.workflow import Run      # inside grain
    from grain_contracts.workflow import Run      # anywhere else
"""

from grain_contracts.workflow import (
    PROTOCOL_API_VERSION,
    WORKFLOW_RUN_API_VERSION,
    Artifact,
    Gate,
    Mode,
    Protocol,
    Run,
    RunStatus,
    StepRecord,
    StepSpec,
    StepStatus,
    StopReason,
    Supervision,
)

__all__ = [
    "Artifact",
    "Gate",
    "Mode",
    "PROTOCOL_API_VERSION",
    "Protocol",
    "Run",
    "RunStatus",
    "StepRecord",
    "StepSpec",
    "StepStatus",
    "StopReason",
    "Supervision",
    "WORKFLOW_RUN_API_VERSION",
]
