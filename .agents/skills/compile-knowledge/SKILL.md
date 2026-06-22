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

- Proposal mode: at most 3 `wiki/` note creations or updates, matching `.private/compiled_sources.yml` changes, and source-exhaustion findings.
- After exact approval: only the approved `wiki/` and `.private/compiled_sources.yml` changes.

The `wiki/` changes and `.private/compiled_sources.yml` changes are one logical change.
Wiki frontmatter keeps `source` as a list of stable `src_...` IDs. Do not write raw paths into wiki frontmatter and do not rename the field to `source_id`.
The registry owns the `source_id` -> `source_path` -> `outputs` mapping, and source IDs remain stable if raw files are moved or renamed.

Do not modify `golden_questions.yml` or any evaluation criteria during compilation.
Do not persist evaluation reports. Evaluation criteria and evaluation-report persistence belong to `evaluate-knowledge`.

## Procedure

1. Read `AGENTS.md`.
2. Read `.private/compiled_sources.yml` if it exists.
3. Exclude sources already listed in the registry unless the user explicitly requested an update to existing wiki notes.
4. Inspect the selected source notes. Never modify `raw/imported/`.
5. Search existing `wiki/` notes before proposing new notes.
6. Identify reusable knowledge, conflicts, and possible note boundaries.
7. Draft at most 3 wiki note changes and the matching source-registry changes together.
8. Run a source-exhaustion check for every source that would receive a registry entry.
9. When orchestrated by `knowledge-cycle`, provide the proposal and source-exhaustion findings to `evaluate-knowledge` for a read-only `compile-fidelity` preview.
10. Show one combined proposed diff covering `wiki/` and `.private/compiled_sources.yml`, plus source-exhaustion findings.
11. Stop and wait for explicit approval before writing.
12. Only the exact response `approve` authorizes writing.
13. Treat a repeated request to run the skill as not approval.

## Source-Exhaustion Check

For each source that would be marked compiled in `.private/compiled_sources.yml`, explicitly state whether durable reusable knowledge from that source is exhausted.

`source_exhausted: true` means every material durable point is either:

- represented in the proposed wiki changes
- already represented in existing wiki notes
- explicitly classified as non-durable, private, or project-specific material

Without a partial-compilation registry state, any deferred durable reusable knowledge requires `source_exhausted: false`.

If `source_exhausted: false`, do not propose a registry entry for that source.

## Stopping Conditions

- Stop before writing any file during proposal mode.
- Stop unless the exact response `approve` is received.
- Stop if the requested sources are already compiled and no explicit update was requested.
- Stop if source traceability cannot be preserved.
- Stop if deferred durable reusable knowledge would require a registry entry.
- Stop if a safe, policy-compliant source ID cannot be chosen.
- Stop if a proposed wiki `source` value is a raw path, malformed source ID, or source ID absent from `.private/compiled_sources.yml`.
- Stop if conflicts in the source material cannot be represented without inventing facts.

## Completion Criteria

- No more than 3 wiki notes were created or updated.
- `raw/imported/` was not modified.
- Wiki frontmatter uses `source` lists containing only registry-backed `src_...` IDs.
- The registry entries match the wiki outputs they support.
- The combined diff was approved with the exact response `approve` before writing.
- Source-exhaustion findings are explicit for every proposed registry entry.
