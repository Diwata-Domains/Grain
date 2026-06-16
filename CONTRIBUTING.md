# Contributing to Grain

Thanks for your interest in Grain.

---

## What contributions are accepted

### Community adapters

The primary contribution path is **community adapters** — adapter profiles that tune Grain's context selection and review focus for a specific domain, framework, or toolchain.

Adapter contributions are submitted as pull requests to this repo under `contrib/community_adapter_registry/`. CI automatically validates the adapter schema on every PR.

**To contribute a community adapter:**

1. Read the authoring guide: `docs/working/community_adapter_authoring.md`
2. Fork this repo
3. Add your adapter under `contrib/community_adapter_registry/<your-adapter-name>/`
4. Open a pull request — CI will validate the schema automatically
5. A maintainer will review and merge once the adapter passes validation and review

Adapter PRs are the only code contributions currently accepted.

### Bug reports

Open a bug report using the [bug report template](https://github.com/Diwata-Labs/Grain/issues/new/choose). Include the `grain-kit` version, Python version, OS, and exact steps to reproduce.

### Feature requests

Open a feature request using the [feature request template](https://github.com/Diwata-Labs/Grain/issues/new/choose). Describe the workflow problem you're trying to solve — that context is more useful than a description of the solution alone.

---

## What is not accepted

Grain does not currently accept external code contributions outside of community adapters. This is an intentional IP policy during the early commercial phase — clean ownership matters for the dual-licensing model.

This includes:
- Core CLI changes
- New built-in adapters
- Documentation edits
- Test additions

If you have a suggestion for any of these, open a feature request or bug report instead. The maintainer will consider it for a future release.

---

## Community adapter tiers

| Tier | Description |
|---|---|
| **Official** | Shipped with Grain; maintained by Diwata Labs |
| **Verified** | Reviewed and approved by maintainer; listed in the registry |
| **Community** | PR-based; schema-validated by CI; not individually reviewed beyond schema |

Community adapters are schema-validated but not functionally tested by the maintainer. Use them at your own judgment.

---

## Code of conduct

Be direct and constructive. Issues and PRs are for problem-solving, not debate. The maintainer reserves the right to close issues or PRs that are off-topic or unconstructive without explanation.
