# -*- coding: utf-8 -*-
"""Rebuild the python data modules from the delivered workbook."""
import openpyxl, json, re

SRC = "/mnt/user-data/outputs/Pakistan_Staggered_District_Programs_Evaluation_Catalogue.xlsx"
wb = openpyxl.load_workbook(SRC, data_only=True)


def rows(sheet, ncols):
    ws = wb[sheet]
    out = []
    for i in range(2, ws.max_row + 1):
        vals = [ws.cell(i, j).value for j in range(1, ncols + 1)]
        if vals[0] is None:
            continue
        out.append(["" if v is None else str(v) for v in vals])
    return out


programs = rows("01_Programs", 16)
outcomes = rows("02_Outcomes", 7)
datasets = rows("04_Datasets", 10)
mx = rows("03_Program_x_Outcome", 10)

# matrix sheet columns: prog_id, programme, domain, out_id, outcome, mechanism,
# sign, dataset_names(expanded), sources, feasibility
# We need the original dataset KEYS back. Rebuild by matching expanded names to keys.
ds_by_name = {}
for d in datasets:
    ds_by_name[d[1]] = d[0]

name_sorted = sorted(ds_by_name.keys(), key=len, reverse=True)


def to_keys(expanded):
    keys = []
    for part in expanded.split("; "):
        part = part.strip()
        matched = None
        for nm in name_sorted:
            if part.startswith(nm):
                suffix = part[len(nm):].strip()
                matched = ds_by_name[nm] + ((" " + suffix) if suffix else "")
                break
        keys.append(matched if matched else part)
    return "|".join(keys)


matrix = [[m[0], m[3], m[4], m[5], m[6], to_keys(m[7]), m[9]] for m in mx]

with open("/home/claude/site/catalogue_raw.json", "w", encoding="utf-8") as f:
    json.dump({"programs": programs, "outcomes": outcomes,
               "datasets": datasets, "matrix": matrix}, f, ensure_ascii=False)

print("programs", len(programs), "outcomes", len(outcomes),
      "datasets", len(datasets), "matrix", len(matrix))
unmatched = [m[5] for m in matrix if any(
    p not in [d[0] for d in datasets] and " " not in p for p in m[5].split("|"))]
print("sample keys:", matrix[0][5], "||", matrix[60][5])
