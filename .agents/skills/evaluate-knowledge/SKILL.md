---
name: evaluate-knowledge
description: Runs repository-local knowledge evaluation suites. Use when explicitly invoked as $evaluate-knowledge with a selected suite, or when orchestrated by $knowledge-cycle to run compile-fidelity and golden-answerability in sequence.
---

# Evaluate Knowledge

Read and follow `AGENTS.md` first. This skill owns evaluation criteria and evaluation-report persistence.

It defines exactly two suites:

- `compile-fidelity`
- `golden-answerability`

For direct invocation, the user must explicitly select one suite. When orchestrated by `$knowledge-cycle`, run both suites in the required sequence:

1. read-only `compile-fidelity` preview before approval
2. final persisted `compile-fidelity` after approval, application, deterministic validation, and index update/check
3. persisted `golden-answerability` against `wiki/`

Do not modify evaluated notes, proposed notes, source notes, or `golden_questions.yml`.

## Inputs

- Suite: exactly one of `compile-fidelity` or `golden-answerability`.
- Previous reports only to avoid filename collisions.

For `compile-fidelity`:

- Source notes used by the compile proposal.
- Proposed or applied `wiki/` changes.
- Proposed or applied `.private/compiled_sources.yml` changes.
- Existing `wiki/` notes needed to check already-represented knowledge.
- Source-exhaustion findings from `compile-knowledge`.

Wiki frontmatter must keep `source` as a list of registry-backed `src_...` IDs. Raw paths belong only in `.private/compiled_sources.yml`.

For `golden-answerability`:

- Target corpus: exactly one of `wiki/` or `public/`.
- Question set: `golden_questions.yml` at the repository root.
- Previous reports only to avoid filename collisions.

Raw notes are allowed only for `compile-fidelity`. Raw notes are prohibited for `golden-answerability`.

Existing reports under `evals/reports/` are legacy read-only artifacts. Do not modify, delete, or append to them.

## Outputs

- `compile-fidelity` preview: read-only result in the response; no file is written.
- `compile-fidelity` final report: `.private/eval_runs/YYYY-MM-DD-HHMM-compile-fidelity.md`.
- `golden-answerability` report: `.private/eval_runs/YYYY-MM-DD-HHMM-golden-answerability-<target>.md`.

Never overwrite a previous report. Never write new reports under `evals/reports/`.

## Compile-Fidelity Suite

Purpose: determine whether proposed or applied wiki and registry changes faithfully preserve reusable knowledge from the selected source notes.

For each source, evaluate:

- source-exhaustion correctness
- unsupported factual claims
- material durable-knowledge omissions
- source-to-wiki traceability
- conflict preservation
- schema and integrity compatibility
- wiki `source` IDs resolve through `.private/compiled_sources.yml`
- non-blocking note-boundary, duplication, or wording concerns

Outcomes:

- `FAIL` when any of these applies:
  - unsupported factual claims
  - material durable-knowledge omission
  - source exhaustion is false while a registry entry is proposed
  - broken source-to-wiki traceability
  - source conflicts were silently removed
  - wiki frontmatter uses raw paths, malformed source IDs, or source IDs absent from the registry
  - schema or integrity violation
- `WARN` for non-blocking note-boundary, duplication, or wording concerns.
- `PASS` when no `FAIL` condition exists and there are no unresolved warnings.

A `FAIL` before approval must cause the proposal to be revised before asking for `approve`.

The final persisted report must evaluate the actual applied wiki files and registry entries, not merely copy the pre-approval preview.

## Golden-Answerability Suite

Purpose: determine whether the selected corpus can answer each enabled golden question.

For every enabled golden question:

1. Generate a candidate answer using only the selected corpus.
2. Cite supporting corpus files.
3. Evaluate supportedness.
4. Evaluate completeness.
5. Evaluate directness.
6. Evaluate conflict handling.
7. Identify missing knowledge.
8. Assign a per-question status.

The candidate answer is an evaluation artifact, not canonical knowledge. Do not write it into `wiki/` or `public/`.

Use these per-question statuses:

- `pass`: answer is supported, complete enough, direct, and handles conflicts.
- `partial`: answer has some support but is incomplete, indirect, or has unresolved conflict-handling gaps.
- `fail`: selected corpus cannot answer the question without unsupported invention.

## Procedure For Direct Invocation

1. Read `AGENTS.md`.
2. Require explicit suite selection: `compile-fidelity` or `golden-answerability`.
3. For `compile-fidelity`, require explicit proposed/applied artifacts and source-exhaustion findings.
4. For `golden-answerability`, require exactly one target corpus: `wiki/` or `public/`.
5. Record the evaluated Git commit with `git rev-parse HEAD` when available.
6. Produce the selected suite result.
7. Persist exactly one report only when report persistence is requested or when orchestrated by `knowledge-cycle`.

## Procedure For Knowledge Cycle

1. Receive the compile proposal, source notes, proposed registry changes, and source-exhaustion findings.
2. Run read-only `compile-fidelity` preview before approval.
3. If the preview outcome is `FAIL`, require proposal revision before approval.
4. After exact approval, application, deterministic validation, and index update/check, run final `compile-fidelity` against the actual applied wiki files and registry entries.
5. Persist exactly one final `compile-fidelity` report.
6. Run `golden-answerability` against `wiki/`.
7. Persist exactly one `golden-answerability` report.

## Report Contents

Every report includes:

- evaluated Git commit, when available
- suite name
- evaluated inputs
- report timestamp
- summary outcome

`compile-fidelity` reports include:

- source IDs and source paths
- proposed or applied wiki files
- proposed or applied registry entries
- source-exhaustion findings
- outcome: `PASS`, `WARN`, or `FAIL`
- per-finding severity
- supporting source references
- required proposal revisions when outcome is `FAIL`

`golden-answerability` reports include these fields for every enabled question:

- question
- candidate answer
- evidence files
- supportedness
- completeness
- directness
- conflict handling
- missing knowledge
- status

## Stopping Conditions

- Stop if direct invocation does not explicitly select a suite.
- Stop if the target corpus is ambiguous or more than one target is requested for `golden-answerability`.
- Stop if the report path already exists.
- Stop rather than modifying evaluated notes or the question set.
- Stop if `golden-answerability` would require raw notes or general knowledge to answer a question.
- Stop if `compile-fidelity` lacks the source notes, proposed/applied wiki files, proposed/applied registry entries, or source-exhaustion findings required for evaluation.

## Completion Criteria

- The selected suite was explicit.
- Any persisted report was written exactly once under `.private/eval_runs/`.
- `compile-fidelity` reports have a clear `PASS`, `WARN`, or `FAIL` outcome.
- `golden-answerability` reports include every enabled golden question and all required per-question fields.
