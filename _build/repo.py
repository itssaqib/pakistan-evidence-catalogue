# -*- coding: utf-8 -*-
"""Repository files: README, licence, citation metadata, sitemap, issue forms,
redirects from version 1 URLs, editor and publish tooling, and a copy of the
build scripts in _build/."""
import json, os, shutil, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(HERE)
IN_REPO = os.path.exists(os.path.join(_PARENT, "assets", "css", "site.css"))
SITE = _PARENT if IN_REPO else os.path.join(_PARENT, "out", "pakistan-evidence-catalogue")
V1 = "/home/claude/site/pakistan-evidence-catalogue"  # publish scripts carried over (only used when building outside the repo)
D = json.load(open(os.path.join(SITE, "data", "catalogue.json"), encoding="utf-8"))
META, C, P = D["meta"], D["meta"]["counts"], D["programmes"]
VERSION, URL, REPO = META["version"], "https://itssaqib.github.io/pakistan-evidence-catalogue/", "https://github.com/itssaqib/pakistan-evidence-catalogue"
TODAY = "2026-11-04"


def w(rel, text, mode="w"):
    path = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(path) or SITE, exist_ok=True)
    with open(path, mode, encoding="utf-8", newline="\n") as f:
        f.write(text)


# ----------------------------------------------------------------- sitemap
pages = ["", "programmes/index.html", "atlas/index.html", "insights/index.html", "datasets/index.html", "toolkit/index.html",
         "guide/index.html", "guide/timing.html", "guide/caveats.html", "about/index.html", "contribute/index.html"]
pages += [f"programmes/{p['slug']}.html" for p in P]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for pg in pages:
    pr = "1.0" if pg == "" else "0.8" if pg.startswith("programmes/p") else "0.9"
    sm.append(f"  <url><loc>{URL}{pg}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>")
sm.append("</urlset>")
w("sitemap.xml", "\n".join(sm) + "\n")
w("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /_build/\n\nSitemap: {URL}sitemap.xml\n")
w(".nojekyll", "")

# ----------------------------------------------------------------- redirects from v1 URLs
REDIR = {"matrix/index.html": "../insights/index.html#outcomes", "outcomes/index.html": "../insights/index.html#outcomes",
         "methods/index.html": "../guide/index.html", "timing/index.html": "../guide/timing.html",
         "caveats/index.html": "../guide/caveats.html", "data/index.html": "../toolkit/index.html#downloads"}
