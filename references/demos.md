# Hue Demo System

Demos are interactive evidence embedded in the reading flow. A demo clarifies one idea —
a control's states, a flow's steps, a motion's feel. It is content, not decoration: insert
one where the reader would otherwise have to imagine behavior.

Every demo is a self-contained block stored as one file in `templates/demos/`. To use it,
paste the whole block inside `<figure class="demo">` in the document, add an optional
`<figcaption>`, and translate every visible string into the document's language.

## Block contract

```html
<section data-demo="name">
  <style>
    [data-demo="name"] .control { ... }        /* every selector scoped to the block */
    @keyframes name-enter { ... }              /* keyframes prefixed with the demo name */
  </style>
  <div class="stage">
    <!-- markup: classes only, never ids -->
  </div>
  <script>
    (function () {
      var root = document.currentScript.closest('[data-demo="name"]');
      /* query only inside root; no globals, no libraries */
    })();
  </script>
</section>
```

Hard rules (enforced by `scripts/check.py`):

- The root element is `<section data-demo="name">`; the file name equals the demo name.
- Every CSS selector starts with `[data-demo="name"]`. No global selectors, no `*`.
- `@keyframes` names start with the demo name (`name-enter`, not `enter`).
- Colors come from `var(--…)` tokens only; raw hex is rejected. Fonts use
  `var(--serif)` / `var(--mono)` only. Spacing, radius, duration, and easing values
  come from the token scales in `references/design-system.md`.
- Scripts are IIFEs that locate their root via `document.currentScript.closest(...)`
  and never touch the document outside that root. The same block can therefore be
  pasted twice in one document without breaking.
- No `id` attributes anywhere in the block. No inline `style` attributes in markup;
  dynamic visual state is set from JS via `el.style` or class toggling.
- No external assets, fonts, or libraries. Everything renders offline.
- No em-dash or en-dash in visible strings (gate-checked).

Quality bar (judgment, not gated):

- Real interaction, not a static picture: hover, focus, pressed, and disabled states
  where the control has them; keyboard operation for anything activatable
  (`<button>`, `role="switch"` with Space/Enter, arrow keys for tabs/slider).
  The one exception is `wireframe`, which is deliberately static (see below).
- Accessible by default: native elements first; `aria-*` where semantics are missing;
  visible focus via the document's `:focus-visible` rule.
- Motion uses `--dur-*` and `--ease-*` tokens, animates `transform`/`opacity` only,
  and is already disabled globally under `prefers-reduced-motion` — never re-enable it.
- Blocks assume they sit inside `figure.demo` (surface card provided by the template);
  they style their own controls but not the card itself.
- Visible strings are placeholders written in English; the assembling model translates
  them into the document language when inserting the block.

## Catalog

| File | Block | Use it when the requirement involves |
|---|---|---|
| `button-states.html` | Primary, secondary, and danger buttons with hover, pressed, disabled, and loading states | Actions, CTAs, destructive operations, async submits |
| `form-validation.html` | Text input with inline error and success on blur/submit | Input rules, error copy, field-level feedback |
| `toggle.html` | Switch with on/off state, keyboard operable | Settings, feature flags, enable/disable behavior |
| `slider.html` | Range slider with live value readout | Thresholds, ranges, tunable parameters |
| `segmented-control.html` | Mutually exclusive option switch | Modes, views, small enum choices |
| `tabs.html` | Tab bar switching panels, arrow-key navigation | Multi-view screens, categorized content |
| `accordion.html` | Expand/collapse stacked sections | Progressive disclosure, FAQ-like content, dense pages |
| `stepper.html` | Multi-step flow with previous/next and status | Onboarding, wizards, ordered processes |
| `dialog.html` | Modal with overlay, confirm/cancel, Esc and overlay-click close | Confirmations, destructive decisions, interruptions |
| `toast.html` | Trigger a transient message that auto-dismisses | Async results, non-blocking feedback |
| `progress.html` | Determinate progress bar animating to a target | Uploads, imports, long tasks |
| `skeleton.html` | Loading placeholder shimmer in a card layout | Perceived performance, loading states |
| `card-list.html` | List of cards with hover and selected state | Feeds, pick-one lists, collections |
| `spring-motion.html` | Same element animated with ease-out vs spring on click | Motion specs, transition feel, animation vocabulary |
| `wireframe.html` | Static SVG schematic of an interface layout; no interaction | Showing a screen's structure, region layout, or before/after arrangement |

## Wireframe drawing rules

`wireframe` is the static exception: it shows what an interface looks like, so it has no
script and no interaction. The block's `<style>` is pasted verbatim; the `<svg>` markup
inside is drawn bespoke for each document, using only the primitive classes it defines:

- `.wf-frame` — outer containers: `--surface` fill, 1px `--border` stroke.
- `.wf-block` — content regions (cards, media, panels): `--sand` fill.
- `.wf-line`, `.wf-line-soft` — text stand-ins: rounded bars in `--border` /
  `--border-soft`, never real body copy. `.wf-text` marks the one primary heading bar
  (`--ink-2`).
- `.wf-accent` — the single element being discussed: `--accent-tint` fill with
  `--accent-tint-3` stroke. At most one per drawing.
- `.wf-label` — region names in `--mono` 12px caps, `--ink-3`, below the regions.

Drawing discipline: `viewBox` only (no fixed pixel size, the canvas scales to the stage);
corner radii 4-8px; strokes 1px; no ids, gradients, filters, or images; label strings are
placeholders in English and get translated on insert like any other visible string.

## Adding a new demo

1. Pick a lowercase kebab-case name; create `templates/demos/<name>.html` following the
   contract above.
2. Run `bash scripts/check.sh templates/demos/<name>.html` — it must print `check: ok`.
3. Verify by hand: paste the block twice into a scratch document, confirm both instances
   work, and operate the control with keyboard only.
4. Add one row to the catalog table above. Keep it a table; do not add sections.

Gate subtleties worth knowing before you debug them the hard way:

- The double-space rule scans raw text nodes, including indentation whitespace — keep
  every element's text on a single line flush inside its tags.
- `font-family: inherit` is rejected; set `font-family: var(--serif)` explicitly on
  controls (they do not inherit the document font by default).
- `@media` blocks cannot appear inside demo styles (selectors would escape scoping);
  the document template owns `prefers-reduced-motion` globally.
