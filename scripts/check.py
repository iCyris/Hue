#!/usr/bin/env python3
"""Hue quality gate. Stdlib only; no third-party imports.

Checks a generated Hue document against the contracts that are mechanical enough
to enforce without judgment:

  structure    doctype, <html lang>, charset, viewport, non-empty <title>,
               no leftover @slot markers
  containment  no external resources (script/link/img/iframe/video/audio/source,
               CSS url()/@import), no inline style attributes
  tokens       hex colors and font-family declarations only inside :root or
               html[lang] token-definition blocks
  language     zh: no half-width punctuation next to CJK, no em/en dash,
               one space between CJK and Latin/digits
               en: no em/en dash, no double spaces
               (--fix rewrites only the unambiguous zh spacing cases)
  demos        every [data-demo] block: its <style> selectors are scoped to
               [data-demo="name"], its @keyframes names are prefixed with the
               demo name, its <script> uses document.currentScript scoping,
               and no id is duplicated anywhere in the document

Usage: check.py [--lang zh|en|auto] [--fix] file.html [file.html ...]
Exit code 1 when any file reports an error. Aesthetic judgment stays with the
model and references/design-system.md; this script owns mechanical checks only.
"""

import argparse
import re
import sys
from html.parser import HTMLParser

CJK = r"㐀-䶿一-鿿豈-﫿"
CJK_RE = "[" + CJK + "]"
LATIN_RE = r"[A-Za-z0-9]"
DASHES = ["—", "–"]  # em dash, en dash

HALFWIDTH = '「,.;:!?()」'[1:-1]  # , . ; : ! ? ( )
HALFWIDTH_RE = "[" + re.escape(",.;:!?()") + "]"

RESOURCE_TAGS = ("img", "iframe", "video", "audio", "source", "embed", "object")


class Doc:
    def __init__(self, path, text):
        self.path = path
        self.text = text
        self.errors = []   # (line, rule, message)
        self.lang = "en"
        self.title_text = ""
        self._title_depth = 0
        self.has_doctype = False
        self.has_charset = False
        self.has_viewport = False
        self.html_lang = None
        self.ids = {}      # id -> first line
        self.styles = []   # (line, css_text, demo_name or None)
        self.scripts = []  # (line, js_text, demo_name or None)
        self.text_runs = []  # (line, text) prose nodes for language checks

    def error(self, line, rule, message):
        self.errors.append((line, rule, message))


class HueParser(HTMLParser):
    def __init__(self, doc):
        super().__init__(convert_charrefs=True)
        self.doc = doc
        self.stack = []            # tag names
        self.demo_stack = []       # data-demo names, parallel to open elements
        self.capture = None        # ("style"|"script"|"title", start_line, [chunks], demo)

    def _current_demo(self):
        return self.demo_stack[-1] if self.demo_stack else None

    def handle_decl(self, decl):
        if decl.strip().lower().startswith("doctype"):
            self.doc.has_doctype = True

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        line = self.getpos()[0]
        d = self.doc

        if tag == "html":
            d.html_lang = attrs.get("lang")
            if d.html_lang:
                d.lang = "zh" if d.html_lang.lower().startswith("zh") else "en"
        if tag == "meta":
            if attrs.get("charset") or "charset" in attrs.get("http-equiv", "").lower():
                d.has_charset = True
            if attrs.get("name", "").lower() == "viewport":
                d.has_viewport = True

        if attrs.get("style") is not None:
            d.error(line, "containment", "inline style attribute is forbidden; use token classes")

        if tag == "link" and attrs.get("href"):
            d.error(line, "containment", "external <link href> resource: %s" % attrs["href"][:60])
        if tag == "script" and attrs.get("src"):
            d.error(line, "containment", "external <script src>: %s" % attrs["src"][:60])
        if tag in RESOURCE_TAGS:
            for key in ("src", "data"):
                val = attrs.get(key)
                if val and not val.startswith("data:"):
                    d.error(line, "containment", "external resource <%s %s=...>: %s" % (tag, key, val[:60]))

        if "id" in attrs:
            if attrs["id"] in d.ids:
                d.error(line, "demos", 'duplicate id "%s" (first seen line %d)' % (attrs["id"], d.ids[attrs["id"]]))
            else:
                d.ids[attrs["id"]] = line

        demo = attrs.get("data-demo")
        self.demo_stack.append(demo if demo else self._current_demo())
        self.stack.append(tag)

        if tag in ("style", "script", "title"):
            self.capture = (tag, line, [], self._current_demo())

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.capture and self.capture[0] == tag:
            kind, start_line, chunks, demo = self.capture
            body = "".join(chunks)
            if kind == "style":
                self.doc.styles.append((start_line, body, demo))
            elif kind == "script":
                self.doc.scripts.append((start_line, body, demo))
            else:
                self.doc.title_text = body.strip()
            self.capture = None
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
            self.demo_stack.pop()

    def handle_data(self, data):
        if self.capture:
            self.capture[2].append(data)
            return
        if any(t in ("code", "pre") for t in self.stack):
            return
        if data.strip():
            self.doc.text_runs.append((self.getpos()[0], data))


