# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Shared safety-mode and review-bundle helpers for office artifact writes."""

from __future__ import annotations

from grain.domain.office_writes import (
    OfficeReviewBundle,
    OfficeValidatorResult,
    OfficeWriteDecision,
    OfficeWriteRequest,
)


class OfficeWriteService:
    """Resolve safe operation modes for office writes and build review bundles."""

    def resolve_write_mode(self, request: OfficeWriteRequest) -> OfficeWriteDecision:
        resolved_mode = request.requested_mode
        fallback_reason = ""
        residual_risks: list[str] = []

        if request.requested_mode == "apply" and not request.explicit_apply:
            resolved_mode = "propose"
            fallback_reason = "explicit operator intent is required for in-place office mutations"
        elif request.requested_mode == "apply" and request.validation_state == "partial":
            resolved_mode = "export-as-new-file"
            fallback_reason = "partial validation cannot approve an in-place office mutation"
            residual_risks.append("validation coverage is partial")
        elif request.requested_mode == "apply" and request.high_risk:
            resolved_mode = "export-as-new-file"
            fallback_reason = "high-risk office mutations must stay comparison-first"
            residual_risks.append("operation flagged as high risk")
        elif request.requested_mode == "apply" and request.validation_state in {"failed", "not_run"}:
            resolved_mode = "propose"
            fallback_reason = "in-place office mutations require passing validation first"
            if request.validation_state == "failed":
                residual_risks.append("validation did not pass")
            else:
                residual_risks.append("validation has not run yet")

        return OfficeWriteDecision(
            packet_id=request.packet_id,
            artifact=request.artifact,
            requested_mode=request.requested_mode,
            resolved_mode=resolved_mode,
            fallback_reason=fallback_reason,
            residual_risks=residual_risks,
        )

    def build_review_bundle(
        self,
        *,
        packet_id: str,
        decision: OfficeWriteDecision,
        validator_results: list[OfficeValidatorResult],
        change_summary: list[str],
        residual_risks: list[str] | None = None,
    ) -> OfficeReviewBundle:
        artifact_paths = [decision.artifact.source_path]
        if decision.artifact.output_path:
            artifact_paths.append(decision.artifact.output_path)

        merged_risks = list(decision.residual_risks)
        if residual_risks:
            for risk in residual_risks:
                if risk not in merged_risks:
                    merged_risks.append(risk)

        if any(item.state == "partial" for item in validator_results):
            if "validation coverage is partial" not in merged_risks:
                merged_risks.append("validation coverage is partial")
        if any(item.state == "failed" for item in validator_results):
            if "one or more validators failed" not in merged_risks:
                merged_risks.append("one or more validators failed")

        return OfficeReviewBundle(
            packet_id=packet_id,
            artifact_paths=artifact_paths,
            operation_mode=decision.resolved_mode,
            change_summary=list(change_summary),
            validator_results=list(validator_results),
            residual_risks=merged_risks,
        )
