# Plan: TASK-0044

## Approach

Add narrowly scoped tests that exercise the existing context and routing layers directly. Use minimal repository fixtures to verify bundle assembly, export output, and routing decisions without changing implementation behavior.

---

## Step 1 — Add context bundle coverage

Create tests that confirm packet-local files are discovered, canonical docs are selected by context tags, working docs stay excluded by default, and optional working-doc inclusion is honored.

---

## Step 2 — Add export coverage

Create tests that verify markdown export rendering and write-path behavior, including source metadata and embedded content for selected docs.

---

## Step 3 — Add routing coverage

Create tests that verify stage/role routing decisions and escalation target selection against the runtime model profile contract.

---

## Verification

Run the new tests plus the focused model/context suites that already exist, then run the full pytest suite to confirm there are no regressions.
