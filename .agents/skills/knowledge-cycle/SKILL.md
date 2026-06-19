---
name: knowledge-cycle
description: Runs one complete private knowledge-maintenance cycle. Use only when explicitly invoked as $knowledge-cycle to compile, validate, and evaluate the private wiki in a single repository-local workflow.
---

# Knowledge Cycle

Keep this skill thin. Read and orchestrate sibling task skills instead of redefining their detailed rules.

## Inputs

- `AGENTS.md`.
- `.agents/skills/compile-knowledge/SKILL.md`.
- `.agents/skills/evaluate-knowledge/SKILL.md`.
- Existing validation scripts under `scripts/`.

## Outputs

- Approved private wiki and source-registry changes from the compile step.
- One appended wiki coverage report from the evaluate step.

Never modify or publish `public/`. Do not modify evaluation criteria during the same knowledge cycle.

## Procedure

1. Follow `AGENTS.md`.
2. Read `.agents/skills/compile-knowledge/SKILL.md`.
3. Follow the `compile-knowledge` workflow in proposal mode.
4. Show one combined wiki and source-registry diff.
5. Stop and wait for explicit approval.
6. Only the exact response `approve` authorizes writing.
7. Treat a repeated request to run the skill as not approval.
8. After approval, apply only the approved compile changes.
9. Run:

   ```bash
   python3 -B scripts/check_wiki_integrity.py
   python3 -B scripts/check_no_raw_leak.py
   git diff --check
   ```

10. If validation fails, stop and report the failure. Do not make unrelated repairs.
11. If validation passes, read `.agents/skills/evaluate-knowledge/SKILL.md`.
12. Follow the `evaluate-knowledge` workflow against `wiki/`.
13. Automatically append a new coverage report.
14. Summarize the cycle.

## Summary Contents

Include sources compiled, wiki notes created or updated, registry changes, validation results, evaluation coverage results, and remaining coverage gaps.

## Stopping Conditions

- Stop before writing until the exact response `approve` is received.
- Stop if validation fails.
- Stop if the compile proposal cannot preserve traceability.
- Stop before any public publishing action.

## Completion Criteria

- Approved compile changes were applied exactly.
- Validation passed.
- One new `wiki/` coverage report was appended under `.private/eval_runs/`.
