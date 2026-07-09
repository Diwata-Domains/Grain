# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Shared review-bundle and validator pipeline for office artifact writes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from grain.domain.office_writes import OfficeValidatorResult, OfficeReviewBundle
from grain.services.docx_write_service import DocxWriteResult
from grain.services.office_write_service import OfficeWriteService
from grain.services.spreadsheet_write_service import SpreadsheetWriteResult


@dataclass(frozen=True)
class OfficeArtifactReviewResult:
    review_bundle: OfficeReviewBundle
    validator_results: list[OfficeValidatorResult]


class OfficeArtifactReviewService:
    """Build consistent validator output and review bundles for office writes."""

    def __init__(self, office_write_service: OfficeWriteService | None = None) -> None:
        self._office_write_service = office_write_service or OfficeWriteService()

    def build_docx_review_result(
        self,
        *,
        root: Path,
        packet_id: str,
        result: DocxWriteResult,
    ) -> OfficeArtifactReviewResult:
        validator_results = self._validate_docx_result(root=root, result=result)
        bundle = self._office_write_service.build_review_bundle(
            packet_id=packet_id,
            decision=result.decision,
            validator_results=validator_results,
            change_summary=result.change_summary,
        )
        return OfficeArtifactReviewResult(
            review_bundle=bundle,
            validator_results=validator_results,
        )

    def build_spreadsheet_review_result(
        self,
        *,
        root: Path,
        packet_id: str,
        result: SpreadsheetWriteResult,
    ) -> OfficeArtifactReviewResult:
        validator_results = self._validate_spreadsheet_result(root=root, result=result)
        bundle = self._office_write_service.build_review_bundle(
            packet_id=packet_id,
            decision=result.decision,
            validator_results=validator_results,
            change_summary=result.change_summary,
        )
        return OfficeArtifactReviewResult(
            review_bundle=bundle,
            validator_results=validator_results,
        )

    def _validate_docx_result(
        self,
        *,
        root: Path,
        result: DocxWriteResult,
    ) -> list[OfficeValidatorResult]:
        output_path = root / result.output_path
        structure_state = (
            "passed"
            if result.headings_preserved > 0 and result.tables_preserved >= 0
            else "partial"
        )
        reference_state = "passed" if output_path.exists() else "failed"
        policy_state = (
            "passed"
            if result.decision.resolved_mode in {"propose", "export-as-new-file"}
            else "failed"
        )

        return [
            OfficeValidatorResult(
                validator_id="docx-structure",
                category="structure",
                state=structure_state,
                summary=(
                    "Document preserved heading and table structure."
                    if structure_state == "passed"
                    else "Document output exists, but structural preservation signals are partial."
                ),
                findings=(
                    []
                    if structure_state == "passed"
                    else ["heading preservation could not be fully confirmed"]
                ),
            ),
            OfficeValidatorResult(
                validator_id="docx-reference",
                category="reference",
                state=reference_state,
                summary=(
                    "Referenced `.docx` output file exists."
                    if reference_state == "passed"
                    else "Referenced `.docx` output file is missing."
                ),
                findings=(
                    []
                    if reference_state == "passed"
                    else [f"missing output file: {result.output_path}"]
                ),
            ),
            OfficeValidatorResult(
                validator_id="docx-policy",
                category="policy",
                state=policy_state,
                summary=(
                    "Write mode respects Phase 23 policy."
                    if policy_state == "passed"
                    else "Write mode violates Phase 23 office policy."
                ),
                findings=(
                    []
                    if policy_state == "passed"
                    else [f"disallowed mode: {result.decision.resolved_mode}"]
                ),
            ),
        ]

    def _validate_spreadsheet_result(
        self,
        *,
        root: Path,
        result: SpreadsheetWriteResult,
    ) -> list[OfficeValidatorResult]:
        output_path = root / result.output_path
        structure_state = (
            "passed"
            if result.touched_sheets and result.touched_ranges
            else "partial"
        )
        reference_state = "passed" if output_path.exists() else "failed"
        policy_state = (
            "passed"
            if result.decision.resolved_mode in {"propose", "export-as-new-file"}
            else "failed"
        )

        return [
            OfficeValidatorResult(
                validator_id="spreadsheet-structure",
                category="structure",
                state=structure_state,
                summary=(
                    "Workbook change summary includes touched sheets and ranges."
                    if structure_state == "passed"
                    else "Workbook output exists, but touched-sheet or touched-range signals are partial."
                ),
                findings=(
                    []
                    if structure_state == "passed"
                    else ["touched sheet or range reporting is incomplete"]
                ),
            ),
            OfficeValidatorResult(
                validator_id="spreadsheet-reference",
                category="reference",
                state=reference_state,
                summary=(
                    "Referenced spreadsheet output file exists."
                    if reference_state == "passed"
                    else "Referenced spreadsheet output file is missing."
                ),
                findings=(
                    []
                    if reference_state == "passed"
                    else [f"missing output file: {result.output_path}"]
                ),
            ),
            OfficeValidatorResult(
                validator_id="spreadsheet-policy",
                category="policy",
                state=policy_state,
                summary=(
                    "Write mode respects Phase 23 policy."
                    if policy_state == "passed"
                    else "Write mode violates Phase 23 office policy."
                ),
                findings=(
                    []
                    if policy_state == "passed"
                    else [f"disallowed mode: {result.decision.resolved_mode}"]
                ),
            ),
        ]
