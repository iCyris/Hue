#!/usr/bin/env python3
"""Embed an image file into a Hue document's image demo block as base64.

The image demo block (templates/demos/image.html) ships with a small sample
image. When the user supplies a screenshot or mockup, this script swaps it in:
it finds the Nth <section data-demo="image"> block in the document and rewrites
the src of its .thumb <img> with a data: URI built from the image file. The
lightbox copies that src at runtime, so one replacement covers both views.

The base64 payload is written straight into the document and never printed,
so it stays out of the agent's context. Do not paste base64 by hand.

Usage:
    python3 scripts/embed-image.py <image> <document.html> [--block N] [--alt "text"]

    --block N   target the Nth image demo block (1-based, default 1)
    --alt TEXT  also rewrite the thumbnail's alt text (default: keep as-is)
"""
import argparse
import base64
import re
import sys

BLOCK_RE = re.compile(r'<section data-demo="image">')
THUMB_RE = re.compile(r'<img class="thumb"[^>]*>')
SRC_RE = re.compile(r'src="[^"]*"')
ALT_RE = re.compile(r'alt="[^"]*"')

# magic bytes -> (mime, label)
SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "image/png", "PNG"),
    (b"\xff\xd8\xff", "image/jpeg", "JPEG"),
    (b"GIF87a", "image/gif", "GIF"),
    (b"GIF89a", "image/gif", "GIF"),
)

WARN_BYTES = 512 * 1024


def sniff(data):
    for magic, mime, label in SIGNATURES:
        if data.startswith(magic):
            return mime, label
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp", "WebP"
    return None, None


def main():
    ap = argparse.ArgumentParser(description="Embed an image into a Hue image demo block.")
    ap.add_argument("image", help="image file to embed (PNG, JPEG, GIF, WebP)")
    ap.add_argument("document", help="the generated Hue document to modify in place")
    ap.add_argument("--block", type=int, default=1, help="1-based index of the image block (default 1)")
    ap.add_argument("--alt", default=None, help="replacement alt text for the thumbnail")
    args = ap.parse_args()

    try:
        with open(args.image, "rb") as f:
            data = f.read()
    except OSError as exc:
        print("embed-image: cannot read %s: %s" % (args.image, exc), file=sys.stderr)
        return 1
    mime, label = sniff(data)
    if mime is None:
        print("embed-image: %s is not a PNG, JPEG, GIF, or WebP image" % args.image, file=sys.stderr)
        return 1
    if len(data) > WARN_BYTES:
        print("embed-image: warning: %s is %.0f KB; it is embedded as-is (lossless), so the document grows with it"
              % (args.image, len(data) / 1024), file=sys.stderr)

    try:
        with open(args.document, encoding="utf-8") as f:
            doc = f.read()
    except OSError as exc:
        print("embed-image: cannot read %s: %s" % (args.document, exc), file=sys.stderr)
        return 1

    blocks = list(BLOCK_RE.finditer(doc))
    if not blocks:
        print("embed-image: no <section data-demo=\"image\"> block in %s; paste templates/demos/image.html first"
              % args.document, file=sys.stderr)
        return 1
    if not 1 <= args.block <= len(blocks):
        print("embed-image: --block %d out of range; %s has %d image block(s)"
              % (args.block, args.document, len(blocks)), file=sys.stderr)
        return 1

    start = blocks[args.block - 1].start()
    thumb = THUMB_RE.search(doc, start)
    if thumb is None:
        print("embed-image: no .thumb <img> found inside image block %d" % args.block, file=sys.stderr)
        return 1

    tag = thumb.group(0)
    uri = "data:%s;base64,%s" % (mime, base64.b64encode(data).decode("ascii"))
    tag = SRC_RE.sub('src="%s"' % uri, tag, count=1)
    if args.alt is not None:
        if '"' in args.alt:
            print("embed-image: --alt must not contain double quotes", file=sys.stderr)
            return 1
        tag = ALT_RE.sub('alt="%s"' % args.alt, tag, count=1)

    doc = doc[:thumb.start()] + tag + doc[thumb.end():]
    with open(args.document, "w", encoding="utf-8") as f:
        f.write(doc)

    print("embed-image: embedded %s (%.0f KB) into image block %d of %s"
          % (label, len(data) / 1024, args.block, args.document))
    return 0


if __name__ == "__main__":
    sys.exit(main())