# --- CSS -----------------------------------------------------------------

def strip_css_comments(css):
    """Remove /* ... */ comments, preserving newlines so line numbers stay accurate."""
    return re.sub(r"/\*.*?\*/",
                  lambda m: "\n" * m.group(0).count("\n"),
                  css, flags=re.S)


def iter_css_blocks(css, base_line):
    """Yield (selector_stack, declarations, line) for each leaf declaration block."""
    css = strip_css_comments(css)
    stack = []  # (name, line)
    i, n = 0, len(css)
    token_start = 0
    line = base_line

    def advance_line(fragment):
        nonlocal line
        line += fragment.count("\n")

    while i < n:
        ch = css[i]
        if ch == "{":
            name = css[token_start:i].strip()
            stack.append((name, line))
            advance_line(css[token_start:i + 1])
            i += 1
            token_start = i
        elif ch == "}":
            content = css[token_start:i]
            if stack:
                name, start_line = stack.pop()
                if "{" not in content:
                    yield ([s for s, _ in stack] + [name], content, start_line)
            advance_line(content + "}")
            i += 1
            token_start = i
        else:
            i += 1


HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
TOKEN_SELECTOR_RE = re.compile(r"^(:root|html\[lang)")
FONT_VAR_ONLY_RE = re.compile(r"^\s*var\(--[A-Za-z0-9-]+\)\s*$")


def check_css(doc):
    for start_line, css, demo in doc.styles:
        for stack, decls, line in iter_css_blocks(css, start_line):
            top = stack[0] if stack else ""
            innermost = stack[-1] if stack else ""
            if top.startswith("@keyframes"):
                continue
            in_token_block = bool(TOKEN_SELECTOR_RE.match(innermost))
            if HEX_RE.search(decls) and not in_token_block:
                bad = HEX_RE.search(decls).group(0)
                doc.error(line, "tokens",
                          "raw hex %s outside :root / html[lang] token blocks (selector: %s)"
                          % (bad, innermost[:40]))
            font_m = re.search(r"(?:^|;)\s*font-family\s*:\s*([^;]+)", decls)
            if font_m and not in_token_block and not FONT_VAR_ONLY_RE.match(font_m.group(1)):
                doc.error(line, "tokens",
                          "font-family outside token blocks (selector: %s); use var(--serif)/var(--mono)"
                          % innermost[:40])
            if demo:
                for sel in innermost.split(","):
                    sel = sel.strip()
                    if not sel.startswith('[data-demo="%s"]' % demo):
                        doc.error(line, "demos",
                                  'demo "%s" style selector not scoped: %s' % (demo, sel[:50]))
        if demo:
            for m in re.finditer(r"@keyframes\s+([A-Za-z0-9_-]+)", css):
                if not m.group(1).startswith(demo + "-"):
                    doc.error(start_line + css[:m.start()].count("\n"), "demos",
                              '@keyframes "%s" must be prefixed "%s-"' % (m.group(1), demo))
            if re.search(r"@(import|font-face)\b", css):
                doc.error(start_line, "containment", "@import/@font-face are forbidden in demos")
        if re.search(r"@import\b", css):
            doc.error(start_line, "containment", "@import is forbidden")
        for m in re.finditer(r"url\(\s*['\"]?(?!data:)([^)'\"]+)", css):
            doc.error(start_line + css[:m.start()].count("\n"), "containment",
                      "external CSS url(): %s" % m.group(1)[:60])


