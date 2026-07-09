# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Shared scaffold constants consumed by both init and onboard services.

`init_service` (fresh-project init) and `onboard_service` (additive onboarding of an
existing repo) legitimately differ in the *bodies* they write — init copies bundled
templates, onboard writes DRAFT stubs into canonical/working docs. But the directory
layout and the runtime/prompt seed maps are genuinely shared, and keeping a single
definition here prevents the recurring init/onboard desync (a missing entry in one
list but not the other).

This module is domain-only: it holds plain string literals and must never import from
`grain.services`, to keep the domain layer free of a dependency cycle.
"""

from __future__ import annotations

# Directories required by architecture.md Section 5. Both scaffolders create these.
REQUIRED_DIRS: list[str] = [
    "docs/canonical",
    "docs/working",
    "docs/working/proposals",
    "docs/runtime",
    "tasks",
    "templates/docs",
    "templates/tasks",
    "templates/prompts",
    "src",
    "tests",
]

# Bundled runtime docs + task templates, seeded verbatim by BOTH scaffolders.
# Keys: destination path relative to the project root.
# Values: source path relative to the bundled data root.
RUNTIME_SEED_SOURCES: dict[str, str] = {
    "docs/runtime/PROJECT_RULES.md": "runtime/PROJECT_RULES.md",
    "docs/runtime/docs_manifest.yaml": "runtime/docs_manifest.yaml",
    "docs/runtime/docs_index.md": "runtime/docs_index.md",
    "docs/runtime/context_loading.md": "runtime/context_loading.md",
    "docs/runtime/agent_profiles.md": "runtime/agent_profiles.md",
    "docs/runtime/adapter_profiles.md": "runtime/adapter_profiles.md",
    "docs/runtime/workflow_loop.yaml": "runtime/workflow_loop.yaml",
    "templates/tasks/task.md": "templates/tasks/task.md",
    "templates/tasks/context.md": "templates/tasks/context.md",
    "templates/tasks/plan.md": "templates/tasks/plan.md",
    "templates/tasks/deliverable_spec.md": "templates/tasks/deliverable_spec.md",
    "templates/tasks/results.md": "templates/tasks/results.md",
    "templates/tasks/handoff.md": "templates/tasks/handoff.md",
    "templates/tasks/task_packet.md": "templates/tasks/task_packet.md",
}

# Bundled workflow prompts, seeded verbatim by BOTH scaffolders.
# Keys: destination path relative to the project root.
# Values: source path relative to the bundled data root.
PROMPT_SEED_SOURCES: dict[str, str] = {
    "prompts/workflow.resume.md": "prompts/workflow.resume.md",
    "prompts/workflow.onboard.new.md": "prompts/workflow.onboard.new.md",
    "prompts/workflow.onboard.existing.md": "prompts/workflow.onboard.existing.md",
    "prompts/workflow.init.md": "prompts/workflow.init.md",
    "prompts/task.plan.next.md": "prompts/task.plan.next.md",
    "prompts/task.execute.md": "prompts/task.execute.md",
    "prompts/task.review.md": "prompts/task.review.md",
    "prompts/task.close.md": "prompts/task.close.md",
    "prompts/phase.plan.next.md": "prompts/phase.plan.next.md",
    "prompts/phase.review.md": "prompts/phase.review.md",
    "prompts/phase.review_and_close.md": "prompts/phase.review_and_close.md",
    "prompts/tasks.plan.next.md": "prompts/tasks.plan.next.md",
    "prompts/tasks.next_and_implement.md": "prompts/tasks.next_and_implement.md",
    "prompts/tasks.review.md": "prompts/tasks.review.md",
    "prompts/tasks.close.md": "prompts/tasks.close.md",
}
