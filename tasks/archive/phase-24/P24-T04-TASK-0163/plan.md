# Plan: TASK-0163

## Approach

Keep the Obsidian behavior narrow and additive. Reuse the existing adapter candidate selection and semantic reranking pipeline, then layer one small vault-aware prioritization pass that recognizes note targets and wiki-linked neighbors without creating a new graph subsystem.

---

## Step 1 — Audit current adapter selection flow

Inspect where `obsidian_adapter` enters context selection so the new behavior slots into the current candidate, priority, and reranking stages instead of duplicating logic.

---

## Step 2 — Add bounded wiki-link-aware prioritization

Implement one small helper that can anchor on the task objective or note links, prefer the target note first, then wiki-linked neighbors, and preserve that ordering through the final adapter-source list.

---

## Step 3 — Verify through integration coverage and packet closeout

Add focused Obsidian vault tests covering note ordering, wiki-link adjacency, and export behavior, then record the exact verification slice in `results.md` and prepare the review bundle.

---

## Verification

Run the focused adapter/profile and Obsidian integration tests. Confirm the target note ranks ahead of linked notes, linked notes rank ahead of unrelated markdown, and the literal frontmatter/wiki-link text still exports through the normal context flow.
