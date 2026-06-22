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
- One final compile-fidelity report under `.private/eval_runs/`.
- One golden-answerability report for `wiki/` under `.private/eval_runs/`.
- One `wiki/index.md` update/check result.
- One append-only completed-cycle entry in `.private/knowledge_cycle_log.md` through `scripts/append_log.py`.

Never modify or publish `public/`. Do not modify `golden_questions.yml` or any evaluation criteria during the same knowledge cycle.

## Procedure

Before compiling, verify local workspace files explicitly:

```bash
python3 -B scripts/init_workspace.py --check
```

If the workspace check fails, stop and instruct the user to run `python3 -B scripts/init_workspace.py --write`. Do not initialize the workspace silently.

1. Follow `AGENTS.md`.
2. Read `.agents/skills/compile-knowledge/SKILL.md`.
3. Read `.agents/skills/evaluate-knowledge/SKILL.md`.
4. Create the compile proposal in proposal mode.
5. Run the source-exhaustion check for every proposed registry entry.
6. Run a read-only `compile-fidelity` preview through `evaluate-knowledge`.
7. Show the combined wiki and source-registry proposal together with source-exhaustion findings and the compile-fidelity preview result.
8. If compile-fidelity is `FAIL`, revise the proposal before asking for approval.
9. Stop and wait for explicit approval.
10. Only the exact response `approve` authorizes writing.
11. Treat a repeated request to run the skill as not approval.
12. After approval, apply only the approved `wiki/` and `.private/compiled_sources.yml` changes.
13. Run deterministic validation:

   ```bash
   python3 -B scripts/check_wiki_integrity.py
   python3 -B scripts/check_no_raw_leak.py
   git diff --check
   ```

14. If validation fails, stop and report the failure. Do not persist evaluations. Do not append the cycle log.
15. Run deterministic index update and check:

   ```bash
   python3 -B scripts/update_index.py --write
   python3 -B scripts/update_index.py --check
   ```

16. Record `index_status` as `updated` if `update_index.py --write` changed `wiki/index.md`; otherwise record `unchanged`.
17. If index update or index check fails, stop and report the failure. Do not persist evaluations. Do not append the cycle log.
18. Run or verify final `compile-fidelity` through `evaluate-knowledge` against the actual applied wiki files and registry entries.
19. Persist exactly one final report under `.private/eval_runs/YYYY-MM-DD-HHMM-compile-fidelity.md`.
20. Run `golden-answerability` through `evaluate-knowledge` against `wiki/`.
21. Persist exactly one report under `.private/eval_runs/YYYY-MM-DD-HHMM-golden-answerability-wiki.md`.
22. Append one canonical completed-cycle entry to `.private/knowledge_cycle_log.md` through `scripts/append_log.py`:

   ```bash
   python3 -B scripts/append_log.py \
     --cycle-id YYYY-MM-DD-HHMM-knowledge-cycle \
     --source-id src_example_001 \
     --wiki-output wiki/topics/example.md \
     --index-status updated \
     --compile-fidelity-report .private/eval_runs/YYYY-MM-DD-HHMM-compile-fidelity.md \
     --golden-answerability-report .private/eval_runs/YYYY-MM-DD-HHMM-golden-answerability-wiki.md \
     --write
   ```

23. Provide the final summary.

## Summary Contents

Include source IDs compiled, wiki notes created or updated, registry changes, validation results, index status, final compile-fidelity outcome, golden-answerability results, canonical log entry status, and remaining missing knowledge.

## Stopping Conditions

- Stop before writing until the exact response `approve` is received.
- Stop before asking for approval if the compile-fidelity preview is `FAIL`.
- Stop if validation fails.
- Stop if index update or index check fails.
- Stop if final compile-fidelity cannot be run against the actual applied files and registry entries.
- Stop if either evaluation report cannot be persisted.
- Stop if `scripts/append_log.py --write` rejects the cycle entry.
- Stop if the compile proposal cannot preserve traceability.
- Stop before any public publishing action.

## Completion Criteria

- Approved compile changes were applied exactly.
- Validation passed.
- The generated wiki index was updated and checked.
- Final compile-fidelity was run against actual applied files and registry entries.
- One compile-fidelity report was persisted under `.private/eval_runs/`.
- One golden-answerability report for `wiki/` was persisted under `.private/eval_runs/`.
- One canonical completed-cycle entry was appended to `.private/knowledge_cycle_log.md` through `scripts/append_log.py`.