def check_scripts(doc):
    for start_line, js, demo in doc.scripts:
        if demo and "currentScript" not in js:
            doc.error(start_line, "demos",
                      'demo "%s" script must scope via document.currentScript.closest(...)' % demo)


# --- language --------------------------------------------------------------

def check_language(doc):
    zh = doc.lang == "zh"
    runs = list(doc.text_runs)
    if doc.title_text:
        runs.append((1, doc.title_text))
    for line, text in runs:
        for dash in DASHES:
            idx = text.find(dash)
            if idx != -1:
                doc.error(line + text[:idx].count("\n"), "language",
                          "em/en dash is forbidden; use a comma, colon, or parentheses")
        if zh:
            for m in re.finditer(HALFWIDTH_RE, text):
                i = m.start()
                before = text[i - 1] if i > 0 else ""
                after = text[i + 1] if i + 1 < len(text) else ""
                if re.match(CJK_RE, before) or re.match(CJK_RE, after):
                    if re.match(LATIN_RE, before) and after in ".)":
                        continue  # decimals such as 3.5
                    doc.error(line + text[:i].count("\n"), "language",
                              "half-width '%s' next to CJK; use full-width punctuation" % m.group(0))
            m = re.search(CJK_RE + LATIN_RE + "|" + LATIN_RE + CJK_RE, text)
            if m:
                doc.error(line + text[:m.start()].count("\n"), "language",
                          "missing space between CJK and Latin/digits")
        else:
            idx = text.find("  ")
            if idx != -1:
                doc.error(line + text[:idx].count("\n"), "language", "double space")


def fix_zh_spacing(text):
    """Rewrite only zero-ambiguity cases outside <style>/<script> regions."""
    protected = re.compile(r"(<style.*?</style>|<script.*?</script>)", re.S)
    parts = protected.split(text)

    def fix(part):
        part = re.sub("(" + CJK_RE + ")(" + LATIN_RE + ")", r"\1 \2", part)
        part = re.sub("(" + LATIN_RE + ")(" + CJK_RE + ")", r"\1 \2", part)
        return part

    return "".join(fix(p) if i % 2 == 0 else p for i, p in enumerate(parts))


# --- driver ----------------------------------------------------------------

def check_file(path, forced_lang, fix):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if fix:
        text = fix_zh_spacing(text)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    doc = Doc(path, text)
    HueParser(doc).feed(text)

    fragment = not doc.has_doctype  # demo blocks are fragments; full documents are not
    if forced_lang != "auto":
        doc.lang = forced_lang
    if "@slot" in text:
        doc.error(1, "structure", "unfilled @slot marker remains in the document")
    if not fragment:
        if not doc.html_lang:
            doc.error(1, "structure", "missing <html lang=...>")
        if not doc.has_charset:
            doc.error(1, "structure", "missing <meta charset>")
        if not doc.has_viewport:
            doc.error(1, "structure", "missing viewport meta")
        if not doc.title_text:
            doc.error(1, "structure", "empty <title>")

    check_css(doc)
    check_scripts(doc)
    check_language(doc)

    for line, rule, message in sorted(doc.errors):
        print("%s:%d: [%s] %s" % (path, line, rule, message))
    if not doc.errors:
        print("%s: check: ok (lang=%s%s)" % (path, doc.lang, ", fragment" if fragment else ""))
    return not doc.errors


def main():
    ap = argparse.ArgumentParser(description="Hue quality gate")
    ap.add_argument("--lang", choices=["zh", "en", "auto"], default="auto")
    ap.add_argument("--fix", action="store_true", help="rewrite unambiguous zh spacing cases")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()
    ok = all(check_file(p, args.lang, args.fix) for p in args.files)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
