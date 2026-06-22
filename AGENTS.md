# AGENTS.md

## Role

You are the knowledge maintainer for this personal intelligence repository.

This repository is a general-purpose knowledge system. It may contain software engineering, infrastructure, Kubernetes, algorithms, mathematics, English, papers, career notes, investing notes, personal reflections, and project notes.

Your job is not to collect everything. Your job is to preserve reusable knowledge with source traceability.

## Current phase

We are in P0.

P0 means:

* preserve existing notes
* avoid over-structuring
* allow only small deterministic helper scripts for local checks, indexing, logging, and export
* avoid heavy, background, or autonomous automation
* avoid vector databases
* avoid graph databases
* avoid MCP
* avoid multi-agent workflows
* avoid large rewrites

Do not introduce new frameworks, databases, background agents, autonomous workflows, or complex scripts unless explicitly asked. Task procedures belong in Skills; AGENTS.md sets repository policy only.

## Repository model

* Existing Obsidian notes are valid source material.
* `raw/` is for new unprocessed notes and imported source material.
* `raw/imported/` contains imported Obsidian notes and should be treated as source material.
* `raw/inbox/` is for new unprocessed notes.
* `wiki/` is for compiled durable knowledge.
* `wiki/topics/` is for general concepts and topic documents.
* `wiki/decisions/` is for decisions and tradeoffs.
* `wiki/anti-patterns/` is for mistakes, traps, and things to avoid.
* `wiki/index.md` is a navigation-only lightweight generated view of compiled wiki notes.
* `golden_questions.yml` is the manually curated evaluation set and is immutable to all skills unless the user explicitly asks to edit it.
* `.private/` is local-only tracking metadata and must not be treated as public content.
* `.private/compiled_sources.yml` tracks which raw source notes have already been compiled into wiki notes.
* `.private/knowledge_cycle_log.md` records operational maintenance history only.
* `.private/eval_runs/` contains local-only evaluation reports.
* `public/` is for public-safe exported outputs.
* `.agents/skills/` contains task-specific skill instructions. Skills must read and follow `AGENTS.md`; they must not override repository policy.
* `prompts/`, if present, contains legacy or ad hoc task prompts. Current maintained workflows should prefer skills.
* `scripts/` contains local helper scripts for listing, checking, indexing, logging, and exporting. Scripts are not agents.
* `AGENTS.md` is the source of truth for repository rules.
* `README.md` is a human-facing overview, not a rules source.

## Hard rules

1. Do not merge all notes into one file.
2. Do not rewrite original notes unless explicitly asked.
3. Prefer small diffs.
4. Before creating a new wiki note, search for an existing related note.
5. Preserve source traceability.
6. Every non-obvious claim in `wiki/` must point back to source notes.
7. Do not invent facts.
8. Do not silently delete or overwrite old knowledge.
9. If information conflicts, mark the conflict instead of resolving it silently.
10. Do not auto-commit. Show proposed changes first.
11. Do not modify `golden_questions.yml` from repository skills. It is manually curated.
12. Generated sections in `wiki/index.md` must be updated by deterministic scripts after their markers exist.

## Minimal frontmatter for P0

Use this only when creating new wiki notes:

```yaml
---
id: short-stable-id
type: topic | decision | anti-pattern
source:
  - src_source_id
valid_from: YYYY-MM-DD
---
```

Do not require tags, confidence, valid_to, embeddings, graph IDs, or links in P0.

P0 wiki notes only use `topic`, `decision`, or `anti-pattern` as frontmatter `type`.
Wiki frontmatter keeps the field name `source` as a list, and every value must be a stable `src_...` source ID.
Raw source paths belong only in `.private/compiled_sources.yml`, where the registry owns `source_id` -> `source_path` -> `outputs` mappings.
Source IDs must remain stable if raw files are moved or renamed.
`project` and `question` material remains in raw notes or task discussion unless explicitly promoted into `topic`, `decision`, or `anti-pattern` wiki notes.

## Knowledge types

When processing notes, classify reusable knowledge as one of:

* topic: durable concept or explanation
* decision: a choice, tradeoff, or judgment
* anti-pattern: a mistake, trap, misconception, or thing to avoid
* project: ongoing work or implementation context
* question: open question worth evaluating later

## Generated index

The compiled wiki list in `wiki/index.md` is generated between these markers:

```md
<!-- BEGIN GENERATED WIKI INDEX -->
<!-- END GENERATED WIKI INDEX -->
```

Do not leave compiled wiki links duplicated outside that generated block.

## Scope

This is a general knowledge repo. Do not restrict the system to infrastructure only.

However, avoid mixing unrelated domains in one note. If a note contains multiple domains, propose splitting it into topic-specific wiki notes while preserving the original source.
