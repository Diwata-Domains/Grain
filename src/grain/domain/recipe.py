# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Domain models for the recipe step-runner definition layer.

Parses and validates a ``recipe.yaml`` of ``apiVersion: grain.recipe/v2`` into
typed dataclasses (:class:`RecipeDefinition` / :class:`RecipeStep` /
:class:`RecipeParam`). This is the *definition* model only: no run state, no
execution, no ``{{param}}`` rendering. The recipe engine is parallel to the SDLC
loop and does not touch packet lifecycle code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

RECIPE_API_VERSION = "grain.recipe/v2"  # the only accepted apiVersion

VALID_GATES: frozenset[str] = frozenset({"none", "review"})
VALID_CATEGORIES: frozenset[str] = frozenset(
    {"research", "docs", "data", "ops", "content", "code", "custom"}
)
VALID_SUPERVISION: frozenset[str] = frozenset(
    {"supervised", "gated", "autonomous"}
)

# Strict-schema allow-sets. Keys outside these are rejected.
_ALLOWED_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "apiVersion",
        "id",
        "name",
        "description",
        "category",
        "workspace_kind",  # accepted-and-ignored in MVP
        "supervision",
        "params",
        "steps",
        "final",
    }
)
_ALLOWED_STEP_KEYS: frozenset[str] = frozenset(
    {
        "id",
        "name",
        "prompt",
        "inputs",
        "output",
        "gate",
        "adapter",  # accepted-and-ignored
        "model",  # accepted-and-ignored
    }
)
_ALLOWED_PARAM_KEYS: frozenset[str] = frozenset({"id", "label", "required", "type"})

# The literal an `inputs` entry may use to reference the run params.
_PARAMS_INPUT = "params"


class RecipeSchemaError(ValueError):
    """Raised when a recipe.yaml violates the grain.recipe/v2 schema."""


def is_safe_output_name(name: str) -> bool:
    """True iff ``name`` is a safe RELATIVE artifact filename for a run dir.

    A step ``output`` is written under ``docs/recipes/runs/<run-id>/``; it must
    therefore be a relative path that cannot escape that directory. This rejects
    absolute paths, Windows drive/UNC and backslash separators, and any
    parent-traversal (``..``) component. Path-traversal hardening (F1).
    """
    if not isinstance(name, str) or not name.strip():
        return False
    if "\\" in name:  # backslash separators / Windows-style escapes
        return False
    pure = PurePosixPath(name)
    if pure.is_absolute():
        return False
    parts = pure.parts
    if not parts:  # e.g. "." resolves to no concrete file
        return False
    if any(part == ".." for part in parts):
        return False
    return True


def ensure_output_within(base: Path, output: str, *, label: str = "step") -> Path:
    """Defensive join-site guard for a step ``output`` under ``base`` (F1).

    Validates ``output`` is a safe relative name AND that the resolved
    ``base / output`` stays strictly inside ``base`` (catches symlink/escape
    cases the lexical check alone would miss). Returns the joined (un-resolved)
    path for the caller to use. Raises :class:`RecipeSchemaError` on any escape.
    """
    if not is_safe_output_name(output):
        raise RecipeSchemaError(
            f"{label} output {output!r} is not a safe relative filename "
            f"(no absolute paths, no '..' traversal, no '\\' separators)"
        )
    joined = base / output
    base_resolved = base.resolve()
    candidate = joined.resolve()
    if base_resolved != candidate and base_resolved not in candidate.parents:
        raise RecipeSchemaError(
            f"{label} output {output!r} escapes the run directory {str(base)!r}"
        )
    return joined


@dataclass
class RecipeParam:
    """A single declared recipe parameter."""

    id: str
    required: bool = False
    label: str = ""
    type: str = "string"  # MVP: not enumerated/validated beyond non-empty

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise RecipeSchemaError("recipe param requires a non-empty 'id'")
        if not isinstance(self.required, bool):
            raise RecipeSchemaError(
                f"recipe param {self.id!r} 'required' must be a boolean"
            )
        if not isinstance(self.type, str) or not self.type.strip():
            raise RecipeSchemaError(
                f"recipe param {self.id!r} 'type' must be a non-empty string"
            )


