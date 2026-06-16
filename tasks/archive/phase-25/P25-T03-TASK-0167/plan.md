# Plan: TASK-0167

## Approach

Keep the query/ORM slice objective-sensitive. The database adapter already selects the right class of files, so this task should only change their ordering when the packet objective clearly points at query, repository, or persistence behavior.

---

## Step 1 — Audit the current database selection behavior

Inspect the new database selection rules to see where query and repository surfaces can be introduced without weakening the schema/migration-first default.

---

## Step 2 — Add persistence-aware prioritization

Update the database ordering helper so objectives mentioning queries, repositories, ORM, or persistence lift query and data-access files ahead of model-adjacent context while still excluding unrelated application code.

---

## Step 3 — Verify with focused integration coverage

Add a persistence-oriented integration test that proves query and repository files are included and prioritized correctly, then record the verification slice in `results.md`.

---

## Verification

Run the focused adapter-profile, release-surface, and database integration tests. Confirm query and repository surfaces are included only when the objective points at persistence work and that unrelated application code still stays out of the bundle.
