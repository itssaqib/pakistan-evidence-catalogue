#!/usr/bin/env python3
"""Verify every internal href and src in the site resolves to a real file.

Run from the site root:  python3 _build/linkcheck.py
Exits non-zero if anything is broken, so it works in CI too.
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ATTR = re.compile(r'(?:href|src)="([^"]+)"')
SKIP = ("http://", "https://", "mailto:", "#", "data:", "//", "javascript:")

broken = []
checked = 0
pages = [p for p in glob.glob("**/*.html", recursive=True)
         if not p.startswith("_build" + os.sep)]

for page in pages:
    with open(page, encoding="utf-8") as fh:
        html = fh.read()
    here = os.path.dirname(page)

    for raw in ATTR.findall(html):
        if raw.startswith(SKIP):
            continue
        # Strip the fragment and query string.
        path = raw.split("#")[0].split("?")[0]
        if not path:
            continue
        # JavaScript string concatenation inside inline <script> blocks, not a real link.
        if "'" in raw or "+" in raw or "${" in raw:
            continue
        # 404.html uses absolute paths that only resolve once deployed.
        if page == "404.html" and path.startswith("/"):
            continue

        target = path.lstrip("/") if path.startswith("/") else os.path.join(here, path)
        target = os.path.normpath(target)
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")

        checked += 1
        if not os.path.exists(target):
            broken.append((page, raw))

print(f"Scanned {len(pages)} pages, checked {checked} internal links.")

if broken:
    print(f"\n{len(broken)} broken:\n")
    for page, link in broken:
        print(f"  {page}  ->  {link}")
    sys.exit(1)

print("No broken internal links.")

# Files the pages load or link to from JavaScript, which the regex above misses.
needed = ["data/catalogue.js", "data/geo.js", "data/catalogue.json", "assets/js/core.js", "assets/js/map.js",
          "assets/js/charts.js", "assets/js/pages.js", "assets/fonts/jost-latin-wght-normal.woff2",
          "assets/og/home.jpg"] + [f"assets/og/p{i:02d}.jpg" for i in range(1, 68)]
missing = [f for f in needed if not os.path.exists(f)]
if missing:
    print("\nWARNING: data files fetched by the pages are missing:")
    for f in missing:
        print(f"  {f}")
    sys.exit(1)
print(f"All {len(needed)} runtime files present.")
