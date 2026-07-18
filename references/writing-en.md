# Writing Rules: English Requirement Documents

Loaded when the generated document is English. These rules govern prose quality; the gate
(`scripts/check.py`) enforces the mechanical subset. The goal: a document a busy teammate
reads once and understands completely.

## Voice

- Active voice, present tense for behavior: "the system shows an error", not "an error
  will be shown" or "the system should show". "Should" is for desired outcomes only,
  never for specified behavior.
- Describe what the user can observe: what they see, what they can click, what happens
  next. Internal aspirations ("the architecture must remain flexible") are not
  requirements.
- One idea per paragraph. If a sentence starts with "Moreover," it probably starts a
  new paragraph.
- One name per concept, used everywhere (user/member, order/record — pick one).

## Structure

- Title: concrete, ≤ 10 words, names the thing. NO: "Improving the Checkout Experience"
  OK: "Add real-time shipping tracking to the order page"
- Lead: two sentences max — what this requirement is, why it exists now.
- Sections follow the need: Background / Scope / Behavior / Interaction details /
  Edge cases / Acceptance criteria. No ceremonial sections (Introduction, Vision,
  Conclusion) invented to look complete.
- Acceptance criteria are testable — each verifiable as true or false.
  NO: "The page loads quickly"  OK: "List first paint under 2s on 4G with 100 rows"

## Banned patterns (deterministic)

AI-tone fingerprints in English. Never produce them; rewrite when editing.

1. **Throat-clearing openers**: "In today's fast-paced world", "It is worth noting that",
   "Interestingly", "At its core". Delete; the sentence works without them.
2. **Hype adjectives**: seamless, robust, cutting-edge, best-in-class, intuitive,
   powerful, elegant (as a product claim). State the behavior instead.
3. **Rule of three**: "fast, reliable, and secure" rhythm used for cadence rather than
   content. One precise claim beats three vague ones.
4. **False contrast**: "It's not just X, it's Y" as a rhetorical device.
5. **Summary sentences** that restate the paragraph at its end ("In summary, ...").
6. **Gerund stacking**: "enabling users to leverage...", "allowing for the utilization
   of...". Use the plain verb.
7. **Vague quantifiers**: various, numerous, a wide range of, several. Count or cut.
8. **Buzzword verbs**: leverage, empower, streamline, supercharge, unlock.

## Punctuation and format (gate-enforced subset marked ✓)

- No em-dash (—) or en-dash (–) anywhere. Use a comma, colon, or parentheses. ✓
- No double spaces. ✓
- Curly quotes for quoted text; straight quotes only in code.
- Numbers carry units and conditions: "under 2s on 4G", not "fast".
- List items are parallel in form and complete sentences without the lead-in.

## Demo captions

One sentence: what to try, or what the interaction proves. NO: "The demo below is very
intuitive." OK: "Drag the slider and watch the value and the submit state change."