for src, dst in REDIR.items():
    w(src, f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>
<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={dst}">
<link rel="canonical" href="{URL}{dst.replace('../', '')}"></head>
<body><p>This page has moved to <a href="{dst}">a new address</a>.</p></body></html>
""")

# ----------------------------------------------------------------- licence and citation
w("LICENSE", f"""Creative Commons Attribution 4.0 International (CC BY 4.0)

Copyright (c) 2026 Saqib Hussain

You are free to share and adapt this material for any purpose, including
commercially, provided you give appropriate credit, link to the licence,
and indicate if changes were made.

Full licence text: https://creativecommons.org/licenses/by/4.0/legalcode

SUGGESTED ATTRIBUTION
Hussain, S. (2026). Pakistan Evidence Catalogue: staggered district-level
programmes for causal impact evaluation. Version {VERSION}.

THIRD-PARTY MATERIAL
- The catalogue licence covers the programme inventory, outcome taxonomy,
  dataset descriptions, documented footprints, crosswalk and the mapping
  between them. It does not cover the datasets described, each of which
  carries its own licence and access conditions.
- District boundaries: geoBoundaries gbOpen, Pakistan ADM2 (2019), public
  domain. Runfola et al. (2020), PLoS ONE 15(4): e0231866.
- Typeface: Jost, by Owen Earl (indestructible type*), SIL Open Font
  Licence 1.1. See assets/fonts/OFL-Jost.txt.
- Site code (HTML, CSS, JavaScript, Python, Stata) may also be reused under
  the MIT licence terms: permission is granted, free of charge, to use, copy,
  modify and distribute it, provided this notice is kept. It is provided
  "as is", without warranty of any kind.
""")

w("CITATION.cff", f"""cff-version: 1.2.0
message: "If you use this catalogue, please cite it as below."
title: "Pakistan Evidence Catalogue: staggered district-level programmes for causal impact evaluation"
abstract: >-
  An open catalogue of {C['programmes']} public programmes and natural experiments in Pakistan
  rolled out unit by unit over time at or below the district level, with {C['pairs']}
  programme-outcome pairs, {C['outcomes']} outcome definitions and {C['datasets']} datasets mapped
  against them, documented rollout districts for {C['footprints']} entries, and a district
  crosswalk on constant 2019 boundaries.
type: dataset
version: "{VERSION}"
date-released: "{TODAY}"
license: CC-BY-4.0
repository-code: "{REPO}"
url: "{URL}"
keywords:
  - Pakistan
  - difference-in-differences
  - staggered adoption
  - impact evaluation
  - causal inference
  - district panel
  - development economics
authors:
  - family-names: Hussain
    given-names: Saqib
    email: saqibhussain@kdis.ac.kr
    affiliation: "KDI School of Public Policy and Management"
""")

w(".zenodo.json", json.dumps({
    "title": "Pakistan Evidence Catalogue: staggered district-level programmes for causal impact evaluation",
    "upload_type": "dataset", "version": VERSION, "license": "cc-by-4.0", "access_right": "open",
    "description": (f"An open catalogue of {C['programmes']} public programmes and natural experiments in Pakistan that reached districts at "
                    f"different times, with rollout windows, assignment rules, sources for treatment timing graded by reliability, "
                    f"{C['pairs']} programme-outcome pairs mapped to {C['datasets']} datasets, documented rollout districts for "
                    f"{C['footprints']} entries, a district crosswalk on constant 2019 boundaries, and a Stata starter kit."),
    "creators": [{"name": "Hussain, Saqib", "affiliation": "KDI School of Public Policy and Management"}],
    "keywords": ["Pakistan", "difference-in-differences", "staggered adoption", "impact evaluation", "district panel"],
    "related_identifiers": [{"identifier": URL, "relation": "isDocumentedBy", "resource_type": "other"}],
}, indent=2) + "\n")

# ----------------------------------------------------------------- issue forms
ISS = ".github/ISSUE_TEMPLATE/"
w(ISS + "config.yml", f"""blank_issues_enabled: true
contact_links:
  - name: Email the maintainer
    url: mailto:saqibhussain@kdis.ac.kr
    about: For anything you would rather not post publicly.
  - name: Browse the catalogue
    url: {URL}
    about: Check whether an entry already exists before suggesting one.
""")
w(ISS + "claim.yml", """name: Claim an idea
description: Say you are working on an entry so others can coordinate. This does not reserve it.
title: "[Claim] Pxx "
labels: ["claim"]
body:
  - type: markdown
    attributes:
      value: |
        Claims are shown on the programme page while this issue is open. Close the issue to release the claim.
        Keep the title format `[Claim] P07 Zewar-e-Taleem` so the site can find it.
  - type: input
    id: pid
    attributes: {label: Programme ID, placeholder: P07}
    validations: {required: true}
  - type: input
    id: who
    attributes: {label: Name and affiliation, description: Shown publicly.}
    validations: {required: true}
  - type: dropdown
    id: stage
    attributes:
      label: Stage
      options: [Idea and data search, Building the rollout file, Estimating, Draft paper]
    validations: {required: true}
  - type: textarea
    id: plan
    attributes: {label: Outcome and design, description: One or two lines. Optional.}
  - type: checkboxes
    id: share
    attributes:
      label: Sharing
      options:
        - label: I am willing to share the rollout file here once the paper is out.
""")
w(ISS + "correction.yml", """name: Suggest a correction
description: A date, district, source or claim in an entry is wrong or out of date.
title: "[Correction] Pxx "
labels: ["correction"]
body:
  - type: input
    id: pid
    attributes: {label: Programme ID, placeholder: P33}
    validations: {required: true}
  - type: textarea
    id: wrong
    attributes: {label: What the catalogue says}
    validations: {required: true}
  - type: textarea
    id: right
    attributes: {label: What it should say}
    validations: {required: true}
  - type: textarea
    id: source
    attributes:
      label: Source
      description: A primary document is best (notification, annual report, project document, scheme register). Link or full citation.
    validations: {required: true}
""")
w(ISS + "new-programme.yml", """name: Suggest a programme
description: A programme or natural experiment that reached places at different times.
title: "[New] "
labels: ["new-programme"]
body:
  - type: input
    id: name
    attributes: {label: Programme name and agency}
    validations: {required: true}
  - type: textarea
    id: stagger
    attributes: {label: How it was staggered, description: Which units, in what order, over which years.}
    validations: {required: true}
  - type: textarea
    id: timing
    attributes: {label: Where the dates can be found, description: Register, report, gazette, dataset.}
    validations: {required: true}
  - type: textarea
    id: outcomes
    attributes: {label: Outcomes it could move, description: Optional.}
  - type: textarea
    id: refs
    attributes: {label: Existing evaluations, description: Optional.}
""")
w(ISS + "timing-file.yml", """name: Share a rollout file
description: A district- or tehsil-by-date treatment file for an entry.
title: "[Timing file] Pxx "
labels: ["timing-file"]
body:
  - type: input
    id: pid
    attributes: {label: Programme ID}
    validations: {required: true}
  - type: textarea
    id: file
    attributes:
      label: The file
      description: Drag a CSV here, or link to it. Columns we can use - unit name, province, treatment date, source for each row.
    validations: {required: true}
  - type: textarea
    id: method
    attributes: {label: How it was built, description: Sources and any judgement calls.}
    validations: {required: true}
  - type: input
    id: credit
    attributes: {label: Credit as, description: Name and affiliation to show on the programme page.}
    validations: {required: true}
  - type: checkboxes
    id: licence
    attributes:
      label: Licence
      options:
        - label: I agree to release this file under CC BY 4.0.
          required: true
""")

# ----------------------------------------------------------------- editor and publish tooling
w(".editorconfig", """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.{py,do}]
indent_size = 4

