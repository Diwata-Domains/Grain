# Community Adapter Authoring Guide

This guide explains how to prepare a reviewed community adapter submission for the dedicated community registry repository described in Phase 19.

## Package Contents

Each submission should include exactly these three files:

- `adapter_package.yaml`
- `adapter_profile.md`
- `review_metadata.yaml`

Use the templates in `contrib/community_adapter_registry/templates/` as the starting point.

## Validation Expectations

Before a maintainer accepts a submission, the package should satisfy the same checks enforced by the Phase 19 package validator:

- `adapter_package.yaml` must exist and parse as YAML
- required metadata fields must be present: `package_id`, `adapter_id`, `version`
- `adapter_profile.md` must exist and contain exactly one adapter profile
- the adapter profile must satisfy the current adapter profile parser contract
- `adapter_id` in metadata must match the adapter profile payload

## Review Boundaries

Community adapters are reviewed proposals. Reviewers should confirm:

- the adapter remains declarative and repo-visible
- the profile hints are specific enough to be useful
- the adapter does not shadow an existing official adapter ID
- the review metadata reflects the current maintainer decision

## Install Expectations

Phase 19 install remains explicit and local-only:

- install from an explicit package directory, or
- install from a local reviewed-registry checkout plus handle

There is no remote fetch or hidden registry state in the current install flow.

## Promotion Boundary

Community submission review is not the same thing as promotion to Official status.

- passing validation does not make an adapter Official
- maintainer approval in the reviewed registry does not make an adapter Official
- promotion from Community to Official remains a separate maintainer decision
