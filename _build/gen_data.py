# -*- coding: utf-8 -*-
"""Export the catalogue to JSON and CSV for the website."""
import json, csv, os, re

ROOT = "/home/claude/site/pakistan-evidence-catalogue"
os.makedirs(f"{ROOT}/data", exist_ok=True)

raw = json.load(open("/home/claude/site/catalogue_raw.json", encoding="utf-8"))

PROG_FIELDS = ["id", "programme", "domain", "agency", "scope", "start_year", "rollout_window",
               "rollout_unit", "n_districts", "staggering", "assignment", "timing_source",
               "timing_quality", "identification", "threats", "evidence"]
OUT_FIELDS = ["id", "domain", "outcome", "definition", "unit", "frequency", "datasets"]
DS_FIELDS = ["key", "dataset", "producer", "type", "unit", "coverage", "district_id",
             "access", "url", "notes"]
MX_FIELDS = ["programme_id", "outcome_id", "outcome", "mechanism", "expected_sign",
             "dataset_keys", "feasibility"]

DATASETS = {d[0]: d[1:] for d in raw["datasets"]}


def region_of(scope):
    s = scope.lower()
    tags = []
    if "national" in s:
        tags.append("National")
    if "punjab" in s:
        tags.append("Punjab")
    if "sindh" in s:
        tags.append("Sindh")
    if "khyber" in s or re.search(r"\bkp\b", s):
        tags.append("Khyber Pakhtunkhwa")
    if "balochistan" in s:
        tags.append("Balochistan")
    if "fata" in s:
        tags.append("Ex-FATA")
    if "ajk" in s or "kashmir" in s:
        tags.append("AJK")
    if re.search(r"\bgb\b", s) or "gilgit" in s:
        tags.append("Gilgit-Baltistan")
    return tags or ["National"]


def unit_of(u):
    u = u.lower()
    # Check the finer unit first: "Tehsil (ARC), aggregable to district" is a
    # tehsil-level treatment, and mislabelling it District hides the best
    # feature of those entries (within-district variation).
    if "tehsil" in u:
        return "Tehsil"
    if "constituency" in u:
        return "Constituency"
    if "agency" in u or "tribal" in u:
        return "Agency / tribal district"
    if "province" in u:
        return "Province"
    if any(k in u for k in ["facility", "school", "plant", "lot", "scheme",
                            "watercourse", "market", "road section", "claim"]):
        return "Sub-district"
    return "District"


def era_of(start):
    m = re.search(r"\d{4}", str(start))
    if not m:
        return "Continuous"
    y = int(m.group())
    if y < 2005:
        return "Pre-2005"
    if y < 2010:
        return "2005-2009"
    if y < 2015:
        return "2010-2014"
    if y < 2020:
        return "2015-2019"
    return "2020 onwards"


def quality_rank(q):
    q = q.lower()
    if q.startswith("high"):
        return 3
    if q.startswith("medium-high"):
        return 2
    if q.startswith("medium"):
        return 1
    return 0


def quality_label(q):
    return {3: "High", 2: "Medium-High", 1: "Medium", 0: "Low-Medium"}[quality_rank(q)]


matrix_by_prog = {}
for row in raw["matrix"]:
    matrix_by_prog.setdefault(row[0], []).append(row)

SHOCK_IDS = {"P62", "P63", "P64", "P65", "P66", "P67"}

