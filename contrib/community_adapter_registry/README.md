# Community Adapter Registry

Community adapters extend Grain with context profiles for specific domains, frameworks, or toolchains. They follow the same adapter contract as official adapters and are distributed separately from the core package.

## Submitting an adapter

Each adapter submission lives in its own directory under `submissions/`:

```text
community_adapter_registry/
  submissions/
    <package_id>/
      adapter_package.yaml   — package metadata (id, name, description, version, author)
      adapter_profile.md     — the adapter profile payload
      review_metadata.yaml   — maintainer review record (filled in during review)
```

Templates for each file are in `templates/`.

To submit:
1. Copy the templates into `submissions/<your-package-id>/`
2. Fill in `adapter_package.yaml` and `adapter_profile.md`
3. Leave `review_metadata.yaml` as-is — the maintainer fills this in
4. Open a pull request — CI validates the schema automatically

## Trust model

| Tier | Meaning |
|---|---|
| **Official** | Shipped with Grain; maintained by Diwata Labs |
| **Verified** | Reviewed and approved by maintainer |
| **Community** | Schema-validated by CI; not individually reviewed beyond schema |

Community adapters are schema-validated but not functionally tested by the maintainer. Install them with `grain adapter install` and evaluate them for your use case.

## Local install

```bash
grain adapter install --source path/to/adapter_package.yaml
```
