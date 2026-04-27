# Community Adapter Review Checklist

Use this checklist when reviewing a community adapter submission in the dedicated reviewed registry repo.

- Confirm `adapter_package.yaml` is present and machine-parseable.
- Confirm `adapter_profile.md` contains exactly one adapter profile.
- Confirm `adapter_id` in package metadata matches the adapter profile payload.
- Confirm the adapter remains declarative and repo-visible.
- Confirm the profile does not shadow an existing official adapter ID.
- Confirm the adapter domain hints are specific enough to be useful during context selection or review.
- Confirm the submission is still Community status and does not claim automatic promotion to Official.
