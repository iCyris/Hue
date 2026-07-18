# Hue Design System

The single source of truth for every visual decision in Hue documents. The AI never invents
styles: it fills `templates/document.html`, which implements this spec, and inserts demo
blocks from `templates/demos/`, which are built from these same tokens. If a needed pattern
is missing here, compose existing tokens and components — do not create new ones.

Hue is named after the hydrangea (绣球花): one plant, many quiet hues. The system mirrors
that — a warm paper canvas, a warm gray text ramp, and one living accent used sparingly.

## Ten invariants

1. **One accent.** Hydrangea blue (`--accent`) is the only chromatic color on the page,
   covering at most 5% of the surface. The single sanctioned second color is `--danger`,
   reserved for error states inside demos and warning callouts.
2. **Warm neutrals only.** Every gray leans warm (R ≥ G > B). Cool grays and pure blue-grays
   are forbidden. Page background is never pure white; body text is never pure black.
3. **Serif-led, two weights.** One serif family per document, at weights 400 and 500 only.
   `strong` renders at 500. No synthetic bold, no 700/900, no italic for emphasis in CJK text.
4. **Tokens or nothing.** All colors, font families, sizes, spacing, radii, shadows, and
   motion values come from the token table below. Raw hex colors and raw font stacks may
   appear only inside `:root` and `html[lang]` token-definition blocks; everywhere else
   references tokens via `var(--…)`.
5. **4px spacing grid.** Every margin, padding, and gap is a multiple of 4px, chosen from
   the spacing scale.
6. **Quiet depth.** Elevation is a 1px ring (`--border`) or one whisper shadow. No hard
   shadows, no gradients on surfaces, no glassmorphism.
7. **Reading measure.** Prose column is 680px; the page shell never exceeds 960px.
   Line length beats screen width.
8. **Line-height bands.** Headlines 1.1–1.35, reading text 1.5–1.65. Never below 1.05,
   never above 1.7.
9. **Motion is tokenized and optional.** Durations and easings come from motion tokens.
   Every animation and transition must be disabled under `prefers-reduced-motion`.
10. **Single file, self-contained.** Output HTML inlines all CSS and JS. No external
    fonts, scripts, stylesheets, images, or iframes. The font stacks degrade gracefully
    through system fonts.

## Color tokens

| Token | Value | Use |
|---|---|---|
| `--paper` | `#F7F5EE` | Page background |
| `--surface` | `#FDFCF9` | Cards, demo stages, lifted surfaces |
| `--sand` | `#EFEDE3` | Interactive surface (hover, pressed, selected fills) |
| `--ink` | `#1B1B18` | Primary text |
| `--ink-2` | `#4B4A44` | Secondary text |
| `--ink-3` | `#76756E` | Tertiary text, metadata, captions |
| `--border` | `#E8E5DA` | Hairlines, rings |
| `--border-soft` | `#EEECE2` | Dividers inside components |
| `--accent` | `#4E5FA0` | Links, focus rings, h2 bar, primary demo controls, tags |
| `--accent-strong` | `#3D4C85` | Link hover, pressed primary controls |
| `--accent-tint` | `#ECEFF7` | Accent surface (tag background, selected rows) |
| `--accent-tint-2` | `#DFE4F2` | Stronger accent surface (hover on tint) |
| `--accent-tint-3` | `#C9D1E9` | Accent borders on tinted surfaces |
| `--danger` | `#A5483D` | Error text/icons in demos, warning callout accent |
| `--danger-tint` | `#F6E9E6` | Error/warning surface |

Usage rules:

- `--accent` text on `--paper`/`--surface` measures ≈5.5:1 — safe for links and labels.
  Never set body prose in accent; accent is for wayfinding, not reading.
- Shadows use `rgba(27, 27, 24, …)` (derived from `--ink`), never raw black at high alpha.
- Focus visibility: `outline: 2px solid var(--accent); outline-offset: 2px;` — restyle
  focus, never remove it.

## Typography

### Font stacks (token definitions, verbatim)

```css
:root {
  --serif: Charter, "Bitstream Charter", Georgia, "TsangerJinKai02",
           "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", serif;
  --mono: "JetBrains Mono", "SF Mono", Consolas, "TsangerJinKai02",
          "Source Han Serif SC", monospace;
}
html[lang^="zh"] {
  --serif: "TsangerJinKai02", "Source Han Serif SC", "Noto Serif CJK SC",
           "Songti SC", Georgia, serif;
}
```

- Any stack that may render CJK carries a CJK fallback — including `--mono`.
- Weights 400/500 only. `strong { font-weight: 500 }`, headings 500, body 400.
  Add `font-synthesis: none` so missing weights never get faux-bolded.
- The sans-serif is deliberately absent: serif carries both prose and UI in Hue.

### Type scale (screen, px)

| Role | Size / line-height | Weight | Notes |
|---|---|---|---|
| Display (doc title) | 34 / 1.15 | 500 | letter-spacing 0 (zh) / −0.3px (en) |
| H2 (section) | 20 / 1.3 | 500 | 2.5px accent left bar, 10px padding-left |
| H3 (subsection) | 17 / 1.35 | 500 | |
| Lead | 17 / 1.65 | 400 | `--ink-2`, under the title |
| Body | 15 / 1.65 | 400 | |
| Caption / metadata | 12.5 / 1.5 | 400 | `--ink-3` |
| Label / tag | 12.5 / 1.4 | 500 | |

