# Context Loading

## Principle
Load the smallest valid set of documents needed for one task.

## Default Read Order
1. PROJECT_RULES.md
2. relevant task packet
3. relevant canonical docs
4. relevant working docs only if needed

## For Task Packet Generation
Read:
- PROJECT_RULES.md
- docs_index.md
- docs_manifest.yaml
- backlog.md
- current_focus.md
- implementation_plan.md
- only relevant canonical docs
- task_packet template

## For Implementation
Read:
- PROJECT_RULES.md
- task packet
- only the canonical docs referenced by the packet
- working docs only if needed

## For Review
Read:
- PROJECT_RULES.md
- task packet
- implementation output
- referenced canonical docs
- working docs only if needed for sequencing or drift checks

## Avoid By Default
- full repo context
- unrelated historical docs
- future-phase docs
- unrelated prompts