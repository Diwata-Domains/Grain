# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field

OFFICE_ARTIFACT_KINDS: frozenset[str] = frozenset({"docx", "spreadsheet"})
OFFICE_OPERATION_MODES: frozenset[str] = frozenset(
    {"propose", "apply", "export-as-new-file"}
)
OFFICE_VALIDATION_STATES: frozenset[str] = frozenset(
    {"not_run", "passed", "partial", "failed"}
)
OFFICE_VALIDATOR_CATEGORIES: frozenset[str] = frozenset(
    {"structure", "reference", "policy"}
)


@dataclass(frozen=True)
class OfficeArtifactRef:
    artifact_kind: str
    source_path: str
    output_path: str = ""

    def __post_init__(self) -> None:
        if self.artifact_kind not in OFFICE_ARTIFACT_KINDS:
            raise ValueError(
                f"Invalid office artifact kind {self.artifact_kind!r}. "
                f"Must be one of: {sorted(OFFICE_ARTIFACT_KINDS)}"
            )
        if not self.source_path.strip():
            raise ValueError("OfficeArtifactRef.source_path must not be empty")


@dataclass(frozen=True)
class OfficeValidatorResult:
    validator_id: str
    category: str
    state: str
    summary: str
    findings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.category not in OFFICE_VALIDATOR_CATEGORIES:
            raise ValueError(
                f"Invalid office validator category {self.category!r}. "
                f"Must be one of: {sorted(OFFICE_VALIDATOR_CATEGORIES)}"
            )
        if self.state not in OFFICE_VALIDATION_STATES:
            raise ValueError(
                f"Invalid office validation state {self.state!r}. "
                f"Must be one of: {sorted(OFFICE_VALIDATION_STATES)}"
            )
        if not self.validator_id.strip():
            raise ValueError("OfficeValidatorResult.validator_id must not be empty")


@dataclass(frozen=True)
class OfficeWriteRequest:
    packet_id: str
    artifact: OfficeArtifactRef
    requested_mode: str = "propose"
    explicit_apply: bool = False
    high_risk: bool = False
    validation_state: str = "not_run"

    def __post_init__(self) -> None:
        if not self.packet_id.strip():
            raise ValueError("OfficeWriteRequest.packet_id must not be empty")
        if self.requested_mode not in OFFICE_OPERATION_MODES:
            raise ValueError(
                f"Invalid office operation mode {self.requested_mode!r}. "
                f"Must be one of: {sorted(OFFICE_OPERATION_MODES)}"
            )
        if self.validation_state not in OFFICE_VALIDATION_STATES:
            raise ValueError(
                f"Invalid office validation state {self.validation_state!r}. "
                f"Must be one of: {sorted(OFFICE_VALIDATION_STATES)}"
            )


@dataclass(frozen=True)
class OfficeWriteDecision:
    packet_id: str
    artifact: OfficeArtifactRef
    requested_mode: str
    resolved_mode: str
    review_required: bool = True
    validator_required: bool = True
    fallback_reason: str = ""
    residual_risks: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OfficeReviewBundle:
    packet_id: str
    artifact_paths: list[str]
    operation_mode: str
    change_summary: list[str] = field(default_factory=list)
    validator_results: list[OfficeValidatorResult] = field(default_factory=list)
    residual_risks: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.packet_id.strip():
            raise ValueError("OfficeReviewBundle.packet_id must not be empty")
        if self.operation_mode not in OFFICE_OPERATION_MODES:
            raise ValueError(
                f"Invalid office operation mode {self.operation_mode!r}. "
                f"Must be one of: {sorted(OFFICE_OPERATION_MODES)}"
            )
        if not self.artifact_paths:
            raise ValueError("OfficeReviewBundle.artifact_paths must not be empty")

