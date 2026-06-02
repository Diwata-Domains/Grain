# Grain — Landscape

**Status:** CANONICAL
**Produced:** 2026-06-02
**Source:** Diwata-Infra P17-T02

---

## Competitors

Tools that overlap with what Grain does — task management, workflow orchestration, or AI-assisted development.

| Tool | What it does | How Grain differs |
|---|---|---|
| **Linear** | Issue tracking, sprint management, roadmaps. Multi-user, cloud-backed. | Grain is file-backed and local-first. No cloud, no team infrastructure. Grain is a workflow kernel inside a single repo; Linear is a team coordination layer above many repos. |
| **GitHub Projects** | Kanban + backlog views on top of GitHub Issues. Tight GitHub coupling. | GitHub Projects is UI-only state — no structured packet system, no context assembly, no AI integration. Grain manages structured task packets that carry context into AI execution. |
| **Jira** | Enterprise issue tracker with advanced project management features. | Jira is a coordination surface for humans. Grain is a workflow kernel for AI-assisted execution. Grain packets carry execution context, not just ticket metadata. |
| **Notion (tasks)** | Flexible databases, embedded task views, wikis. Cloud, collaborative. | Notion is a human-readable content system. Grain is a machine-readable execution system. A Grain packet is a structured context unit; a Notion task is a formatted document. |
| **Claude Code / Cursor / Codex CLI** | AI coding assistants that execute code changes inside the editor or terminal. | These are *execution surfaces* — they take the current file context and act. Grain is the *workflow state manager* that tells these agents what to work on next, tracks task lifecycle, and gates review and close. They are complementary: Grain + Claude Code is the intended operating pattern. |
| **LangGraph** | Python framework for building stateful multi-agent workflows. Graph-based agent orchestration. | LangGraph is a runtime for agent graphs, not a developer workflow system. It orchestrates agents; Grain orchestrates work. Grain's state lives in files and is inspectable without running code. |
| **AutoGen / CrewAI** | Multi-agent conversation and task-delegation frameworks. | Agentic frameworks — designed for multi-agent coordination, not developer workflow management. Grain is not a framework; it's a workflow kernel with a stable CLI interface. |
| **Taskfile / GNU Make** | Declarative task runners — define targets and dependencies. | Make/Taskfile execute commands. Grain orchestrates structured knowledge work — it manages context, routes model selection, gates review, and tracks lifecycle. Grain's inspiration is the discrete-unit model; the implementation is different. |
| **Obsidian (vault + plugins)** | Local-first markdown knowledge base with plugin ecosystem. Dataview, tasks plugin, kanban plugin. | Obsidian is a knowledge tool for humans. Grain is a workflow tool for AI-assisted execution. Grain's docs-as-files philosophy was influenced by Obsidian, but Grain's state is machine-parseable by design. |
| **Docusaurus / GitBook** | Documentation sites — static rendering of markdown files. | Static publishing surfaces. Not workflow systems. Grain manages living working docs that change with project state. |

---

## Inspirations

Tools and ideas that shaped Grain's design — not competitors, but things that informed how it works.

| Source | What it is | What Grain drew from it |
|---|---|---|
| **git** | Distributed version control — commits as discrete, reviewable, named units of change. | The fundamental mental model: *discrete reviewed units*. A Grain task packet is the equivalent of a well-formed commit — bounded, reversible, documented. The task close/review model mirrors the commit+PR model. |
| **GNU Make** | Declarative build system — phased dependency graph, deterministic task execution. | The phase/task dependency model. Grain phases are like Make targets — ordered, closeable, with explicit dependencies. |
| **Obsidian** | Local-first markdown knowledge base with bidirectional links and plugin-generated views. | Files are truth. State lives in files, not a database. The user can always inspect, edit, and recover from any state without running Grain. |
| **Hermes Agent** (Nous Research) | Multi-channel, multi-context agent platform with subagent isolation and autonomous scheduling. | Multi-adapter context model: different domains (code, docs, data) need different context protocols. Hermes' channel isolation pattern informed how Grain adapters stay independent and composable. |
| **Scrapy / item pipelines** | Python web scraping framework with structured item pipeline. | The adapter capability surface pattern — a consistent protocol interface that adapters implement, with graceful degradation when capabilities are absent. |
| **LLM context windows** | The fundamental constraint in AI-assisted development: all relevant context must fit in one window. | Every Grain design decision is bounded by context window economics. Smaller, more precise context bundles — not broad file dumps — are a first-class design goal. |
| **Grain (cereal)** | The smallest unit of weight in historical measurement systems (the "kernel" of wheat). | The name itself. Grain is the smallest useful unit of structured workflow — the kernel beneath every other workflow system in the Diwata stack. |

---

## References

Relevant work worth reading when thinking about Grain's past, present, or future:

- **[Graphify (MIT)](https://github.com/graphify)** — tree-sitter + parallel subagent pattern for structural code analysis at scale. Referenced when designing Phase 10 (structural intelligence layer). 19-language tree-sitter support model influenced Grain's extraction coverage decisions.
- **[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)** — foundational paper on interleaving reasoning traces with action execution. Relevant to Grain's execute → review → close loop design philosophy.
- **[The Composable Build System (Bazel docs)](https://bazel.build/about)** — hermetic, reproducible, composable build targets. Relevant to the v0.4.0 "composable toolkit" direction: what would it mean for Grain phases and recipes to be truly composable?
- **[Conventional Commits](https://www.conventionalcommits.org/)** — the discrete, typed commit model. Influenced how Grain structures task descriptions and close artifacts.
- **[How to Write a Git Commit Message (Chris Beams)](https://cbea.ms/git-commit/)** — the commit-as-unit-of-communication framing. Grain's task packets follow similar discipline principles.
- **[Writing for Machines (Anthropic prompt engineering)](https://www.anthropic.com/research/prompting)** — writing prompts and context that AI agents act on reliably. Directly relevant to Grain's prompt library and context loading design.
