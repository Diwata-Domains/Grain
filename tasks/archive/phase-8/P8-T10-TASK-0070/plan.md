# Plan: TASK-0070

## Approach

Add a new `forge verify` command group to cli_spec.md as a deferred surface (three subcommands: submit, status, ingest), update the §12 coverage summary, then write `v2_plan.md §11` as the authoritative Sentinel bridge contract documenting the command surface, the minimal result payload schema, and the verification gate stop condition rules. No implementation.

---

## Step 1 — Add `forge verify` to cli_spec.md §6.9

Insert a new command group section after §6.8 (`orchestrate`). The section must:
- follow the same structure as existing command groups (Purpose, Commands, Responsibilities, Must not, Recommended options, Deferral note)
- define three subcommands: `submit`, `status`, `ingest`
- mark the entire group as deferred per §5.1
- not alter any existing section

---

## Step 2 — Update cli_spec.md §12 Coverage Summary

Add the three `forge verify` subcommands to the command list. Add a note that they are defined but deferred (like the `forge orchestrate` note).

---

## Step 3 — Write v2_plan.md §11 — Sentinel Bridge Contract

Add §11 as a new section at the end of v2_plan.md. Contents:
- reference the `forge verify` command surface (§6.9 of cli_spec.md)
- define the minimal Sentinel result payload schema with required and optional fields
- define the verification gate stop condition rule for the runner
- note that no Sentinel implementation is required for this contract; FR-006 implements against it
- note that `forge verify` commands must register as not-implemented stubs until FR-006 is built

---

## Step 4 — Update backlog.md

Change P8-T10 status from `ready` → `in_progress`.

---

## Step 5 — Update current_task.md

Set to P8-T10-TASK-0070, in_progress.

---

## Verification

After all edits:
- cli_spec.md has a new §6.9 forge verify section
- cli_spec.md §12 includes forge verify submit/status/ingest with a deferral note
- v2_plan.md has a new §11 section
- No existing cli_spec.md sections were modified (only additions)
- backlog.md P8-T10 = in_progress
