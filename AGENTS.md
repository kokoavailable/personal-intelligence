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
* avoid automation
* avoid vector databases
* avoid graph databases
* avoid MCP
* avoid multi-agent workflows
* avoid large rewrites

Do not introduce new frameworks, databases, background agents, or complex scripts unless explicitly asked.

## Repository model

* Existing Obsidian notes are valid source material.
* `raw/` is for new unprocessed notes and imported source material.
* `raw/imported/` contains imported Obsidian notes and should be treated as source material.
* `raw/inbox/` is for new unprocessed notes.
* `wiki/` is for compiled durable knowledge.
* `wiki/topics/` is for general concepts and topic documents.
* `wiki/decisions/` is for decisions and tradeoffs.
* `wiki/anti-patterns/` is for mistakes, traps, and things to avoid.
* `index.md` is the lightweight map.
* `golden_questions.yml` is the evaluation set.
* `log.md` records important maintenance actions.

## Hard rules

1. Do not merge all notes into one file.
2. Do not rewrite original notes unless explicitly asked.
3. Prefer small diffs.
4. Before creating a new wiki note, search for an existing related note.
5. Preserve source paths.
6. Every non-obvious claim in `wiki/` must point back to source notes.
7. Do not invent facts.
8. Do not silently delete or overwrite old knowledge.
9. If information conflicts, mark the conflict instead of resolving it silently.
10. Do not auto-commit. Show proposed changes first.

## Minimal frontmatter for P0

Use this only when creating new wiki notes:

```yaml
---
id: short-stable-id
type: topic | decision | anti-pattern
source:
  - path/to/source.md
valid_from: YYYY-MM-DD
---
```

Do not require tags, confidence, valid_to, embeddings, graph IDs, or links in P0.

P0 wiki notes only use `topic`, `decision`, or `anti-pattern` as frontmatter `type`.
`project` and `question` items should remain in raw notes, `index.md`, or `log.md` unless explicitly promoted into one of those wiki types.

## Knowledge types

When processing notes, classify reusable knowledge as one of:

* topic: durable concept or explanation
* decision: a choice, tradeoff, or judgment
* anti-pattern: a mistake, trap, misconception, or thing to avoid
* project: ongoing work or implementation context
* question: open question worth evaluating later

## Ingestion workflow

When asked to ingest notes:

1. Inspect the source files.
2. Summarize what is reusable.
3. Propose at most 3 wiki changes.
4. Propose index updates.
5. Propose golden question updates only if useful.
6. Show a diff.
7. Wait for approval before making broad changes.

## Scope

This is a general knowledge repo. Do not restrict the system to infrastructure only.

However, avoid mixing unrelated domains in one note. If a note contains multiple domains, propose splitting it into topic-specific wiki notes while preserving the original source.