@dataclass
class RecipeStep:
    """A single ordered step in a recipe."""

    id: str
    prompt: str  # path (e.g. "steps/intake.md") or "inline:..." string
    output: str  # artifact filename this step must produce
    inputs: list[str] = field(default_factory=list)  # "params" or earlier step ids
    name: str = ""
    gate: str = "none"  # one of VALID_GATES

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise RecipeSchemaError("recipe step requires a non-empty 'id'")
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise RecipeSchemaError(
                f"recipe step {self.id!r} requires a non-empty 'prompt'"
            )
        if not isinstance(self.output, str) or not self.output.strip():
            raise RecipeSchemaError(
                f"recipe step {self.id!r} requires a non-empty 'output'"
            )
        if not is_safe_output_name(self.output):
            raise RecipeSchemaError(
                f"recipe step {self.id!r} has unsafe output {self.output!r}; "
                f"output must be a relative filename inside the run dir "
                f"(no absolute paths, no '..' traversal, no '\\' separators)"
            )
        if not isinstance(self.inputs, list) or not all(
            isinstance(item, str) for item in self.inputs
        ):
            raise RecipeSchemaError(
                f"recipe step {self.id!r} 'inputs' must be a list of strings"
            )
        if self.gate not in VALID_GATES:
            raise RecipeSchemaError(
                f"recipe step {self.id!r} has invalid gate {self.gate!r}; "
                f"expected one of {sorted(VALID_GATES)}"
            )


@dataclass
class RecipeDefinition:
    """A parsed and validated grain.recipe/v2 recipe definition."""

    id: str
    name: str
    final: str  # must equal some step.output
    params: list[RecipeParam] = field(default_factory=list)
    steps: list[RecipeStep] = field(default_factory=list)
    supervision: str = "gated"  # one of VALID_SUPERVISION; default per spec §2.1
    description: str = ""  # retained v1 metadata, optional
    category: str = ""  # if set, must be in VALID_CATEGORIES

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise RecipeSchemaError("recipe requires a non-empty 'id'")
        if not isinstance(self.name, str) or not self.name.strip():
            raise RecipeSchemaError(f"recipe {self.id!r} requires a non-empty 'name'")
        if not isinstance(self.final, str) or not self.final.strip():
            raise RecipeSchemaError(
                f"recipe {self.id!r} requires a non-empty 'final'"
            )
        if not self.steps:
            raise RecipeSchemaError(
                f"recipe {self.id!r} requires at least one step"
            )

        if self.supervision not in VALID_SUPERVISION:
            raise RecipeSchemaError(
                f"recipe {self.id!r} has invalid supervision {self.supervision!r}; "
                f"expected one of {sorted(VALID_SUPERVISION)}"
            )

        if self.category and self.category not in VALID_CATEGORIES:
            raise RecipeSchemaError(
                f"recipe {self.id!r} has invalid category {self.category!r}; "
                f"expected one of {sorted(VALID_CATEGORIES)}"
            )

        # Unique step ids.
        seen: set[str] = set()
        for step in self.steps:
            if step.id in seen:
                raise RecipeSchemaError(
                    f"recipe {self.id!r} has duplicate step id {step.id!r}"
                )
            seen.add(step.id)

        # Unique output filenames (two steps must never write the same artifact,
        # which would let one step clobber another's output). Uniqueness like
        # step ids (F3).
        seen_outputs: set[str] = set()
        for step in self.steps:
            if step.output in seen_outputs:
                raise RecipeSchemaError(
                    f"recipe {self.id!r} has duplicate step output "
                    f"{step.output!r}; each step must declare a unique output"
                )
            seen_outputs.add(step.output)

        # Inputs reference integrity: each entry is "params" or the id of a
        # step appearing EARLIER in the list (no forward/self/unknown refs).
        earlier: set[str] = set()
        for step in self.steps:
            for ref in step.inputs:
                if ref == _PARAMS_INPUT:
                    continue
                if ref not in earlier:
                    raise RecipeSchemaError(
                        f"recipe {self.id!r} step {step.id!r} references unknown or "
                        f"non-earlier input {ref!r}; inputs must be 'params' or the id "
                        f"of an earlier step"
                    )
            earlier.add(step.id)

        # final must resolve to some step output.
        outputs = {step.output for step in self.steps}
        if self.final not in outputs:
            raise RecipeSchemaError(
                f"recipe {self.id!r} final {self.final!r} does not match any step output"
            )


