---
name: compile-knowledge
description: Compiles a small batch of unprocessed raw notes into private wiki notes. Use when explicitly invoked as $compile-knowledge or when orchestrated by $knowledge-cycle to ingest, compile, or update raw source notes into wiki/ while preserving source traceability in this repository.
---

# Compile Knowledge

Read and follow `AGENTS.md` first. Treat it as the repository policy source; do not restate or override repository-wide schemas, source-ID policy, or public/private boundaries here.

## Inputs

- User-selected raw notes, or unprocessed candidates from `raw/inbox/` and `raw/imported/`.
- `.private/compiled_sources.yml`, when present.
- Existing `wiki/` notes.

## Outputs

- Proposal mode: at most 3 `wiki/` note creations or updates plus matching `.private/compiled_sources.yml` changes.
- After exact approval: only the approved `wiki/` and `.private/compiled_sources.yml` changes.

The `wiki/` changes and `.private/compiled_sources.yml` changes are one logical change.

Do not modify evaluation criteria during compilation.

## Procedure

1. Read `AGENTS.md`.
2. Read `.private/compiled_sources.yml` if it exists.
3. Exclude sources already listed in the registry unless the user explicitly requested an update to existing wiki notes.
4. Inspect the selected source notes. Never modify `raw/imported/`.
5. Search existing `wiki/` notes before proposing new notes.
6. Identify reusable knowledge, conflicts, and possible note boundaries.
7. Draft at most 3 wiki note changes and the matching source-registry changes together.
8. Show one combined proposed diff covering `wiki/` and `.private/compiled_sources.yml`.
9. Stop and wait for explicit approval before writing.
10. Only the exact response `approve` authorizes writing.
11. Treat a repeated request to run the skill as not approval.

## Stopping Conditions

- Stop before writing any file during proposal mode.
- Stop unless the exact response `approve` is received.
- Stop if the requested sources are already compiled and no explicit update was requested.
- Stop if source traceability cannot be preserved.
- Stop if a safe, policy-compliant source ID cannot be chosen.
- Stop if conflicts in the source material cannot be represented without inventing facts.

## Completion Criteria

- No more than 3 wiki notes were created or updated.
- `raw/imported/` was not modified.
- The registry entries match the wiki outputs they support.
- The combined diff was approved with the exact response `approve` before writing.