- Body letter-spacing: zh `0.35px`, en `0`.
- Paragraph separation by `margin-bottom: 16px`, not by enlarged line-height.
- Numbers in tables, the meta line, and demos: `font-variant-numeric: tabular-nums`.
- Floors: never below 12px anywhere.

## Spacing, layout, radius, depth

- Spacing scale (px): `4 · 8 · 12 · 16 · 24 · 40 · 64` — exposed as `--s1…--s7`.
- Page shell: max-width 960px, padding `64px 24px`; prose column max-width 680px, centered.
- Section rhythm: `h2` blocks separated by `--s6` (40px) top margin; header block separated
  from body by a `--border` hairline plus `--s6`.
- Radius: `--r1: 6px` (tags, small controls) · `--r2: 8px` (cards, inputs, dialogs) ·
  `--r3: 12px` (demo stage, large surfaces).
- Depth, pick one per surface: `box-shadow: 0 0 0 1px var(--border)` (ring) or
  `0 1px 2px rgba(27,27,24,.04), 0 4px 24px rgba(27,27,24,.05)` (whisper).

## Document components

Implemented in `templates/document.html`; the AI selects and fills, never restyles.

- **Doc header**: eyebrow row (type tag + metadata in `--ink-3`, 12.5px), display title,
  lead paragraph, then a hairline. Optional meta line (status / owner / version / date):
  one horizontal row of label-value pairs below the lead — labels in `--ink-3`, values in
  `--ink` plain text, 12.5px, `tabular-nums`, 24px between fields, wrapping as needed.
  Values never use tag chips; the eyebrow tag is the header's only accent.
- **H2 section**: 2.5px `--accent` left bar. H3 is plain, no bar.
- **Prose**: `p`, `ul`/`ol` (markers in `--ink-3`), `blockquote` (2px `--border` left bar,
  `--ink-2`, no italic), `hr` (hairline).
- **Tags** (`.tag`): 12.5px/500, `--accent-tint` background, `--accent` text, `--r1`
  radius, 2px/8px padding. Solid token colors only.
- **Callouts** (`.callout`, `.callout--warn`): `--sand` (or `--danger-tint`) surface,
  `--r2`, 12px/16px padding, title row 500 weight. For notes, risks, decisions.
- **Tables** (`.table`): full-width within measure, hairline row borders, header row in
  `--ink-3` 12.5px labels, `tabular-nums`, 8px/12px cell padding.
- **Code**: inline `code` — `--mono` at 0.92em, `--sand` background, 4px radius.
  `pre` blocks — `--surface` + ring, `--mono` 13px/1.6, 16px padding, horizontal scroll.
- **Demo stage** (`figure.demo`): `--surface` card, ring, `--r3`, 24px padding; the demo
  block lives inside; optional `figcaption` in 12.5px `--ink-3` below. Demos are content,
  not decoration — one per idea being clarified.
- **Footer**: hairline, then 12.5px `--ink-3` line (generated-by, date, version).

## Motion

```css
:root {
  --dur-1: 120ms; --dur-2: 200ms; --dur-3: 320ms;
  --ease-out: cubic-bezier(.22, 1, .36, 1);
  --ease-spring: cubic-bezier(.5, 1.6, .4, 1);
}
```

- UI state changes (hover, focus, toggle): `--dur-1`–`--dur-2`, `--ease-out`.
- Entrances and spring demos: `--dur-3`, `--ease-spring`. Nothing exceeds 480ms.
- Animate `transform` and `opacity` only; never layout properties. Sanctioned
  exceptions: progress-fill `width`, accordion `grid-template-rows`.
- The global escape lives in the document template, not in demo blocks:
  `@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }`
  Demos must never re-enable motion; ambient loops simply stop. Explicitly user-triggered
  motion whose entire subject is motion (e.g. the spring comparison) may still play.

## Per-language adjustments

| Rule | en | zh |
|---|---|---|
| `--serif` stack | Charter-led | TsangerJinKai02-led (see stacks above) |
| Body letter-spacing | 0 | 0.35px |
| Display letter-spacing | −0.3px | 0 |
| Emphasis | `strong` at 500 | `strong` at 500; never italic |
| Punctuation | curly quotes, no em-dash (use commas/parentheses/colons) | full-width, no em-dash; one half-width space between CJK and Latin/digits |

## Anti-patterns (hard failures)

- Raw hex or `font-family` outside token-definition blocks; new tokens invented inline.
- Pure white page, pure black text, cool gray, gradients on surfaces, glassmorphism,
  heavy drop shadows.
- Font weights above 500, synthetic bold, italic CJK.
- Emoji as UI icons; icon fonts; external assets of any kind.
- Accent everywhere: colored headings, tinted paragraphs, more than one accent per screen.
- Demos that restyle the page, leak global CSS/JS, or depend on network.
- Animation on layout properties; motion without a reduced-motion escape.
