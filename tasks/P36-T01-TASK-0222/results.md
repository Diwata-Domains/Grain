# Results: TASK-0222

## Packet State
- **Current Task Status:** review
- **Review Readiness:** ready — release is live and externally verifiable
- **Recommended Next Status:** done

## Files Changed
- `products/grain/pyproject.toml` — `[project.urls]` fixed from `Diwata-Labs/Grain` to `Diwata-Domains/Grain` (shipped into immutable PyPI metadata)
- `products/grain/tasks/P36-T01-TASK-0222/` — this packet
- `products/grain/docs/working/{backlog,current_task}.md` — status bookkeeping
- Tag `grain-v0.5.0` moved from `ff8d06c` to merge commit `ba010dd` (never on remote, safe) and pushed

## Summary
Shipped grain-kit 0.5.0 to PyPI (2026-07-07). Pre-flight per audit §3: version
coherence verified (pyproject 0.5.0, tag, CHANGELOG 2026-06-28, `grain doctor` 4/4 —
the audit's 0.1.0 mismatch was already fixed by `ff8d06c`); `[project.urls]` fixed and
confirmed inside the built wheel METADATA; `uv build` + `twine check` PASSED on sdist
and wheel; `PYPI_TOKEN_GRAIN`/`SYNC_TOKEN` present. Fix landed via PR #5
(PR #4 closed — branch name had dots, violating trace's `prefix/scope-slug`; renamed to
`chore/grain-release-preflight`). Tag push fired `release-python.yml` run 28845125357:
all steps succeeded — test, build, PyPI publish, mirror sync, GitHub Release on
`Diwata-Domains/Grain`. PyPI now lists 0.5.0 as latest.

Deviations: none of scope. Audit's stale `products/grain/uv.lock` concern (P36-T05)
confirmed inert for the release — resolution uses the root workspace lock (assay's
releases shipped the same way); left for P36-T05.

## Test Results
1632 passed, 1 xfailed locally (41s); release workflow's own pytest gate passed in CI.

## Efficiency
### Execute
- **Prompt Runs:** 1 session (shared with unrelated ops work)
- **Conversation Restarts:** 0
- **Files Read (est.):** ~15
- **Tokens:** n/a
- **Notes:** One avoidable round-trip: release branch name contained dots (`0.5.0`), rejected by trace lint-branch in CI; cost one closed PR (#4) and a rename.

### Review
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** None

### Close
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** None

## Review Notes
- Verify externally: `pip index versions grain-kit` (or PyPI page) shows 0.5.0 latest; sidebar links point at Diwata-Domains.
- The tag now points at merge commit `ba010dd`, not the original release commit `ff8d06c` — contents differ only by docs/test-fix/urls commits.

## User Review
- **State:** pending
- **Summary:** [reviewer fills]
- **Resolution Mode:** [revise_current_task / replan_current_task / create_followup_task / close_task]

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- Trace lint-branch: consider allowing dots in slugs (version strings are natural in release branches) — or document the constraint in CONTRIBUTING.

### Follow-Ups To Log
- P36-T02 (heavy deps → extras) targets the next release; P36-T05 (orphan uv.lock) remains hygiene.

### Residual Risks
- None

## Verification Review
- **State:** passed
- **Summary:** PyPI index lists grain-kit 0.5.0 as latest; release run 28845125357 all-green.

### Findings
- None

## Closure Decision
- **Decision:** pending
- **Reason:** awaiting operator review

### Closure Blockers
- None

## Deliverable Checklist
- [x] grain-kit 0.5.0 published to PyPI via the tag-push pipeline
- [x] PyPI metadata carries Diwata-Domains URLs
- [x] All tests passing
