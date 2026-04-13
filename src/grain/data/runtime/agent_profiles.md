# Agent Profiles

## Purpose
Defines model classes and routing behavior for Grain.

## Model Classes

### open_model
Use for:
- boilerplate
- formatting
- narrow implementation
- simple packet drafting

Avoid for:
- architecture ambiguity
- final validation
- major design tradeoffs

### frontier_model
Use for:
- architecture
- workflow logic
- ambiguous tasks
- cross-file coordination
- difficult debugging

### reviewer_model
Use for:
- review
- consistency checks
- acceptance validation
- patch critique

## Escalation Rules
Escalate from open_model to frontier_model when:
- ambiguity blocks progress
- design tradeoffs appear
- output repeatedly fails quality checks
- task affects canonical design indirectly

Use reviewer_model when:
- task is marked complete
- CLI contracts changed
- packet proposes canonical changes
- phase gate or release gate is reached

## Current Preferred Mapping
- open_model: Claude or Codex
- frontier_model: Claude or Codex
- reviewer_model: Claude or Codex

## Prompt Metadata Consumption
- Prompt metadata is advisory runtime guidance in the current repo state.
- Humans or external agents may use `recommended_model_class` and `escalation_model_class` when choosing how to run a prompt.
- Until `grain model select` and related routing commands are implemented, prompt metadata should not be treated as an enforced contract.
- When those commands exist, they may consume prompt metadata as an input to routing, but runtime routing rules still override prompt wording if they conflict.

## Principle
Routing is based on role and capability, not vendor name.
