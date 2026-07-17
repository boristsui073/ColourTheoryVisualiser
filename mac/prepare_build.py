#!/usr/bin/env python3
"""Prepare build sources for the Colour Mixer macOS app.

1. Copies the canonical HTML (never mutated in place) to
   mac/build_src/index.html.
2. Patches the Three.js CDN <script> tag to the local vendored file —
   exact-match, asserted to occur exactly once.
3. Downloads three.min.js from the mrdoob/three.js r128 tag and verifies
   its sha256 against a pinned hash before accepting it (supply-chain
   guard; hash computed and pinned 2026-07-17 from
   raw.githubusercontent.com/mrdoob/three.js/r128/build/three.min.js).

Usage: python3 mac/prepare_build.py <path-to-canonical-html>
Runs in CI (GitHub runner has network); requires only stdlib.
"""

import hashlib
import os
import shutil
import sys
import urllib.request

THREE_URL = (
    "https://raw.githubusercontent.com/mrdoob/three.js/r128/build/three.min.js"
)
THREE_SHA256 = "9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2"
THREE_SIZE = 603445  # bytes, informational cross-check

CDN_TAG = (
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/'
    'r128/three.min.js"></script>'
)
LOCAL_TAG = '<script src="three.min.js"></script>'


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} <canonical-html>")
    src_html = sys.argv[1]
    if not os.path.isfile(src_html):
        raise SystemExit(f"HTML source not found: {src_html}")

    here = os.path.dirname(os.path.abspath(__file__))
    build_src = os.path.join(here, "build_src")
    shutil.rmtree(build_src, ignore_errors=True)
    os.makedirs(build_src)

    # --- 1+2: copy and patch, with uniqueness assertion -------------------
    with open(src_html, encoding="utf-8") as f:
        html = f.read()
    n = html.count(CDN_TAG)
    assert n == 1, (
        f"CDN script tag found {n} times (expected exactly 1) — "
        "the canonical HTML has changed; update CDN_TAG in this script."
    )
    html = html.replace(CDN_TAG, LOCAL_TAG)
    out_html = os.path.join(build_src, "index.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"patched HTML -> {out_html} ({len(html)} bytes)")

    # --- 3: vendor three.min.js, hash-verified ----------------------------
    out_js = os.path.join(build_src, "three.min.js")
    with urllib.request.urlopen(THREE_URL) as r:
        data = r.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != THREE_SHA256:
        raise SystemExit(
            "three.min.js hash mismatch — refusing to bundle.\n"
            f"  expected {THREE_SHA256}\n  got      {digest}"
        )
    if len(data) != THREE_SIZE:
        print(f"note: size {len(data)} != recorded {THREE_SIZE} "
              "(hash matched, so content is identical; record is stale)")
    with open(out_js, "wb") as f:
        f.write(data)
    print(f"vendored three.min.js -> {out_js} (sha256 verified)")


if __name__ == "__main__":
    main()
