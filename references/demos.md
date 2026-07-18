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

## Toggle sizing rules

The toggle is an inline settings control, not a hero object. Keep the visible track at
36×20px with a 12px knob inset by 4px. Preserve a forgiving click target with an invisible
44×44px pseudo-element rather than enlarging the painted control. Setting rows use 8px
vertical padding and a 12px text-to-control gap. The knob gets a hairline and one small
shadow only; large ambient shadows make the control look inflated. Track color, ring,
opacity, and knob position transition with the motion tokens.

## Wireframe drawing rules

`wireframe` is the static exception: it shows what an interface looks like, so it has no
script and no interaction. The block's `<style>` is pasted verbatim; the `<svg>` markup
inside is drawn bespoke for each document, using only the primitive classes it defines:

- `.wf-frame` — outer containers: `--surface` fill, 1px `--border` stroke.
- `.wf-block` — substantial unspecified regions such as media and panels: `--sand` fill.
- `.wf-block-soft` — quiet structural placeholders: `--border-soft` fill.
- `.wf-card` — compact rows or cards: `--surface` fill with a `--border` stroke.
- `.wf-control` — explicit controls: `--surface` fill with a `--border-strong` stroke.
- `.wf-line`, `.wf-line-soft` — text stand-ins: rounded bars in `--border` /
  `--border-soft`, used only where the source leaves content unspecified.
- `.wf-copy`, `.wf-copy-strong`, `.wf-copy-muted` — real interface copy in the document
  language, set in `--serif` at the document's quiet ink levels. Preserve wording the
  user supplied, including labels, values, actions, statuses, and short explanatory text.
  Do not replace known copy with anonymous bars.
- `.wf-accent` — the single element being discussed: `--accent-tint` fill with
  `--accent-tint-3` stroke. At most one per drawing.
- `.wf-label` — region names in `--mono` 12px caps, `--ink-3`, below the regions.

Drawing discipline: `viewBox` only (no fixed pixel size, the canvas scales to the stage);
corner radii 4-8px; strokes 1px; no ids, gradients, filters, or images; label strings are
placeholders in English and get translated on insert like any other visible string.

### Wireframe layout algorithm

Treat every shape and text run as a rectangle before writing SVG. Use this sequence so
the finished drawing does not depend on visual guesswork:

1. **Partition first.** Reserve the outer frame, a 16px inner gutter, and a dedicated
   28-36px label band when region labels sit below content. Divide the remaining content
   area into non-overlapping regions before placing children.
2. **Place known copy before placeholders.** Estimate each single-line text box as
   `characters × font-size × 0.62` for Latin and `characters × font-size` for CJK, then
   add at least 8px clearance on every side. Wrap user-supplied copy into explicit
   `<tspan>` lines when it exceeds the region width. Skeleton bars fill only the space
   left after those boxes are placed.
3. **Check rectangle intersections.** Expand every text box by 4px and every shape box by
   2px. Two expanded boxes may not intersect unless the text intentionally belongs inside
   that shape. Labels, highlights, and content blocks are separate collision groups.
4. **Resolve in a fixed order.** On collision, first move the later item on the dominant
   flow axis, then shorten an unspecified skeleton bar, then wrap known copy, then enlarge
   the `viewBox`. Never cover, clip, shrink below 12px, or silently delete user-supplied
   text to make the drawing fit.
5. **Run boundary checks.** Every expanded box must remain inside its assigned region and
   above the label band. Keep at least 8px between sibling blocks and at least 12px between
   real copy and an unrelated block edge.

The result may mix literal UI copy, subdued structural blocks, and text stand-ins. Fidelity
follows the input: explicit areas are drawn with real labels and suitable Hue styling;
unspecified areas remain schematic.

Color blocks must express hierarchy instead of repeating one card shape. Compact rows and
controls are normally 24-36px high with 4px corner radii; selected rows may reach 44px and
use 6px corners; 48-96px filled areas are reserved for media, previews, or genuinely large
content regions. Vary width and height according to content, and do not stack three or more
identical filled rectangles when bordered rows or real copy can express the structure more
precisely.

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
