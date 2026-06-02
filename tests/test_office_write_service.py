from __future__ import annotations

import pytest

from grain.domain import (
    OfficeArtifactRef,
    OfficeValidatorResult,
    OfficeWriteRequest,
)
from grain.services.office_write_service import OfficeWriteService


def test_apply_requires_explicit_operator_intent() -> None:
    service = OfficeWriteService()
    request = OfficeWriteRequest(
        packet_id="TASK-0152",
        artifact=OfficeArtifactRef("docx", "docs/brief.docx"),
        requested_mode="apply",
        validation_state="passed",
    )

    decision = service.resolve_write_mode(request)

    assert decision.resolved_mode == "propose"
    assert "explicit operator intent" in decision.fallback_reason


def test_apply_with_partial_validation_falls_back_to_export() -> None:
    service = OfficeWriteService()
    request = OfficeWriteRequest(
        packet_id="TASK-0152",
        artifact=OfficeArtifactRef("spreadsheet", "data/report.xlsx"),
        requested_mode="apply",
        explicit_apply=True,
        validation_state="partial",
    )

    decision = service.resolve_write_mode(request)

    assert decision.resolved_mode == "export-as-new-file"
    assert "partial validation" in decision.fallback_reason
    assert decision.residual_risks == ["validation coverage is partial"]


def test_apply_with_high_risk_falls_back_to_export() -> None:
    service = OfficeWriteService()
    request = OfficeWriteRequest(
        packet_id="TASK-0152",
        artifact=OfficeArtifactRef("docx", "docs/brief.docx"),
        requested_mode="apply",
        explicit_apply=True,
        high_risk=True,
        validation_state="passed",
    )

    decision = service.resolve_write_mode(request)

    assert decision.resolved_mode == "export-as-new-file"
    assert decision.residual_risks == ["operation flagged as high risk"]


def test_apply_without_validation_falls_back_to_propose() -> None:
    service = OfficeWriteService()
    request = OfficeWriteRequest(
        packet_id="TASK-0152",
        artifact=OfficeArtifactRef("spreadsheet", "data/report.xlsx"),
        requested_mode="apply",
        explicit_apply=True,
        validation_state="not_run",
    )

    decision = service.resolve_write_mode(request)

    assert decision.resolved_mode == "propose"
    assert decision.residual_risks == ["validation has not run yet"]


def test_propose_mode_remains_stable() -> None:
    service = OfficeWriteService()
    request = OfficeWriteRequest(
        packet_id="TASK-0152",
        artifact=OfficeArtifactRef("docx", "docs/brief.docx"),
        requested_mode="propose",
        validation_state="not_run",
    )

    decision = service.resolve_write_mode(request)

    assert decision.resolved_mode == "propose"
    assert decision.fallback_reason == ""


def test_build_review_bundle_collects_paths_and_validator_results() -> None:
    service = OfficeWriteService()
    request = OfficeWriteRequest(
        packet_id="TASK-0152",
        artifact=OfficeArtifactRef(
            "spreadsheet",
            "data/report.xlsx",
            output_path="tasks/P23-T01-TASK-0152/report.preview.xlsx",
        ),
        requested_mode="apply",
        explicit_apply=True,
        validation_state="partial",
    )
    decision = service.resolve_write_mode(request)
    validators = [
        OfficeValidatorResult(
            validator_id="sheet-structure",
            category="structure",
            state="partial",
            summary="Formula coverage is incomplete.",
        ),
        OfficeValidatorResult(
            validator_id="policy-review",
            category="policy",
            state="passed",
            summary="No policy violations detected.",
        ),
    ]

    bundle = service.build_review_bundle(
        packet_id="TASK-0152",
        decision=decision,
        validator_results=validators,
        change_summary=["Updated revenue formulas in Summary sheet."],
        residual_risks=["manual workbook review recommended"],
    )

    assert bundle.packet_id == "TASK-0152"
    assert bundle.operation_mode == "export-as-new-file"
    assert bundle.artifact_paths == [
        "data/report.xlsx",
        "tasks/P23-T01-TASK-0152/report.preview.xlsx",
    ]
    assert bundle.change_summary == ["Updated revenue formulas in Summary sheet."]
    assert bundle.validator_results == validators
    assert bundle.residual_risks == [
        "validation coverage is partial",
        "manual workbook review recommended",
    ]


def test_invalid_artifact_kind_raises() -> None:
    with pytest.raises(ValueError, match="Invalid office artifact kind"):
        OfficeArtifactRef("pdf", "docs/spec.pdf")


def test_invalid_validator_category_raises() -> None:
    with pytest.raises(ValueError, match="Invalid office validator category"):
        OfficeValidatorResult(
            validator_id="x",
            category="format",
            state="passed",
            summary="bad",
        )
