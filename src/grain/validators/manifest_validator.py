# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Manifest schema validator.

Validates that a parsed manifest dict conforms to the schema defined in
data_contracts.md Sections 5 and 6. Returns a list of error strings.
An empty list means the manifest is structurally valid.
"""

REQUIRED_TOP_LEVEL = ["version", "project", "canonical", "working", "runtime", "tasks", "rules"]

REQUIRED_DOC_ENTRY_FIELDS = ["id", "path", "purpose", "authority", "editable_by_agents", "read_when"]

REQUIRED_TASKS_FIELDS = ["root", "packet_files", "patch_dir", "status_values", "id_format"]

REQUIRED_RULES_SUBKEYS = [
    "authority_order",
    "canonical_change_policy",
    "context_policy",
    "execution_policy",
    "completion_policy",
]

_REQUIRED_POLICY_FIELDS = {
    "canonical_change_policy": ["direct_agent_edits_allowed", "require_human_approval", "proposal_location"],
    "context_policy": ["load_minimum_required_docs", "prefer_task_packet_context", "avoid_full_repo_context"],
    "execution_policy": ["use_task_packets", "one_task_one_packet", "patch_over_rewrite", "preserve_doc_separation"],
    "completion_policy": [
        "require_defined_deliverable",
        "require_results_recorded",
        "require_rule_check",
        "require_user_approval",
        "require_verification_pass",
        "allow_close_when_verification_not_run",
    ],
}

_DOC_LAYERS = ["canonical", "working", "runtime"]


def validate_manifest_schema(manifest: dict) -> list[str]:
    """Validate the structural schema of a parsed manifest dict.

    Args:
        manifest: Parsed manifest dict from load_manifest().

    Returns:
        List of error strings. Empty list means structurally valid.
    """
    errors: list[str] = []

    # Top-level required sections
    for key in REQUIRED_TOP_LEVEL:
        if key not in manifest:
            errors.append(f"Missing required top-level section: '{key}'")

    if errors:
        # Cannot safely validate nested structures if top-level keys are absent
        return errors

    # Doc entry validation for canonical, working, runtime layers
    for layer in _DOC_LAYERS:
        entries = manifest.get(layer)
        if not isinstance(entries, list):
            errors.append(f"Section '{layer}' must be a list")
            continue
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"Entry {i} in '{layer}' must be a mapping")
                continue
            for field in REQUIRED_DOC_ENTRY_FIELDS:
                if field not in entry:
                    entry_id = entry.get("id", f"index {i}")
                    errors.append(f"Doc entry '{entry_id}' in '{layer}' missing required field: '{field}'")
            # editable_by_agents must be boolean
            if "editable_by_agents" in entry and not isinstance(entry["editable_by_agents"], bool):
                entry_id = entry.get("id", f"index {i}")
                errors.append(f"Doc entry '{entry_id}' in '{layer}': 'editable_by_agents' must be a boolean")
            # read_when must be a non-empty list
            if "read_when" in entry:
                read_when = entry["read_when"]
                if not isinstance(read_when, list) or len(read_when) == 0:
                    entry_id = entry.get("id", f"index {i}")
                    errors.append(f"Doc entry '{entry_id}' in '{layer}': 'read_when' must be a non-empty list")

    # Tasks section validation
    tasks = manifest.get("tasks", {})
    if not isinstance(tasks, dict):
        errors.append("Section 'tasks' must be a mapping")
    else:
        for field in REQUIRED_TASKS_FIELDS:
            if field not in tasks:
                errors.append(f"Section 'tasks' missing required field: '{field}'")

    # Rules section validation
    rules = manifest.get("rules", {})
    if not isinstance(rules, dict):
        errors.append("Section 'rules' must be a mapping")
    else:
        for subkey in REQUIRED_RULES_SUBKEYS:
            if subkey not in rules:
                errors.append(f"Section 'rules' missing required sub-key: '{subkey}'")
        # Validate required fields within each policy mapping
        for policy_key, required_fields in _REQUIRED_POLICY_FIELDS.items():
            policy = rules.get(policy_key)
            if isinstance(policy, dict):
                for field in required_fields:
                    if field not in policy:
                        errors.append(f"rules.{policy_key} missing required field: '{field}'")

    return errors
