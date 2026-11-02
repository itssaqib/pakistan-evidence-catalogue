# Pakistan Evidence Catalogue

**Staggered district-level programmes for causal impact evaluation.**

An open catalogue of **67** public programmes and natural experiments in Pakistan that
reached different places at different times, with **322** programme-outcome pairs,
**102** outcome definitions and **55** datasets mapped against them.

Live site: <https://itssaqib.github.io/pakistan-evidence-catalogue>

---

## What problem this solves

Staggered rollout is the variation causal inference needs, and Pakistan has a great deal of it that
has never been used. The binding constraint is rarely the research question. It is two practical
facts that are expensive to establish: **when** each district was actually treated, and **whether an
outcome exists at the same resolution**. Both sit scattered across agency reports, project documents
and evaluation appendices.

This catalogue records both for every entry, and grades how reliable the timing data is -- including
where the honest answer is that it is not reliable at all. Of 67 entries,
**26 are graded High** and **19 Medium-High**.

## Entries with the most reliable treatment dates

| ID | Programme | Rollout | Outcomes |
|----|-----------|---------|----------|
| `P04` | BISP Waseela-e-Taleem (primary education CCT) | Launched November 2012 in 5 districts; expanded in waves to  | 7 |
| `P06` | Ehsaas Nashonuma (nutrition CCT with specialised nutritious food) | Phase 1 in 9 districts (2020), expanded to 13-15 districts ( | 6 |
| `P07` | Punjab Zewar-e-Taleem (girls' secondary stipend) | Phased across 16-17 low-literacy districts, 2017-2019 | 6 |
| `P08` | Punjab Female School Stipend Programme (PFSSP) | 15 low-literacy districts from 2004; later extension | 6 |
| `P13` | Prime Minister's National Health Programme / Federal Sehat Sahulat (SSP-I and II) | Launched 31 December 2015 in an initial district set; SSP-II | 7 |
| `P14` | KP Sehat Card Plus (universal provincial coverage) | 4 pilot districts (2015, poorest ~21%); ~24 districts (2017) | 6 |

See the [full list](https://itssaqib.github.io/pakistan-evidence-catalogue/programmes/?quality_label=High).

---

## Repository layout

```
.
├── index.html                  Home
├── programmes/                 Index + 67 programme pages (p01.html ... p67.html)
├── matrix/                     Programme x outcome browser
├── outcomes/                   Outcome taxonomy
├── datasets/                   Dataset catalogue
├── methods/                    Identification playbook
├── timing/                     How to obtain treatment dates
├── caveats/                    Standing caveats
├── data/                       Downloads page + all data files
│   ├── programmes.csv          67 rows
│   ├── programme_outcome_matrix.csv   322 rows
│   ├── outcomes.csv            102 rows
│   ├── datasets.csv            55 rows
│   └── catalogue.json          everything, nested
├── contribute/                 Contribute, claim, correct
├── about/                      About
├── assets/css/main.css         Single stylesheet
├── assets/js/site.js           Filtering, search, sorting, SVG charts
├── 404.html
├── publish.sh / publish.ps1    One-command commit + push
├── .vscode/tasks.json          VS Code tasks (publish, preview, rebuild, linkcheck)
├── sitemap.xml  robots.txt  .nojekyll  .gitignore  .editorconfig
└── CITATION.cff  LICENSE
```

No build step, no dependencies, no package.json. Every page is plain HTML; the tables are
rendered client-side from the JSON in `data/`.

---

## Publishing from VS Code

Open **this folder** in VS Code (`File -> Open Folder`, select the folder containing
`index.html` -- not its parent). Then either:

**Option A -- the task (no terminal needed)**

`Terminal -> Run Task... -> Publish to GitHub`, or press `Ctrl/Cmd+Shift+B`. It asks for a
commit message, then commits and pushes. Leave the message blank for an automatic dated one.

**Option B -- the script**

```bash
./publish.sh "Initial commit"      # macOS / Linux
.\publish.ps1 "Initial commit"     # Windows PowerShell
```

**Option C -- the Source Control panel**

`Ctrl/Cmd+Shift+G` -> *Initialize Repository* -> stage all -> commit -> *Publish Branch*.
VS Code handles GitHub sign-in itself, which is the easiest route if you have never
authenticated git on this machine.

### First run

The script creates the repository for you if the [`gh` CLI](https://cli.github.com) is
installed and signed in (`gh auth login`). Otherwise it pauses and asks you to create an
**empty** repository at <https://github.com/new> first -- no README, no `.gitignore`, no
licence, since this folder already has all three and GitHub's versions would collide.

Change the target by editing the three variables at the top of the script, or by exporting
them:

```bash
GITHUB_USER=yourname REPO_NAME=your-repo ./publish.sh
```

### Authentication

Pushing over HTTPS needs a credential, not your account password. Easiest first:

1. `gh auth login` -- handles everything, and lets the script create the repo too.
2. VS Code's Source Control panel -- signs in through the browser.
3. A [personal access token](https://github.com/settings/tokens) with `repo` scope, used as
   the password when git prompts.

### Other tasks

| Task | What it does |
|------|--------------|
| **Preview site locally** | Serves on `http://localhost:8000`. Required -- see below. |
| **Rebuild site from data** | Regenerates every page from `_build/catalogue_raw.json`. |
| **Check for broken links** | Verifies all 3,500+ internal links resolve. |

## Publishing on GitHub Pages

1. Create a repository named `pakistan-evidence-catalogue`.
2. Upload the contents of this folder to the repository root (not the folder itself --
   `index.html` must sit at the top level).
3. Settings -> Pages -> Source: **Deploy from a branch** -> Branch: `main`, folder: `/ (root)`.
4. Wait about a minute. The site appears at `https://<username>.github.io/pakistan-evidence-catalogue/`.

`.nojekyll` is already included, which stops GitHub from running Jekyll over the files.

### Publishing at a different path

The site uses **relative links throughout**, so it works at any subpath without changes.
Two exceptions, both cosmetic:

- `404.html` has absolute links -- edit them if your repository name differs.
- `sitemap.xml` and `robots.txt` contain the full URL -- update `https://itssaqib.github.io/pakistan-evidence-catalogue` if your username or
  repository name differs.

### Custom domain

Add a file named `CNAME` at the root containing your domain, then point a CNAME DNS record at
`<username>.github.io`.

---

## Local preview

```bash
cd pakistan-evidence-catalogue
python3 -m http.server 8000
# then open http://localhost:8000
```

A plain `file://` open will show the pages but the tables will stay empty: browsers block `fetch()`
of local JSON. Use the server above, any static server, or deploy.

---

## Regenerating the site

The HTML is generated from the data files by the Python scripts in `_build/` (not required to run
the site). To change content, edit the source data and regenerate, rather than editing HTML by hand:

```bash
python gen_data.py       # catalogue -> data/*.json, data/*.csv
python gen_pages.py      # home + programme index
python gen_programmes.py # 67 programme pages
python gen_sections.py   # matrix, outcomes, datasets
python gen_guides.py     # methods, timing
python gen_misc.py       # caveats, data, contribute, about, 404
python gen_repo.py       # README, sitemap, licence, citation
python linkcheck.py      # verify every internal link still resolves
```

---

## Data schema

Full column documentation is on the [downloads page](https://itssaqib.github.io/pakistan-evidence-catalogue/data/). In brief, `programmes.csv`
carries, for each entry: identifier, name, domain, agency, scope, start year, rollout window,
rollout unit, number of treated units, type of staggering, assignment rule, **timing source**,
**timing quality**, identification notes, threats to identification, and existing evidence --
plus derived fields for province, rollout unit class, start period, suitable designs and
outcome count.

`programme_outcome_matrix.csv` carries one row per programme-outcome pair with the mechanism,
expected sign, dataset keys and a feasibility note. Dataset keys join to `datasets.csv` on `key`.

---

## Caveats worth reading before use

1. **District boundaries move.** Nankana Sahib 2005, Chiniot 2009, seven ex-FATA districts 2018,
   five more in Punjab in 2022-23. Harmonise to a constant boundary set before building any panel.
2. **Most of these programmes were targeted at districts already doing badly**, which guarantees
   mean reversion.
3. **Several treatments switched off again** -- contracting was reversed, Saaf Pani was suspended,
   local governments were dissolved and restored.
4. **Dates in secondary sources disagree routinely.** Verify against the primary document named on
   each programme page.
5. **Expected signs are hypotheses, not findings.** Nothing here has been estimated.

The [caveats page](https://itssaqib.github.io/pakistan-evidence-catalogue/caveats/) covers all eight in full.

---

## Contributing

The most valuable contribution is a **district-by-date treatment-timing file** for any entry --
it saves the next person months, and will be hosted here with attribution. Corrections to dates
backed by a primary document come second. See [contribute](https://itssaqib.github.io/pakistan-evidence-catalogue/contribute/).

## Citation

> Hussain, S. (2026). *Pakistan Evidence Catalogue: staggered district-level programmes for causal
> impact evaluation.* Version 1.0.0. <https://itssaqib.github.io/pakistan-evidence-catalogue>

Machine-readable metadata in [`CITATION.cff`](CITATION.cff).

## Licence

[CC BY 4.0](LICENSE) for the catalogue. The underlying datasets it describes each carry their own
licence and access conditions -- see the `access` field on every dataset entry.

## Maintainer

Saqib Hussain -- [itssaqib.github.io](https://itssaqib.github.io) -- saqibhussain@kdis.ac.kr
