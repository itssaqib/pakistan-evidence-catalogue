# Build scripts

The site is plain static HTML and needs none of this to run. These scripts regenerate it
from the catalogue data, so content changes should be made here rather than by editing
HTML by hand.

Requires Python 3 only (no packages). Run from this directory's parent:

    python gen_data.py        # catalogue_raw.json -> ../data/*.json and *.csv
    python gen_pages.py       # home + programme index
    python gen_programmes.py  # 67 programme detail pages
    python gen_sections.py    # matrix, outcomes, datasets
    python gen_guides.py      # methods, timing
    python gen_misc.py        # caveats, downloads, contribute, about, 404
    python gen_repo.py        # README, sitemap, robots, licence, citation

`layout.py` holds the shared page chrome (masthead, footer, meta tags).
`catalogue_raw.json` is the source data extracted from the original workbook by `extract.py`.
`check.js` renders every page in headless Chrome and asserts there are no console errors,
no horizontal overflow at 390px, and that filtering, sorting and deep links work
(needs `npm install puppeteer-core` and a local server on port 8742).
