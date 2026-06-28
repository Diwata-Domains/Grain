# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Authority-order validator.

Validates authority-related constraints across a DocumentRegistry and manifest:
- each record's authority value is from the allowed set
- canonical-layer records are not editable by agents
- rules.authority_order is a non-empty list

Returns a list of error strings. An empty list means all checks passed.
"""

from grain.domain.documents import DocumentRegistry

# Allowed authority values from data_contracts.md Section 6.2
ALLOWED_AUTHORITY_VALUES = {
    "highest",
    "high",
    "highest_runtime",
    "high_runtime",
    "secondary",
    "informational",
    "advisory",
}


def validate_authority(registry: DocumentRegistry, manifest: dict) -> list[str]:
    """Validate authority-related constraints on the registry and manifest.

    Args:
        registry: Populated DocumentRegistry from build_registry().
        manifest: Parsed manifest dict (used to check rules.authority_order).

    Returns:
        List of error strings. Empty list means all checks passed.
    """
    errors: list[str] = []

    for record in registry.all():
        # authority value must be from the allowed set
        if record.authority not in ALLOWED_AUTHORITY_VALUES:
            errors.append(
                f"Doc '{record.id}': invalid authority value '{record.authority}'"
            )
        # canonical documents must not be editable by agents
        if record.layer == "canonical" and record.editable_by_agents:
            errors.append(
                f"Doc '{record.id}' (canonical): editable_by_agents must be false"
            )

    # rules.authority_order must be a non-empty list
    rules = manifest.get("rules") if isinstance(manifest, dict) else None
    if not isinstance(rules, dict):
        errors.append("manifest 'rules' section is missing or not a mapping")
    else:
        authority_order = rules.get("authority_order")
        if not isinstance(authority_order, list) or len(authority_order) == 0:
            errors.append("rules.authority_order must be a non-empty list")

    return errors