[*.md]
trim_trailing_whitespace = false
""")
w(".gitignore", """# OS cruft
.DS_Store
Thumbs.db
desktop.ini

# Editor
.vscode/*
!.vscode/tasks.json
!.vscode/settings.json
!.vscode/extensions.json
*.code-workspace
.idea/

# Build and dependency artefacts
node_modules/
__pycache__/
*.py[cod]
.venv/
venv/
paper/*.aux
paper/*.log
paper/*.out

# Local scratch
*.log
*.tmp
shot-*.png
""")
w(".vscode/settings.json", json.dumps({
    "files.eol": "\n", "files.trimTrailingWhitespace": True, "files.insertFinalNewline": True,
    "search.exclude": {"**/node_modules": True, "**/__pycache__": True, "data/catalogue.json": True, "data/catalogue.js": True, "data/geo.js": True},
    "liveServer.settings.root": "/", "liveServer.settings.port": 8000,
    "[html]": {"editor.formatOnSave": False}, "git.enableSmartCommit": True, "git.autofetch": True}, indent=2) + "\n")
w(".vscode/extensions.json", json.dumps({"recommendations": ["ritwickdey.liveserver", "github.vscode-pull-request-github", "editorconfig.editorconfig"]}, indent=2) + "\n")
REBUILD = "python3 geo.py && python3 data.py && python3 stata.py && python3 pages.py && python3 paper.py && python3 repo.py"
w(".vscode/tasks.json", """{
  // Run any of these with: Terminal -> Run Task...  (or Ctrl/Cmd+Shift+P -> "Run Task")
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Publish to GitHub",
      "detail": "Commit everything and push to origin/main. Prompts for a commit message.",
      "type": "shell",
      "command": "./publish.sh",
      "args": ["${input:commitMessage}"],
      "windows": {
        "command": "powershell",
        "args": ["-ExecutionPolicy", "Bypass", "-File", "${workspaceFolder}/publish.ps1", "${input:commitMessage}"]
      },
      "options": { "cwd": "${workspaceFolder}" },
      "problemMatcher": [],
      "presentation": { "reveal": "always", "panel": "dedicated", "clear": true },
      "group": { "kind": "build", "isDefault": true }
    },
    {
      "label": "Preview site locally",
      "detail": "Serve on http://localhost:8000. Opening index.html directly also works; the server matches GitHub Pages more closely.",
      "type": "shell",
      "command": "python3 -m http.server 8000",
      "windows": { "command": "python -m http.server 8000" },
      "options": { "cwd": "${workspaceFolder}" },
      "isBackground": true,
      "problemMatcher": [],
      "presentation": { "reveal": "always", "panel": "dedicated" }
    },
    {
      "label": "Rebuild site from data",
      "detail": "Regenerate data files, Stata kit, every page, the data note and repo files from _build/. Needs Python 3.10+ with pandas; pdflatex for the note.",
      "type": "shell",
      "command": \"""" + REBUILD + """\",
      "windows": { "command": \"""" + REBUILD.replace("python3", "python").replace(" && ", "; ") + """\" },
      "options": { "cwd": "${workspaceFolder}/_build" },
      "problemMatcher": [],
      "presentation": { "reveal": "always", "panel": "dedicated", "clear": true }
    },
    {
      "label": "Check for broken links",
      "detail": "Verify every internal href and src resolves to a real file.",
      "type": "shell",
      "command": "python3 _build/linkcheck.py",
      "windows": { "command": "python _build\\\\linkcheck.py" },
      "options": { "cwd": "${workspaceFolder}" },
      "problemMatcher": [],
      "presentation": { "reveal": "always", "panel": "dedicated", "clear": true }
    }
  ],
  "inputs": [
    { "id": "commitMessage", "type": "promptString", "description": "Commit message (leave blank for an automatic dated one)", "default": "" }
  ]
}
""")
if not IN_REPO:
    for f in ("publish.sh", "publish.ps1"):
        shutil.copy2(os.path.join(V1, f), os.path.join(SITE, f))
    os.chmod(os.path.join(SITE, "publish.sh"), 0o755)

