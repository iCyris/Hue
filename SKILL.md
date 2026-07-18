---
name: hue
description: "Generates elegant single-file HTML requirement documents from natural-language descriptions, with interactive demos embeddable anywhere in the reading flow. Use when users ask in any language to write or express a requirement, PRD, or feature spec as a readable HTML page, or to illustrate behavior with embedded interactive demos. Not for application UI, multi-page sites, landing pages, or editing arbitrary existing HTML."
when_to_use: "写需求, 需求文档, 需求表达, 生成需求页面, PRD, 功能说明, 产品需求, 加个demo, 演示交互, requirement doc, requirement html, PRD html, spec document, feature spec, express this requirement, interactive demo"
dispatch_intent: "Requirement document generation, spec-to-HTML, interactive demo embedding, single-file document"
---

# Hue: Requirement Documents People Actually Read

Turn a natural-language description into one beautiful, self-contained HTML document:
title, structured prose, and interactive demos that match the page's design language.
Named after the hydrangea (绣球花): one plant, many quiet hues; one design system, many
documents.

## Outcome Contract

- Outcome: a rough description becomes a single `.html` file a teammate can open and
  read end to end, with working interactive demos where behavior needs showing.
- Done when: every template slot is filled, the prose passes the writing rules for the
  document's language, all demos come from `templates/demos/` with their visible strings
  translated, and the Quality Gate prints `check: ok`.
- Evidence: the user's description, this skill's templates and references, and the gate
  output. Never invent metrics, dates, owners, or user research.
- Output: one file named `<kebab-case-title>.html` in the working directory, plus a
  short reply listing structure and demos. No sidecar files, no screenshots.

## Core Stance

- The template owns every pixel. You own the content. You never write, extend, or
  override CSS; `templates/document.html` already implements
  `references/design-system.md`.
- A demo is evidence, not decoration. Insert one where the reader would otherwise have
  to imagine behavior; three good demos beat six scattered ones.
- Writing quality is half the product. A requirement document with AI-flavored prose
  fails even when it renders perfectly.

## Pre-flight

1. **Description present?** If the user gave only a topic ("a login page requirement"),
   ask for the one blocking fact (what behavior matters most) or proceed with stated
   assumptions when asking is not possible.
2. **Language routed from the document, not the command.** Default: the language of the
   user's description. If the user asks for a specific output language, that wins.
   Load `references/writing-zh.md` for Chinese output, `references/writing-en.md` for
   English.
3. **Demos.** If the user named positions or components, follow exactly. Otherwise
   choose at most 3 from the catalog in `references/demos.md`, placed where behavior is
   hardest to imagine in words; report your choices in the final reply.

## Workflow

1. Read `templates/document.html` fully. It is the only thing you are allowed to fill.
2. Draft the structure internally: title, lead, sections (typically background /
   scope / behavior / edge cases / acceptance criteria), demo slots. Follow the
   structure rules in the loaded writing reference.
3. Copy the template to `<kebab-case-title>.html` and fill every `@slot`:
   - Set `<html lang>` (`zh-CN` or `en`) and `<title>`.
   - Fill header (tag, meta, title, lead, optional meta table), sections, footer.
   - For each demo slot: paste the whole block from `templates/demos/<name>.html`
     inside `<figure class="demo">`, add a one-sentence `<figcaption>` per the writing
     reference, and translate every visible string in the block into the document
     language (labels, buttons, messages, aria-labels).
4. Run the Quality Gate (below). Fix every error and re-run until `check: ok`.
5. Reply: file path, section list, demos included, and anything the user should verify
   by opening the file.

## Quality Gate

Before delivering, run (skill dir = the directory containing this SKILL.md):

```bash
bash <skill-dir>/scripts/check.sh --lang auto <file>.html
# fallback if the skill dir is unknown:
bash ./scripts/check.sh --lang auto <file>.html
```

The gate checks structure (doctype, lang, charset, viewport, title, leftover `@slot`),
self-containment (no external resources, no inline styles), token discipline (raw hex
and font stacks only inside `:root`/`html[lang]` blocks), language rules (zh: half-width
punctuation next to CJK, CJK-Latin spacing; both: no em/en dash; en: no double spaces),
and the demo contract (scoped selectors, prefixed keyframes, `currentScript` scoping,
no duplicate ids).

- `--fix` rewrites only unambiguous zh CJK-Latin spacing. Everything else is yours to
  fix by editing the document.
- Exit code 1 with findings means the document does not ship. No exceptions.

## Demo System

Fifteen blocks live in `templates/demos/` (button-states, form-validation, toggle,
slider, segmented-control, tabs, accordion, stepper, dialog, toast, progress, skeleton,
card-list, spring-motion, wireframe). The contract and per-block guidance:
`references/demos.md`.

- Use blocks verbatim. If a needed component is not in the catalog, compose it from
  document components (callout, table, list) or tell the user it is a candidate for a
  new block. Never hand-roll a styled widget inline.
- `wireframe` is the exception to verbatim use: its `<style>` is pasted as-is, but its
  `<svg>` is drawn bespoke for the document, using only the block's primitive classes
  and the drawing rules in `references/demos.md`. Preserve every user-supplied UI label,
  value, action, and status as real SVG text; use skeleton bars only for unspecified
  content. Apply the rectangle-based layout and collision checks before inserting it.
- The same block may be pasted multiple times; it is scoped to its own root.

## Hard Rules

- **No CSS authorship.** Fill slots only; never add or edit `<style>` content, never
  use inline `style` attributes. If a visual pattern is missing, compose existing
  components or flag the gap in your reply.
- **Gate or it did not happen.** Never deliver while the gate reports errors.
- **Translate demos on insert.** Every visible string matches the document language.
- **Self-contained output.** No CDNs, webfonts, images by URL, or external anything.
- **No invented facts.** No fake metrics, dates, owners, quotes, or research. Unknown
  fields stay out of the meta table.
- **One file, one language.** A document is zh or en, never mixed prose. (Code and
  proper nouns excepted.)
- **Overwrite carefully.** If `<slug>.html` already exists, confirm before replacing it.

## Gotchas

| What happened | Rule |
|---|---|
| Gate says "unfilled @slot" | Search the file for `@slot`; fill or delete the marker |
| zh document has English button labels | Demo strings were not translated on insert; redo that slot |
| Demo works alone but breaks in the document | It was edited outside its contract; re-paste the block verbatim |
| User wants a component not in the catalog | Compose from callout/table/list, or flag as a new-block candidate; never improvise CSS |
| Description is one vague sentence | Proceed with explicit assumptions listed in the reply; do not stall unless a blocking fact is missing |
| Gate flags punctuation you consider correct | The gate owns mechanical rules; fix the text, do not argue the gate |

## Output

Deliver the file path plus: detected language, section list, demos inserted (name +
position), gate result, and any assumptions made. Keep it under eight lines.