def _reject_unknown_keys(
    data: dict, allowed: frozenset[str], location: str
) -> None:
    """Raise RecipeSchemaError naming any key in ``data`` outside ``allowed``."""
    unknown = [key for key in data if key not in allowed]
    if unknown:
        raise RecipeSchemaError(
            f"unknown key {unknown[0]!r} in {location}; "
            f"allowed keys: {sorted(allowed)}"
        )


def _parse_param(raw: dict, index: int) -> RecipeParam:
    if not isinstance(raw, dict):
        raise RecipeSchemaError(
            f"recipe param at index {index} must be a mapping"
        )
    _reject_unknown_keys(raw, _ALLOWED_PARAM_KEYS, f"param at index {index}")
    if "id" not in raw:
        raise RecipeSchemaError(f"recipe param at index {index} requires 'id'")
    return RecipeParam(
        id=raw["id"],
        required=raw.get("required", False),
        label=raw.get("label", ""),
        type=raw.get("type", "string"),
    )


def _parse_step(raw: dict, index: int) -> RecipeStep:
    if not isinstance(raw, dict):
        raise RecipeSchemaError(f"recipe step at index {index} must be a mapping")
    _reject_unknown_keys(raw, _ALLOWED_STEP_KEYS, f"step at index {index}")
    for required_key in ("id", "prompt", "output"):
        if required_key not in raw:
            raise RecipeSchemaError(
                f"recipe step at index {index} requires {required_key!r}"
            )
    return RecipeStep(
        id=raw["id"],
        prompt=raw["prompt"],
        output=raw["output"],
        inputs=list(raw.get("inputs", [])),
        name=raw.get("name", ""),
        gate=raw.get("gate", "none"),
    )


def parse_recipe(data: dict) -> RecipeDefinition:
    """Validate a parsed-YAML dict against grain.recipe/v2 and build the model.

    Raises:
        RecipeSchemaError: on any schema violation.
    """
    if not isinstance(data, dict):
        raise RecipeSchemaError("recipe definition must be a mapping")

    # 1. apiVersion gate — exact-match only, no major-only matching.
    if "apiVersion" not in data:
        raise RecipeSchemaError(
            f"recipe is missing 'apiVersion'; expected exactly {RECIPE_API_VERSION!r}"
        )
    api_version = data["apiVersion"]
    if api_version != RECIPE_API_VERSION:
        raise RecipeSchemaError(
            f"unsupported recipe apiVersion {api_version!r}; "
            f"expected exactly {RECIPE_API_VERSION!r}"
        )

    # 2. Strict unknown-key rejection (top level).
    _reject_unknown_keys(data, _ALLOWED_TOP_LEVEL_KEYS, "recipe top level")

    # 3. Required top-level keys.
    for required_key in ("id", "name", "final"):
        if required_key not in data:
            raise RecipeSchemaError(f"recipe is missing required key {required_key!r}")
    raw_steps = data.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise RecipeSchemaError("recipe requires a non-empty 'steps' list")

    raw_params = data.get("params", [])
    if not isinstance(raw_params, list):
        raise RecipeSchemaError("recipe 'params' must be a list")

    params = [_parse_param(raw, i) for i, raw in enumerate(raw_params)]
    steps = [_parse_step(raw, i) for i, raw in enumerate(raw_steps)]

    return RecipeDefinition(
        id=data["id"],
        name=data["name"],
        final=data["final"],
        params=params,
        steps=steps,
        supervision=data.get("supervision", "gated"),
        description=data.get("description", ""),
        category=data.get("category", ""),
    )


def load_recipe(path: str | Path) -> RecipeDefinition:
    """Read a recipe.yaml file, YAML-parse it, and return parse_recipe(data).

    Raises:
        RecipeSchemaError: on unreadable/invalid files or schema violations.
    """
    recipe_path = Path(path)
    try:
        text = recipe_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RecipeSchemaError(
            f"could not read recipe file {str(recipe_path)!r}: {exc}"
        ) from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise RecipeSchemaError(
            f"recipe file {str(recipe_path)!r} is not valid YAML: {exc}"
        ) from exc

    if data is None:
        raise RecipeSchemaError(f"recipe file {str(recipe_path)!r} is empty")

    return parse_recipe(data)