# ----------------------------------------------------------------- _build: copy of the build sources
if not IN_REPO:
    B = os.path.join(SITE, "_build")
    os.makedirs(os.path.join(B, "render"), exist_ok=True)
    for f in ["geo.py", "data.py", "stata.py", "pages.py", "paper.py", "repo.py", "layout.py", "linkcheck.py",
              "catalogue_raw.json", "content_v1.json", "pak_adm2_simplified.json", "geo.json", "geo_internal.json", "districts.csv"]:
        shutil.copy2(os.path.join(HERE, f), os.path.join(B, f))
    QA = os.path.join(_PARENT, "qa")
    for f in ["check.js", "interact.js", "og.js", "fig.js"]:
        src = open(os.path.join(QA, f), encoding="utf-8").read().replace("localhost:8752", "localhost:8000")
        src = src.replace("/_og/", "/_build/render/").replace("'/home/claude/site2/out/pakistan-evidence-catalogue/", "require('path').resolve(__dirname, '..') + '/")
        src = src.replace("executablePath: '/usr/bin/google-chrome'", "executablePath: process.env.CHROME || '/usr/bin/google-chrome'")
        open(os.path.join(B, f), "w", encoding="utf-8").write(src)
    for f in ["og.html", "fig.html"]:
        shutil.copy2(os.path.join(HERE, "render", f), os.path.join(B, "render", f))
    w("_build/README.md", f"""# Build scripts

The site is static. Everything under `data/`, `toolkit/`, `programmes/`, the other page folders and `paper/` is generated
from the files in this folder. The stylesheet and scripts in `assets/` are hand-written and edited directly.

Run from this folder, in order (Python 3.10+, `pip install pandas`; `pdflatex` for the note):

    python3 geo.py      # pak_adm2_simplified.json -> geo.json, districts.csv, geo_internal.json
    python3 data.py     # catalogue_raw.json + corrections + footprints -> ../data/*
    python3 stata.py    # -> ../toolkit/stata/*.do and ../toolkit/pec-stata-kit.zip
    python3 pages.py    # -> every HTML page
    python3 paper.py    # -> ../paper/pec-data-note.pdf
    python3 repo.py     # -> README, sitemap, citation files, issue forms, redirects

`data.py` holds the hand-checked parts: `CORRECTIONS`, `FOOTPRINTS` (each phase with its source), `EV_OVERRIDE`,
`CALENDAR` and `BIB`. Edit those, then rerun from `data.py` down.

## Checks and images (optional, Node 18+ and Chrome)

    npm install puppeteer-core
    python3 -m http.server 8000 --directory ..     # in another terminal
    node check.js       # every page, desktop and 390px: console errors and horizontal overflow
    node interact.js    # atlas, filters, search, shortlist, power calculator, chart tables
    node og.js          # social cards -> ../assets/og/*.jpg  (uses render/og.html)
    node fig.js         # figures for the data note -> ../paper/*.png  (uses render/fig.html)
    python3 linkcheck.py

Set `CHROME=/path/to/chrome` if Chrome is not at /usr/bin/google-chrome.
""")
    og = os.path.join(SITE, "_og")
    if os.path.isdir(og):
        shutil.rmtree(og)

