# -*- coding: utf-8 -*-
"""Shared layout chrome for the Pakistan Evidence Catalogue."""

SITE = "Pakistan Evidence Catalogue"
TAGLINE = "Staggered district-level programmes for causal impact evaluation"
VERSION = "1.0.0"
RELEASED = "2 November 2026"
AUTHOR = "Saqib Hussain"
AUTHOR_URL = "https://itssaqib.github.io"
CONTACT = "saqibhussain@kdis.ac.kr"
REPO = "https://github.com/itssaqib/pakistan-evidence-catalogue"

NAV = [
    ("programmes/", "Programmes"),
    ("matrix/", "Outcome matrix"),
    ("datasets/", "Datasets"),
    ("methods/", "Methods"),
    ("data/", "Download"),
    ("contribute/", "Contribute"),
]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def page(body, title, desc, base="", active="", extra_js="", wide=False):
    nav_html = ""
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        nav_html += f'<a href="{base}{href}"{cur}>{label}</a>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &middot; {SITE}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{AUTHOR}">
<meta property="og:title" content="{esc(title)} — {SITE}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%230B1B2E'/%3E%3Crect x='6' y='18' width='4' height='8' fill='%23fff'/%3E%3Crect x='12' y='13' width='4' height='13' fill='%23fff'/%3E%3Crect x='18' y='9' width='4' height='17' fill='%23B2432F'/%3E%3Crect x='24' y='6' width='2' height='20' fill='%23fff'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Public+Sans:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/css/main.css">
</head>
<body data-base="{base}">
<a class="skip" href="#main">Skip to content</a>

<div class="utility">
  <div class="wrap shell">
    <span>{TAGLINE}</span>
    <nav aria-label="Utility">
      <a href="{base}about/">About</a>
      <a href="{base}data/">Data</a>
      <a href="{base}contribute/">Contribute</a>
    </nav>
  </div>
</div>

<header class="masthead">
  <div class="wrap shell">
    <a class="wordmark" href="{base}">
      <span class="mark">PEC</span>
      <span class="name">Pakistan Evidence Catalogue</span>
    </a>
    <button class="navtoggle" type="button" aria-expanded="false" aria-controls="mainnav">Menu</button>
    <nav class="mainnav" id="mainnav" aria-label="Main">{nav_html}</nav>
  </div>
</header>

<main id="main">
{body}
</main>

<footer class="sitefoot">
  <div class="wrap shell">
    <div class="cols">
      <div>
        <h4>Catalogue</h4>
        <ul>
          <li><a href="{base}programmes/">All programmes</a></li>
          <li><a href="{base}programmes/?quality_label=High">Ready to use</a></li>
          <li><a href="{base}matrix/">Outcome matrix</a></li>
          <li><a href="{base}outcomes/">Outcome taxonomy</a></li>
        </ul>
      </div>
      <div>
        <h4>Data</h4>
        <ul>
          <li><a href="{base}data/">Downloads</a></li>
          <li><a href="{base}data/programmes.csv">Programmes (CSV)</a></li>
          <li><a href="{base}data/programme_outcome_matrix.csv">Matrix (CSV)</a></li>
          <li><a href="{base}data/catalogue.json">Full catalogue (JSON)</a></li>
        </ul>
      </div>
      <div>
        <h4>Methods</h4>
        <ul>
          <li><a href="{base}methods/">Identification playbook</a></li>
          <li><a href="{base}methods/#estimators">Estimator choice</a></li>
          <li><a href="{base}timing/">Finding treatment dates</a></li>
          <li><a href="{base}caveats/">Standing caveats</a></li>
        </ul>
      </div>
      <div>
        <h4>About</h4>
        <ul>
          <li><a href="{base}about/">About the catalogue</a></li>
          <li><a href="{base}contribute/">Contribute or correct</a></li>
          <li><a href="mailto:{CONTACT}">Contact</a></li>
          <li><a href="{AUTHOR_URL}">{AUTHOR}</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">
      <p>Compiled and maintained by <a href="{AUTHOR_URL}">{AUTHOR}</a>. Released under a
      Creative Commons Attribution 4.0 licence &mdash; reuse freely with attribution.</p>
      <p><strong>Suggested citation:</strong> Hussain, S. ({RELEASED[-4:]}).
      <em>{SITE}: {TAGLINE.lower()}</em>. Version {VERSION}.</p>
      <p>Version {VERSION} &middot; released {RELEASED} &middot; every date and claim in this
      catalogue should be verified against the primary source named on the programme page
      before use.</p>
    </div>
  </div>
</footer>

<script src="{base}assets/js/site.js"></script>
{extra_js}
</body>
</html>
"""
