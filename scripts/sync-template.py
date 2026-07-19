#!/usr/bin/env python3
"""Sync the document template's base <style> block into generated documents.

templates/document.html is the only implementation of the design system, but
every generated document inlines its own copy of that <style> block. When the
template's styles change, run this script to rewrite the FIRST <style> block
of each target file (the document's base styles in <head>) with the
template's version. Prose, structure, and embedded demo blocks (which carry
their own scoped <style> later in <body>) are left untouched.

Usage:
    python3 scripts/sync-template.py [files...]

With no arguments, every examples/*.html file is synced. Embedded demo blocks
are translated on insert and still sync by hand; re-run the quality gate
(scripts/check.sh) after syncing.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "templates", "document.html")
DEFAULT_TARGETS = os.path.join(ROOT, "examples", "*.html")

# The base style block sits flush at column 0 in <head>; demo blocks carry
# their own indented <style> later in <body> and must stay untouched.
STYLE_RE = re.compile(r"^<style>$", re.MULTILINE)
STYLE_END_RE = re.compile(r"^</style>$", re.MULTILINE)


def style_span(text):
    """Return (start, end) of the first line-anchored <style> block, or None."""
    start = STYLE_RE.search(text)
    if start is None:
        return None
    end = STYLE_END_RE.search(text, start.end())
    if end is None:
        return None
    return start.start(), end.end()


def main(argv):
    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()
    span = style_span(template)
    if span is None:
        print("sync-template: no <style> block in " + TEMPLATE, file=sys.stderr)
        return 1
    base_style = template[span[0]:span[1]]

    targets = argv[1:] or sorted(glob.glob(DEFAULT_TARGETS))
    if not targets:
        print("sync-template: no target files found", file=sys.stderr)
        return 1

    status = 0
    for path in targets:
        with open(path, encoding="utf-8") as f:
            doc = f.read()
        span = style_span(doc)
        if span is None:
            print("skip (no <style> block): " + path)
            status = 1
            continue
        if doc[span[0]:span[1]] == base_style:
            print("in sync: " + path)
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc[:span[0]] + base_style + doc[span[1]:])
        print("updated: " + path)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
