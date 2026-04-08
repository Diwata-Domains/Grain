
## `workflow_spec.md`

```md
# Workflow Specification

## 1. Purpose

This document defines the operational workflow used by `Forge`.

It governs:
- the Building Workflow
- the Build Loop
- workflow stages
- task packet lifecycle
- context loading behavior at the workflow level
- escalation and review points
- completion semantics

It controls decisions about:
- how work moves from idea to execution to review
- when task packets are created
- how tasks are prepared for external coding agents
- when model classes are used or escalated
- what conditions must be met before work is considered complete

It does not cover:
- whether the product should include a feature
- internal module/package boundaries
- exact source code structure
- generic product goals and non-goals

Those belong in product scope and architecture.

---

## 2. Workflow Model

`Forge` uses two linked operational structures:

1. **Building Workflow**
   - the higher-level sequence used to move the project forward

2. **Build Loop**
   - the repeated execution cycle used for each concrete task

The Building Workflow organizes project progress.
The Build Loop executes one scoped task packet at a time.

---

## 3. Building Workflow

The Building Workflow defines the major stages of structured AI-assisted development.

## 3.1 Stages

### Stage 1 — Canonical Design
Define or revise stable source-of-truth decisions.

Outputs may include:
- canonical docs
- approved canonical changes
- clarified project boundaries
- architecture decisions

Entry conditions:
- project initialization
- missing canonical guidance
- approved need for canonical revision

Exit conditions:
- enough canonical direction exists to plan execution work

### Stage 2 — Execution Planning
Translate canonical intent into implementable work.

Outputs may include:
- phase breakdown
- backlog items
- packet candidates
- priority sequencing
- identified dependencies

Entry conditions:
- canonical direction exists
- actionable work needs to be planned

Exit conditions:
- at least one coherent task can be packetized

### Stage 3 — Task Packet Generation
Convert one planned work item into a scoped execution packet.

Outputs must include:
- packet ID
- task definition
- task-local context
- execution plan
- deliverable definition

Entry conditions:
- one task is selected
- dependencies are known or accepted
- scope is bounded

Exit conditions:
- packet is ready for execution preparation

### Stage 4 — Task Execution
Use the packet to support implementation work through external tools or manual execution.

Outputs may include:
- code changes
- docs changes in allowed layers
- results notes
- blocked status
- proposed canonical patches

Entry conditions:
- packet exists
- required context is prepared
- execution path is chosen

Exit conditions:
- deliverable is produced or task is blocked

### Stage 5 — Review and Reconciliation
Check outputs against the packet and broader document authority.

Outputs may include:
- review findings
- corrections required
- task acceptance
- canonical change proposals
- handoff notes

Entry conditions:
- task execution produced a reviewable result

Exit conditions:
- task is accepted, reworked, blocked, or escalated

### Stage 6 — Closure and Handoff
Finalize the packet outcome.

Outputs may include:
- completed packet state
- final results record
- handoff artifact
- follow-up task creation
- backlog update

Entry conditions:
- review result is known

Exit conditions:
- task state is stable and inspectable

---

## 4. Build Loop

The Build Loop is the operational cycle applied to each individual task.

## 4.1 Loop Steps

1. **Select**
   - choose one concrete task

2. **Packetize**
   - create or update the task packet

3. **Prepare Context**
   - load the minimum valid document set

4. **Execute**
   - perform the scoped work using an external coding agent or manual implementation path

5. **Review**
   - verify the output against the packet and authority hierarchy

6. **Record**
   - write results, blockers, and proposals

7. **Close or Continue**
   - mark done, blocked, review-needed, or continue with a revised packet plan

## 4.2 Loop Rule
Do not run broad project execution without first converting work into a task packet.

## 4.3 Prompt Role In The Workflow

Prompt files are execution aids used to apply this workflow through external agents or model CLIs.

Prompts:
- help operationalize task execution, review, and closure
- may improve wording, ergonomics, or role guidance over time
- do not define canonical workflow truth on their own

If a prompt conflicts with canonical or runtime workflow rules, the higher-authority document wins and the prompt should be corrected through working-layer change tracking.

---

## 5. Task Packet Lifecycle

A task packet is the required workflow container for one coherent unit of work.

## 5.1 Packet Lifecycle States

Recommended v1 states:
- `draft`
- `ready`
- `in_progress`
- `blocked`
- `review`
- `done`

These states may be extended later, but v1 should stay minimal.

## 5.2 State Definitions

### `draft`
Packet exists but is incomplete or not yet ready to execute.

### `ready`
Packet scope, context plan, and deliverable are defined sufficiently for execution prep.

### `in_progress`
Execution has started.

### `blocked`
Progress cannot continue without clarification, dependency resolution, or approval.

### `review`
Execution result exists and needs validation.

### `done`
Completion requirements have been satisfied and recorded.

## 5.3 Allowed State Transitions

Allowed default transitions:

- `draft -> ready`
- `ready -> in_progress`
- `in_progress -> blocked`
- `in_progress -> review`
- `blocked -> draft`
- `blocked -> ready`
- `review -> in_progress`
- `review -> done`

Disallowed by default:
- `draft -> done`
- `ready -> done`
- `blocked -> done`

---

## 6. Required Task Packet Contents

A valid packet must contain:

- `task.md`
- `context.md`
- `plan.md`
- `deliverable_spec.md`

Optional during creation, required before closure if applicable:
- `results.md`
- `handoff.md`

### 6.1 File Responsibilities

#### `task.md`
Defines the task objective, scope, constraints, dependencies, and status.

#### `context.md`
Lists the exact materials required for execution.

#### `plan.md`
Defines the intended execution steps.

#### `deliverable_spec.md`
Defines what must exist for the task to count as complete.

#### `results.md`
Records what actually happened, files changed, blockers, and deviations.

#### `handoff.md`
Summarizes final state for reviewer, human operator, or next task owner.

---

## 7. Context Loading Rules

## 7.1 Default Rule
Load only the minimum document set required for one task.

## 7.2 Required Read Priority
For packet execution, the workflow should prefer:
1. packet-local files
2. relevant canonical docs
3. required working docs only if needed
4. runtime references only if needed for execution behavior

## 7.3 Prohibited Context Behavior
- do not load all canonical docs by default
- do not load all working docs by default
- do not pass broad repository state into execution unless task scope requires it
- do not rely on undocumented context

## 7.4 Context Sufficiency Rule
Context is sufficient when the selected docs allow the task to be executed and reviewed without requiring unrelated repo knowledge.

## 7.5 Default Context Tag Behavior
When context commands or services are invoked without explicit tags, canonical doc selection should default to the `running_tasks` tag set.

Rules:
- explicit tags replace the default tag set for that invocation
- working docs remain opt-in and are not included unless requested

## 7.6 Context Representation Rule
Different workflow surfaces may expose different structured context representations when their purposes differ.

For v1:
- `context build` may expose full selected document records for bundle inspection
- `context show` may expose inspection-oriented document summaries
- `context export` may expose source metadata only for external-tool usage

These differences are allowed only when they are explicitly documented in the CLI contract. Silent divergence is not allowed.

---

## 8. Model Class Usage in Workflow

The workflow supports three model classes:

- `open_model`
- `frontier_model`
- `reviewer_model`

## 8.1 Default Usage

### `open_model`
Use for:
- packet drafting
- basic task shaping
- low-risk formatting and transformation work
- routine execution preparation

### `frontier_model`
Use for:
- ambiguous design reasoning
- complex planning
- difficult tradeoff analysis
- proposed canonical-impacting work

### `reviewer_model`
Use for:
- acceptance review
- consistency checks
- critique of outputs
- validating whether deliverables match packet requirements

## 8.2 Escalation Rules

Escalate to `frontier_model` when:
- packet scope depends on ambiguous design decisions
- context conflict cannot be resolved mechanically
- multiple valid implementation paths exist
- failure risk is high

Escalate to `reviewer_model` when:
- execution output is ready for acceptance
- structural validation is complete but quality must be assessed
- a canonical proposal is attached

---

## 9. Workflow Authority Handling

## 9.1 Authority Rule
Execution must follow the document authority hierarchy defined by the project.

## 9.2 Canonical Conflict Rule
If execution reveals that:
- canonical docs are incomplete, or
- lower-level docs conflict with canonical docs,

then the task may continue only if:
- the current execution can remain within existing authority, or
- the conflict is explicitly recorded and deferred

Direct canonical edits are not part of ordinary packet execution.

## 9.3 Proposal Rule
Canonical-impacting discoveries must be recorded as proposals, not silently merged into canonical truth.

---

## 10. Completion Requirements

A task packet may be marked `done` only if all are true:

1. the deliverable in `deliverable_spec.md` exists
2. execution output matches packet scope
3. required files are present and updated
4. `results.md` records actual outcome
5. review findings are resolved or explicitly accepted
6. unresolved follow-up work is captured for later action
7. no hidden canonical change was performed

---

## 11. Failure and Recovery Behavior

## 11.1 Blocked Tasks
A task must move to `blocked` if:
- required context is missing
- dependencies are unresolved
- canonical ambiguity prevents safe execution
- external tool execution cannot proceed meaningfully

## 11.2 Rework from Review
A task in `review` may return to `in_progress` if:
- deliverable is incomplete
- outputs violate packet scope
- output conflicts with authority rules
- missing results or handoff artifacts prevent closure

## 11.3 Split Rule
If a packet grows beyond one coherent unit of work, it should be split into multiple packets rather than broadened indefinitely.

---

## 12. Practical v1 Workflow Rules

1. one packet should target one coherent change
2. execution should be bounded and inspectable
3. packet creation must be lightweight enough for frequent use
4. validation should happen before closure, not only after failure
5. human approval is required for canonical changes
6. the toolkit should assist external coding agents, not replace them
7. the workflow must remain usable without complex automation

---

## 13. Adapter Interaction with the Workflow

Domain adapters may inform task execution without altering the workflow itself.

### 13.1 What Adapters May Do

An active adapter may:
- bias context selection toward domain-relevant files and patterns
- surface domain-specific validation hints in context output
- provide review focus guidance (e.g. UI regression, exit code semantics, VPS rollback risk)
- suggest model-routing preference for domain-typical task types
- supply deliverable pattern guidance for tasks in its domain

### 13.2 What Adapters Must Not Do

An adapter must not:
- alter lifecycle states (`draft`, `ready`, `in_progress`, `blocked`, `review`, `done`) or their semantics
- change closure requirements
- bypass or defer the Review/Gate stage
- override canonical authority rules
- redefine what counts as a valid packet or a complete task

### 13.3 Adapter-Neutral Behavior

When no adapter is declared for a task packet, Forge operates adapter-neutrally. No domain hints are applied. No context biasing occurs. All workflow rules remain identical.

Adapter presence is always explicit — declared in packet metadata. Forge never infers an adapter from file patterns or project type alone.

### 13.4 Workflow Invariance Rule

The workflow loop (select → packetize → prepare context → execute → review → record → close) is the same for every domain. Only the hints, patterns, and validation focus change when an adapter is active. A domain that requires changing the loop itself is not a candidate for adapter-based extension.

---

## 14. Decision Boundaries

### 14.1 Decisions This Document Controls
- workflow stages
- build loop sequence
- packet lifecycle states and transitions
- context loading behavior at workflow level
- model class usage by stage
- closure requirements
- adapter interaction boundaries with the workflow

### 14.2 Decisions This Document Does Not Control
- product feature scope
- system component boundaries
- exact module structure
- specific CLI syntax
- generic project architecture choices

Those must conform to this workflow but are controlled elsewhere.
