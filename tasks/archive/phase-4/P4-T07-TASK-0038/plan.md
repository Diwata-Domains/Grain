# Plan: TASK-0038

## Steps

1. Create export adapter that renders/writes a single assembled markdown file with source header and sourced content sections.
2. Implement `forge context export` using existing bundle assembly and optional output path.
3. Add JSON metadata output path for `--format json` without writing markdown files.
4. Add command tests for default markdown export, custom output path, JSON metadata-only behavior, include-working behavior, and unknown task handling.
5. Run targeted tests and full suite.
