# Inbox

Captured feature-requests and quick-edits awaiting triage. `grain capture promote <id> --phase N`
turns one into a backlog draft entry + a task packet. Pre-backlog and unphased — not a lifecycle.

| ID | Status | Kind | Title | Note | Captured | Task |
|----|--------|------|-------|------|----------|------|
| CAP-0001 | new | chore | Make 'grain workflow reconcile' automatic so backlog.md never silently drifts from packet statuses: run drift-detect in the 'workflow next' preflight (warn, optionally auto-fix on task close), and fix the reconcile archive blind-spot (check tasks/archive/ before flagging missing_packet). Motivated by P33 packets reading done while backlog said ready. |  | 2026-07-23 |  |
