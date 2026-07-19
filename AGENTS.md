# AGENTS.md

Hue is a single skill: it turns natural-language descriptions into elegant, single-file,
interactive requirement documents. This repository is the skill — root-level `SKILL.md`,
installable as-is into agentskills-compatible hosts (`~/.kimi-code/skills/hue/`,
`.claude/skills/`, or any loader that reads `SKILL.md`).

## Layout

- `SKILL.md` — the entrypoint an agent reads: contract, workflow, language routing, gate.
- `references/design-system.md` — the design spec and the only source of visual truth.
- `references/writing-zh.md`, `references/writing-en.md` — prose quality rules per
  document language.
- `references/demos.md` — demo block contract and catalog.
- `templates/document.html` — the base template; the only implementation of the design
  system. Fill slots, never edit its `<style>`.
- `templates/demos/*.html` — self-contained interactive blocks, one file per demo.
- `scripts/check.py` / `check.sh` — the quality gate (Python stdlib only).
- `scripts/sync-template.py` / `sync-template.sh` — re-syncs the template's base
  `<style>` block into generated documents.
- `scripts/embed-image.py` / `embed-image.sh` — embeds a user-supplied image into a
  document's `image` demo block as a base64 data URI (stdlib only; base64 never
  touches stdout).
- `examples/` — generated documents kept as the visual acceptance baseline.
- `assets/` — the logo plus `screenshots/` (README previews of the examples);
  generated documents never reference it.

## Editing rules

- `references/design-system.md` and `templates/document.html` change together. A token
  changed in one must change in the other in the same commit.
- All skill files are written in English. Generated documents use the reader's language.
- The gate must pass before any commit touching `templates/` or `examples/`:
  `bash scripts/check.sh templates/demos/*.html examples/*.html`
- After changing the `<style>` block in `templates/document.html`, re-sync every
  generated document with `bash scripts/sync-template.sh` (defaults to
  `examples/*.html`; pass explicit files to sync others). It rewrites only the
  first line-anchored `<style>` block of each file — prose and embedded demo
  blocks are untouched, so re-run the gate afterwards. Demo blocks are
  translated on insert and always sync by hand.
- `scripts/` stays stdlib-only and self-contained. No new dependencies, no build step,
  no package manager.
- New demos follow the contract in `references/demos.md` (scoped selectors, prefixed
  keyframes, `currentScript` IIFE, no ids) and add exactly one row to its catalog.
- A demo or example update is not done when the gate passes: check whether the same
  change must be reflected in `SKILL.md` (block count, demo list, workflow),
  `README.md` (block counts, feature bullets, screenshots), and `examples/` (the
  showcase is the visual baseline — new blocks appear there, in both languages).
- Catalogs consolidate: fold new banned phrases into the existing lists in the writing
  references instead of appending near-synonyms.
