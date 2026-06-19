---
name: evaluate-knowledge
description: Performs coverage-only evaluation of either the private wiki or the public corpus against golden questions. Use when explicitly invoked as $evaluate-knowledge or when orchestrated by $knowledge-cycle to check whether wiki/ or public/ contains evidence that covers the question set; it does not synthesize canonical answers or modify evaluated material.
---

# Evaluate Knowledge

Read and follow `AGENTS.md` first. This is coverage-only evaluation: assess whether the target corpus contains evidence for each golden question. Do not answer the questions as final knowledge, invent unsupported answers, or modify evaluated notes or evaluation criteria.

## Inputs

- Target corpus: exactly one of `wiki/` or `public/`. Default to `wiki/`.
- Question set: `golden_questions.yml` at the repository root.
- Previous reports only to avoid filename collisions.

Raw notes are prohibited.

Existing reports under `evals/reports/` are legacy read-only artifacts. Do not modify, delete, or append to them.

## Outputs

- One new coverage report under `.private/eval_runs/YYYY-MM-DD-HHMM-<target>.md`.

Never overwrite a previous report. Never write new reports under `evals/reports/`.

## Procedure

1. Read `AGENTS.md`.
2. Resolve exactly one target corpus. Use `wiki/` by default.
3. Read `golden_questions.yml`.
4. Evaluate all questions except entries explicitly marked disabled.
5. Search only the selected target corpus.
6. For each question, determine whether the target corpus contains evidence that supports coverage.
7. If evidence is absent from the selected corpus, record missing coverage. Do not consult raw notes.
8. Record conflicts when evidence disagrees.
9. Do not synthesize canonical answers or fill gaps from general knowledge.
10. Record the evaluated Git commit with `git rev-parse HEAD` when available.
11. Create exactly one new report at the required `.private/eval_runs/` path.

## Report Contents

Include:

- evaluated Git commit, when available
- target corpus
- question-set path
- per-question coverage status
- evidence files
- gaps and conflicts
- summary counts

## Stopping Conditions

- Stop if the target corpus is ambiguous or more than one target is requested.
- Stop if the report path already exists.
- Stop rather than modifying evaluated notes or the question set.

## Completion Criteria

- One new coverage report was appended under `.private/eval_runs/`.
- Every enabled golden question has a coverage status, evidence files when available, and gap notes when coverage is missing.
