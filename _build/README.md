# Build scripts

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