programmes = []
for p in raw["programs"]:
    rec = dict(zip(PROG_FIELDS, p))
    rec["slug"] = rec["id"].lower()
    rec["regions"] = region_of(rec["scope"])
    rec["unit_class"] = unit_of(rec["rollout_unit"])
    rec["era"] = era_of(rec["start_year"])
    rec["quality_rank"] = quality_rank(rec["timing_quality"])
    rec["quality_label"] = quality_label(rec["timing_quality"])
    rec["timing_quality_note"] = rec["timing_quality"]
    rec["n_outcomes"] = len(matrix_by_prog.get(rec["id"], []))
    rec["kind"] = "Shock / natural experiment" if (
        rec["id"] in SHOCK_IDS or rec["domain"].lower().startswith("shock")) else "Programme"
    txt = (rec["identification"] + " " + rec["assignment"] + " " + rec["staggering"]).lower()
    methods = ["Staggered DiD"]
    if any(k in txt for k in ["discontinuity", "cut-off", "cutoff", "threshold", " rd ", "rd on"]):
        methods.append("Regression discontinuity")
    if "synthetic control" in txt:
        methods.append("Synthetic control")
    if "instrument" in txt or "first stage" in txt:
        methods.append("IV / first stage")
    if "event study" in txt or "event-study" in txt:
        methods.append("Event study")
    if any(k in txt for k in ["dose", "intensity", "continuous"]):
        methods.append("Continuous dose")
    if "randomis" in txt or "rct" in txt:
        methods.append("Embedded RCT")
    rec["methods"] = sorted(set(methods))
    rec["ready"] = rec["quality_rank"] >= 2
    rec["status"] = "Open"
    programmes.append(rec)

outcomes = [dict(zip(OUT_FIELDS, o)) for o in raw["outcomes"]]
datasets = [dict(zip(DS_FIELDS, [k] + list(v))) for k, v in DATASETS.items()]

by_id = {p["id"]: p for p in programmes}
out_by_id = {o["id"]: o for o in outcomes}

matrix = []
for row in raw["matrix"]:
    rec = dict(zip(MX_FIELDS, row))
    prog = by_id[rec["programme_id"]]
    rec["programme"] = prog["programme"]
    rec["domain"] = prog["domain"]
    rec["outcome_domain"] = out_by_id.get(rec["outcome_id"], {}).get("domain", "")
    names, sources, seen = [], [], set()
    for d in rec["dataset_keys"].split("|"):
        d = d.strip()
        key = d.split(" ")[0]
        if key in DATASETS:
            meta = DATASETS[key]
            suffix = d[len(key):].strip()
            names.append(meta[0] + (" " + suffix if suffix else ""))
            if key not in seen:
                seen.add(key)
                sources.append({"key": key, "producer": meta[1], "url": meta[7]})
        else:
            names.append(d)
    rec["dataset_names"] = names
    rec["sources"] = sources
    matrix.append(rec)

meta = {
    "title": "Pakistan Evidence Catalogue",
    "subtitle": "Staggered district-level programmes for causal impact evaluation",
    "version": "1.0.0",
    "released": "2026-11-02",
    "licence": "CC BY 4.0",
    "counts": {
        "programmes": len(programmes),
        "outcomes": len(outcomes),
        "pairs": len(matrix),
        "datasets": len(datasets),
        "ready": sum(1 for p in programmes if p["ready"]),
        "high": sum(1 for p in programmes if p["quality_rank"] == 3),
    },
}

for name, obj in [("programmes", programmes), ("outcomes", outcomes),
                  ("datasets", datasets), ("matrix", matrix), ("meta", meta)]:
    json.dump(obj, open(f"{ROOT}/data/{name}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

json.dump({"meta": meta, "programmes": programmes, "outcomes": outcomes,
           "datasets": datasets, "matrix": matrix},
          open(f"{ROOT}/data/catalogue.json", "w", encoding="utf-8"), ensure_ascii=False)


def write_csv(path, fields, rows_):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows_:
            r = dict(r)
            for k, v in list(r.items()):
                if isinstance(v, list):
                    r[k] = "; ".join(str(x) for x in v)
                elif isinstance(v, bool):
                    r[k] = "Yes" if v else "No"
            w.writerow(r)


write_csv(f"{ROOT}/data/programmes.csv",
          PROG_FIELDS + ["kind", "regions", "unit_class", "era", "quality_label",
                         "methods", "ready", "n_outcomes"], programmes)
write_csv(f"{ROOT}/data/outcomes.csv", OUT_FIELDS, outcomes)
write_csv(f"{ROOT}/data/datasets.csv", DS_FIELDS, datasets)
write_csv(f"{ROOT}/data/programme_outcome_matrix.csv",
          ["programme_id", "programme", "domain", "outcome_id", "outcome", "outcome_domain",
           "mechanism", "expected_sign", "dataset_keys", "feasibility"], matrix)

print(json.dumps(meta["counts"]))
