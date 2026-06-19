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
* `.private/eval_runs/` is for append-only evaluation run reports.
* `evals/reports/` contains legacy evaluation reports and should be treated as read-only.
* `AGENTS.md` is the source of truth for repository rules.
* `README.md` is a human-facing overview, not a rules source.

## Source tracking

`.private/compiled_sources.yml` is the local-only registry that maps private raw source paths to stable source IDs.

Use this schema:

```yaml
compiled_sources:
  - source_id: src_short_stable_id
    source_path: raw/imported/path-to-source.md
    outputs:
      - wiki/topics/example.md
    compiled_at: YYYY-MM-DD
```

Rules:

1. Raw source paths must be stored only in `.private/compiled_sources.yml`.
2. New wiki notes must use source IDs in frontmatter.
3. Existing wiki notes should be migrated from raw source paths to source IDs.
4. Public exports must remove both raw source paths and private source IDs.
5. Before compiling a new batch, read `.private/compiled_sources.yml`.
6. Do not recompile sources already listed there unless explicitly updating existing wiki notes.
7. `source_id` should be stable, short, and topic-based, for example `src_vmss_rolling_upgrade_001`.
8. Do not include company names, internal domains, environment names, incident IDs, personal names, or secret-like values in `source_id`.

## Evaluation state

`golden_questions.yml` at the repository root is the evaluation specification.

New evaluation runs must be written only under `.private/eval_runs/YYYY-MM-DD-HHMM-<target>.md`.

Existing reports under `evals/reports/` are legacy read-only artifacts. Do not modify, delete, or append to them.

Evaluation is coverage-only: it checks whether exactly one target corpus, `wiki/` or `public/`, contains evidence for the golden questions. Raw notes are prohibited during evaluation runs. Do not synthesize canonical answers, invent unsupported answers, or modify evaluated notes or evaluation criteria during an evaluation run. Do not modify `golden_questions.yml` during compilation or during the same knowledge cycle; propose evaluation-criteria changes separately.

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
