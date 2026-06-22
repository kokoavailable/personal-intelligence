---
name: publish-knowledge
description: Exports selected private wiki notes as public-safe documents. Use only when explicitly invoked as $publish-knowledge to prepare, sanitize, validate, or publish selected wiki/ knowledge into public/.
---

# Publish Knowledge

Read and follow `AGENTS.md` first. Publishing is separate from the default private knowledge cycle.

## Inputs

- User-selected notes from `wiki/`.
- Existing files under `public/`, only to prepare the resulting public diff.
- Existing deterministic scripts under `scripts/`, especially the public leak validation.

## Outputs

- Proposal mode: public-safe draft changes under `public/` only, shown as a complete public diff.
- After separate exact approval: only approved writes under `public/`.

Never modify `raw/`, `.private/`, or source `wiki/` notes.

## Procedure

1. Read `AGENTS.md`.
2. Read the selected `wiki/` notes.
3. Prepare public-safe output that preserves reusable technical knowledge.
4. Remove or generalize private, personal, organization-specific, source-path, source-ID, environment, credential, and secret-like material.
5. Show the complete proposed `public/` diff.
6. Stop for a separate explicit approval before writing.
7. Only the exact response `approve` authorizes writing.
8. Treat a repeated request to run the skill as not approval.
9. After approval, write only the approved `public/` files.
10. Run the verified public leak validation command:

   ```bash
   python3 -B scripts/check_no_raw_leak.py public
   ```

11. Report validation results and the final public diff.

Use `scripts/export_public.py` only when its marker-based behavior matches the selected publishing task. Do not duplicate or move deterministic scripts into the skill.
`scripts/export_public.py` fails before writing a note if the generated public output would contain `raw/imported/`, `raw/inbox/`, or private `src_...` references; it does not silently redact them.

## Stopping Conditions

- Stop before writing during proposal mode.
- Stop unless the exact response `approve` is received.
- Stop if no source `wiki/` notes were selected.
- Stop if the public-safe version would require checking raw or private files not allowed for the publishing task.
- Stop if validation fails. Do not make unrelated repairs.

## Completion Criteria

- Only `public/` changed.
- Source `wiki/`, `raw/`, and `.private/` were not modified.
- The public diff was separately approved with the exact response `approve` before writing.
- Public leak validation passed or the failure was reported.
