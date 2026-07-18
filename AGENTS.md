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
- `examples/` — generated documents kept as the visual acceptance baseline.
- `assets/` — the logo plus `screenshots/` (README previews of the examples);
  generated documents never reference it.

## Editing rules

- `references/design-system.md` and `templates/document.html` change together. A token
  changed in one must change in the other in the same commit.
- All skill files are written in English. Generated documents use the reader's language.
- The gate must pass before any commit touching `templates/` or `examples/`:
  `bash scripts/check.sh templates/demos/*.html examples/*.html`
- `scripts/` stays stdlib-only and self-contained. No new dependencies, no build step,
  no package manager.
- New demos follow the contract in `references/demos.md` (scoped selectors, prefixed
  keyframes, `currentScript` IIFE, no ids) and add exactly one row to its catalog.
- Catalogs consolidate: fold new banned phrases into the existing lists in the writing
  references instead of appending near-synonyms.
