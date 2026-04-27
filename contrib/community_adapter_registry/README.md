# Community Adapter Registry Scaffold

This directory mirrors the minimum reviewed-registry shape expected by Phase 19.

## Purpose

Community adapters live outside the core Grain repo, but they must remain explicit, reviewable, and compatible with the same adapter contract as official adapters. This scaffold shows the minimum package and review artifacts a reviewed community adapter submission should include.

## Submission Layout

One reviewed community adapter submission should include:

- `adapter_package.yaml` — package metadata consumed by validation and install flows
- `adapter_profile.md` — one declarative adapter profile payload
- `review_metadata.yaml` — registry-maintainer review metadata for the submission

Recommended reviewed-registry layout:

```text
community_adapter_registry/
  submissions/
    <package_id>/
      adapter_package.yaml
      adapter_profile.md
      review_metadata.yaml
```

## Trust Boundaries

- Community adapters are reviewed proposals, not Official adapters.
- Community adapters must pass package validation before local install.
- Local install remains explicit: use a package directory or a local reviewed-registry checkout plus handle.
- Promotion from Community to Official is a separate maintainer decision and is not encoded in these scaffold files.

## Templates

Template files live under `templates/`:

- `adapter_package.yaml`
- `adapter_profile.md`
- `review_metadata.yaml`

Use these as the starting point for new submissions in the dedicated reviewed community registry repository.
