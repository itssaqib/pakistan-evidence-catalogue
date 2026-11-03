# -*- coding: utf-8 -*-
"""Page shell: head, header with menu and search overlays, footer, scripts."""
import json, html as _html

SITE_NAME = "Pakistan Evidence Catalogue"
SITE_URL = "https://itssaqib.github.io/pakistan-evidence-catalogue/"
AUTHOR = "Saqib Hussain"
AUTHOR_URL = "https://itssaqib.github.io"
CONTACT = "saqibhussain@kdis.ac.kr"
REPO = "https://github.com/itssaqib/pakistan-evidence-catalogue"
VERSION = "2.0.0"
RELEASED = "4 November 2026"

NAV = [("programmes/index.html", "Programmes", "browse"), ("atlas/index.html", "Atlas", "atlas"),
       ("insights/index.html", "Insights", "insights"), ("datasets/index.html", "Datasets", "datasets"),
       ("toolkit/index.html", "Toolkit", "toolkit"), ("guide/index.html", "Guide", "guide"),
       ("about/index.html", "About", "about")]


def esc(s):
    return _html.escape(str(s if s is not None else ""), quote=True)


ICON = {
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18"/></svg>',
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>',
    "star": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/></svg>',
    "down": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>',
    "left": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    "right": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
    "play": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4l13 8-13 8z"/></svg>',
    "grid": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="6.5" height="6.5"/><rect x="13.5" y="4" width="6.5" height="6.5"/><rect x="4" y="13.5" width="6.5" height="6.5"/><rect x="13.5" y="13.5" width="6.5" height="6.5"/></svg>',
    "list": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
    "chev": '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4"/></svg>',
    "gh": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0-2.8 17.5c.4.1.6-.2.6-.4v-1.6c-2.5.5-3-1.1-3-1.1-.4-1-1-1.3-1-1.3-.8-.6.1-.6.1-.6.9.1 1.4.9 1.4.9.8 1.4 2.1 1 2.6.8.1-.6.3-1 .6-1.2-2-.2-4.1-1-4.1-4.5 0-1 .4-1.8.9-2.4-.1-.2-.4-1.2.1-2.4 0 0 .8-.2 2.5.9a8.6 8.6 0 0 1 4.5 0c1.7-1.1 2.5-.9 2.5-.9.5 1.2.2 2.2.1 2.4.6.6.9 1.4.9 2.4 0 3.5-2.1 4.3-4.1 4.5.3.3.6.8.6 1.6v2.4c0 .2.2.5.6.4A9 9 0 0 0 12 3z"/></svg>',
}


def tile(p, base, size="", badge=True):
    """A map tile; the canvas is drawn by map.js when it scrolls into view."""
    span = (f"{p['start_y']}–{str(p['end_y'])[2:]}" if p["start_y"] and p["end_y"] and p["end_y"] != p["start_y"]
            else (str(p["start_y"]) if p["start_y"] else "Continuous"))
    flag = '<span class="tile-flag">Districts documented</span>' if p["footprint"] else ""
    return (f'<a class="tile {size}" href="{base}programmes/{p["slug"]}.html" data-pid="{p["id"]}" '
            f'data-macro="{esc(p["macro"])}">'
            f'<div class="tile-media"><canvas aria-hidden="true"></canvas>'
            f'<span class="tile-id">{p["id"]}</span>{flag}'
            + (f'<span class="tile-badge">{span}</span>' if badge else "") +
            f'<button class="tile-star" type="button" data-star="{p["id"]}" aria-pressed="false" aria-label="Save {p["id"]} to shortlist">{ICON["star"]}</button>'
            f'</div><div class="tile-title">{esc(p["short"])}</div></a>')


def rail(tiles_html, label):
    return (f'<div class="rail-wrap"><button class="rail-arrow" data-dir="-1" type="button" aria-label="Scroll {esc(label)} left">{ICON["left"]}</button>'
            f'<div class="rail" role="list" aria-label="{esc(label)}">{tiles_html}</div>'
            f'<button class="rail-arrow" data-dir="1" type="button" aria-label="Scroll {esc(label)} right">{ICON["right"]}</button></div>')


def page(body, *, title, desc, base="", active="", page_id="", extra_body_attrs="", scripts=("core",),
         og_image="assets/og/home.jpg", canonical="", jsonld=None):
    nav = "".join(f'<a href="{base}{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>'
                  for href, label, key in NAV)
    full_title = f"{title} | {SITE_NAME}" if title != SITE_NAME else SITE_NAME
    src = {"catalogue": f'<script src="{base}data/catalogue.js"></script>',
           "geo": f'<script src="{base}data/geo.js"></script>',
           "core": f'<script src="{base}assets/js/core.js"></script>',
           "map": f'<script src="{base}assets/js/map.js"></script>',
           "charts": f'<script src="{base}assets/js/charts.js"></script>',
           "pages": f'<script src="{base}assets/js/pages.js"></script>'}
    order = ["catalogue", "geo", "core", "map", "charts", "pages"]
    want = set(scripts) | {"catalogue", "core", "pages"}
    script_tags = "\n".join(src[k] for k in order if k in want)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#ffffff">