# ----------------------------------------------------------------- README
fp_list = ", ".join(f"{p['id']} {p['short']}" for p in P if p["footprint"])
w("README.md", f"""# Pakistan Evidence Catalogue

**{C['programmes']} public programmes and natural experiments in Pakistan that reached districts at different times**, with the
rollout dates, outcomes and datasets needed to evaluate them.

Live site: **{URL}**

![Pakistan Evidence Catalogue](assets/og/home.jpg)

## What is in it

| | |
|---|---|
| Programmes and natural experiments | {C['programmes']}, each with rollout window, unit, assignment rule, timing source, graded timing-data quality, threats, evidence status |
| Programme–outcome pairs | {C['pairs']}, each with mechanism, expected direction, datasets and feasibility |
| Outcome definitions | {C['outcomes']} |
| Datasets | {C['datasets']}, with coverage, district identifier, access route and panel readiness |
| Documented rollout districts | {C['footprints']} entries, every phase sourced |
| District crosswalk | 200 name variants onto {C['districts']} constant 2019 boundary units, plus a lineage table of later districts |
| Stata kit | harmonisation, Callaway–Sant'Anna, Sun–Abraham, Borusyak–Jaravel–Spiess, de Chaisemartin–D'Haultfœuille, HonestDiD, power |

## The site

- **Programmes**: filter by domain, province, timing data, evidence, rollout unit, design, map and type; grid or table; CSV export.
- **Programme pages**: a district map that replays documented phases, the rollout timeline with sources, identification,
  outcomes with datasets, survey waves against the rollout window, a power calculator and a generated Stata do-file.
- **Atlas**: every district, three layers (programme scope by year, documented rollout, boundary notes); click a district
  to list the programmes that reached it.
- **Insights**: opportunity matrix, rollout timelines, start years, outcome coverage heatmap, dataset usage, survey calendar.
- **Datasets**, **Toolkit** (downloads, crosswalk, Stata kit, power), **Guide** (methods, treatment dates, caveats).
- Search everything with `/` or Ctrl+K. Save entries to a shortlist and compare them side by side.
- Claim an idea or suggest a correction through GitHub issue forms; open claims show on the programme page.

Documented footprints: {fp_list}.

## Files

| Path | Contents |
|---|---|
| `data/programmes.csv`, `.dta` | one row per entry |
| `data/programme_outcome_matrix.csv`, `.dta` | one row per programme–outcome pair |
| `data/outcomes.csv`, `data/datasets.csv` | outcome taxonomy, dataset catalogue |
| `data/documented_footprints.csv`, `.dta` | programme × phase × district, with source |
| `data/districts/` | crosswalk (`.csv`, `.dta`), boundary units, lineage |
| `data/catalogue.json` | everything, nested |
| `data/references.bib` | BibTeX |
| `toolkit/stata/`, `toolkit/pec-stata-kit.zip` | Stata starter kit |
| `paper/pec-data-note.pdf` | five-page data note (LaTeX source alongside) |

## Preview and publish

Open `index.html` directly, or serve the folder: `python3 -m http.server 8000`. To publish, run `./publish.sh`
(macOS, Linux) or `.\\publish.ps1` (Windows), or use the VS Code task *Publish to GitHub*. Then, once:
Settings → Pages → Deploy from a branch → `main` / root.

To rebuild from data, see [`_build/README.md`](_build/README.md).

## Caveats

- Secondary sources disagree on dates routinely. Check every date against the primary source named on the programme page.
- Expected directions are hypotheses, not findings. Nothing here has been estimated.
- Boundaries are geoBoundaries 2019: Punjab shows 34 units, Azad Kashmir and Karachi are single units, and Larkana is not a
  separate polygon. Boundaries do not imply any judgement on the status of any territory; the status of Jammu and Kashmir is disputed.
- Coverage is uneven: Punjab documents its programmes far better than Balochistan or Gilgit-Baltistan.
- Several references could not be verified and are marked as such; replication status of published studies is not assessed.

## Changes in {VERSION}

- New design, a district map for every entry, the atlas, the insights page and the toolkit.
- Documented rollout districts with sources for {C['footprints']} entries; district crosswalk and lineage on constant boundaries.
- Stata kit, per-programme do-files, `.dta` exports, power calculator, data note.
- Evidence status, related entries and dataset panel-readiness for every record.
""" + "".join(f"- Corrected {p['id']} {p['short']}: {p['correction']}\n" for p in P if p["correction"]) + f"""
Version 1 addresses (`/matrix/`, `/outcomes/`, `/methods/`, `/timing/`, `/caveats/`, `/data/`) redirect to their new pages.

## Cite

> Hussain, S. (2026). *Pakistan Evidence Catalogue: staggered district-level programmes for causal impact evaluation*,
> version {VERSION}. {URL}

GitHub's *Cite this repository* button reads `CITATION.cff`. `.zenodo.json` is ready for a Zenodo DOI: connect the repository
at zenodo.org, then publish a GitHub release.

## Licence and credits

Catalogue content CC BY 4.0; site code also MIT (see `LICENSE`). Boundaries: geoBoundaries (public domain).
Typeface: Jost, SIL Open Font Licence. The visual design follows the editorial conventions of film and culture sites:
white ground, a light geometric sans, centred section titles and one dark stage. No third-party brand assets are used.

Maintainer: Saqib Hussain, saqibhussain@kdis.ac.kr
""")
print("repo files written; in repo:", IN_REPO)
