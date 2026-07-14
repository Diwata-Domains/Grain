# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""Grain's workflow kernel, re-exported from the `grain-core` distribution.

The pure `advance()` reducer and the `RunStore` port used to live here. They now live one package
away, in `grain_core.kernel`, for the same reason the vocabulary moved to `grain_contracts`:

`grain-kit` mandatorily depends on `networkx`, `textual`, `pdfplumber`, `openpyxl`, `python-docx`
and `tree-sitter-language-pack`. Diwa's Missions runtime wants the reducer and the port, not a TUI
framework and a tree-sitter language pack. So the engine ships as its own zero-dependency
distribution — `grain-kit` becomes one consumer of the contract rather than its only shipping
vehicle, and Diwa's `PostgresRunStore` implements the same port grain-kit's filesystem store does.

`grain.engine.kernel` stays a valid address; the definitions are the same objects (so
`except grain.engine.kernel.ConcurrentModification` catches what `grain_core` raises):

    from grain.engine.kernel import advance     # inside grain
    from grain_core.kernel import advance        # anywhere else
"""

from grain_core.kernel import (
    DEFAULT_MAX_ATTEMPTS,
    AdvanceEvent,
    ArtifactProduced,
    ConcurrentModification,
    DiscardArtifact,
    Effect,
    GateApproved,
    GateRejected,
    InvalidEvent,
    RunStore,
    StepFailed,
    StepStarted,
    Transition,
    UnknownRun,
    advance,
)

__all__ = [
    "advance",
    "AdvanceEvent",
    "ArtifactProduced",
    "ConcurrentModification",
    "DEFAULT_MAX_ATTEMPTS",
    "DiscardArtifact",
    "Effect",
    "GateApproved",
    "GateRejected",
    "InvalidEvent",
    "RunStore",
    "StepFailed",
    "StepStarted",
    "Transition",
    "UnknownRun",
]