<link rel="canonical" href="{SITE_URL}{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE_URL}{og_image}">
<meta property="og:url" content="{SITE_URL}{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23212934'/%3E%3Cpath d='M9 23V9h6.5a4.5 4.5 0 0 1 0 9H9' fill='none' stroke='%23c9a16e' stroke-width='2.4'/%3E%3C/svg%3E">
<link rel="preload" href="{base}assets/fonts/jost-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}assets/css/site.css">
{ld}
</head>
<body data-base="{base}" data-page="{page_id}" {extra_body_attrs}>
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="hdr-top wrap">
    <div class="hdr-left"><button class="icon-btn" type="button" data-open="menu" aria-label="Open menu" aria-controls="menu">{ICON["menu"]}</button></div>
    <a class="wordmark" href="{base}index.html" aria-label="{SITE_NAME}, home"><span class="wm-main">Pakistan Evidence</span><span class="wm-sub">Catalogue</span></a>
    <div class="hdr-right">
      <button class="icon-btn" type="button" data-open="search" aria-label="Search (press /)" aria-controls="search">{ICON["search"]}</button>
      <a class="icon-btn" href="{base}shortlist/index.html" aria-label="Your shortlist">{ICON["star"]}<span class="count" data-shortlist-count></span></a>
      <a class="icon-btn hide-sm" href="{base}toolkit/index.html#downloads" aria-label="Downloads">{ICON["down"]}</a>
    </div>
  </div>
  <nav class="hdr-nav" aria-label="Main">{nav}</nav>
</header>

<div class="overlay" id="menu" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="wrap">
    <div class="overlay-top"><button class="icon-btn" type="button" data-close aria-label="Close menu">{ICON["close"]}</button>
      <span class="wordmark"><span class="wm-main">Pakistan Evidence</span></span><span style="width:40px"></span></div>
    <div class="menu-grid">
      <nav class="menu-main" aria-label="Sections">
        <a href="{base}index.html">Home</a>
        {"".join(f'<a href="{base}{h}">{l}</a>' for h, l, _ in NAV)}
        <a href="{base}contribute/index.html">Contribute</a>
      </nav>
      <div class="menu-col">
        <h4>Start here</h4>
        <a href="{base}programmes/index.html?tq=High">Programmes with reliable rollout dates</a>
        <a href="{base}programmes/index.html?tq=High&amp;evidence=Unstudied">Reliable dates, no causal study yet</a>
        <a href="{base}programmes/index.html?map=Documented%20districts">Programmes with documented districts</a>
        <a href="{base}atlas/index.html">District atlas</a>
        <a href="{base}guide/index.html">Identification playbook</a>
        <a href="{base}guide/caveats.html">Standing caveats</a>
      </div>
      <div class="menu-col">
        <h4>Data and code</h4>
        <a href="{base}toolkit/index.html#downloads">Downloads: CSV, JSON, Stata</a>
        <a href="{base}toolkit/index.html#crosswalk">District crosswalk</a>
        <a href="{base}toolkit/index.html#stata">Stata starter kit</a>
        <a href="{base}toolkit/index.html#power">Power calculator</a>
        <a href="{base}data/references.bib">References (BibTeX)</a>
        <a href="{REPO}">Repository on GitHub</a>
      </div>
    </div>
  </div>
</div>

<div class="overlay" id="search" role="dialog" aria-modal="true" aria-label="Search">
  <div class="wrap">
    <div class="overlay-top"><span class="small muted">Search programmes, outcomes, datasets and pages</span>
      <button class="icon-btn" type="button" data-close aria-label="Close search">{ICON["close"]}</button></div>
    <div class="search-box">
      <label class="sr-only" for="search-input">Search the catalogue</label>
      <input class="search-input" id="search-input" type="search" placeholder="Search the catalogue" autocomplete="off">
      <p class="search-hint">Try a programme (Sehat), an outcome (stunting), a dataset (ASER) or an ID (P15). Arrow keys move, Enter opens.</p>
    </div>
    <ul class="search-results" id="search-results" aria-live="polite"></ul>
  </div>
</div>

<main id="main">
{body}
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="f-wordmark">Pakistan Evidence Catalogue</div>
    <ul class="f-links">
      <li><a href="{base}programmes/index.html">Programmes</a></li><li><a href="{base}atlas/index.html">Atlas</a></li>
      <li><a href="{base}insights/index.html">Insights</a></li><li><a href="{base}datasets/index.html">Datasets</a></li>
      <li><a href="{base}toolkit/index.html">Toolkit</a></li><li><a href="{base}guide/index.html">Guide</a></li>
      <li><a href="{base}contribute/index.html">Contribute</a></li><li><a href="{base}about/index.html">About</a></li>
      <li><a href="{REPO}">GitHub</a></li>
    </ul>
    <p class="f-meta">Compiled by <a href="{AUTHOR_URL}">{AUTHOR}</a>. Released under CC BY 4.0. Version {VERSION}, {RELEASED}.
    Suggested citation: Hussain, S. (2026). <em>Pakistan Evidence Catalogue: staggered district-level programmes for causal impact evaluation</em>, version {VERSION}.<br>
    District boundaries from geoBoundaries (2019, public domain). Boundaries shown do not imply any judgment on the legal status of any territory; the status of Jammu and Kashmir is disputed.
    Verify every date against the primary source named on each programme page before using it.</p>
  </div>
</footer>
{script_tags}
</body>
</html>
"""
