# -*- coding: utf-8 -*-
"""
Turn the simplified geoBoundaries ADM2 file into site-ready geometry.

Input : pak_adm2_simplified.json  (126 districts, integer grid = degrees x 1000,
        topology-preserving simplification done upstream, so shared borders
        have identical vertices in neighbouring districts)
Output: geo.json  - projected SVG paths for districts, province borders, outline
        districts.csv - the 126 boundary units with province and centroid
        containment checks for districts created after the boundary vintage
"""
import json, math, csv, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "pak_adm2_simplified.json")))

PROV_CODE = {
    "Punjab": "PB", "Sindh": "SD", "Khyber Pakhtunkhwa": "KP", "Balochistan": "BA",
    "Gilgit-Baltistan": "GB", "Azad Kashmir": "AJK", "Islamabad Capital Territory": "ICT",
}
FATA = {"Bajaur", "Mohmand", "Khyber", "Kurram", "Orakzai", "North Waziristan", "South Waziristan"}

# ---------------------------------------------------------------- decode
districts = []
for name, prov, cx, cy, polys in raw["d"]:
    P = []
    for poly in polys:
        R = []
        for flat in poly:
            pts, x, y = [], 0, 0
            for i in range(0, len(flat), 2):
                if i == 0:
                    x, y = flat[0], flat[1]
                else:
                    x += flat[i]; y += flat[i + 1]
                pts.append((x, y))
            R.append(pts)
        P.append(R)
    districts.append({"name": name, "prov": prov, "code": PROV_CODE[prov], "P": P,
                      "cgrid": (cx, cy), "fata": name in FATA})

# stable ids: province code + slug
def slug(s):
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in s).strip("-").replace("--", "-")

for d in districts:
    d["id"] = f"{d['code'].lower()}-{slug(d['name'])}"

# ---------------------------------------------------------------- projection (Albers equal-area conic, spherical)
phi1, phi2, phi0, lam0 = map(math.radians, (25.0, 35.0, 30.0, 69.5))
n = (math.sin(phi1) + math.sin(phi2)) / 2
C = math.cos(phi1) ** 2 + 2 * n * math.sin(phi1)
rho0 = math.sqrt(C - 2 * n * math.sin(phi0)) / n

def albers(lon, lat):
    phi, lam = math.radians(lat), math.radians(lon)
    rho = math.sqrt(C - 2 * n * math.sin(phi)) / n
    th = n * (lam - lam0)
    return rho * math.sin(th), rho0 - rho * math.cos(th)

allp = [albers(x / 1000, y / 1000) for d in districts for poly in d["P"] for r in poly for (x, y) in r]
minx, maxx = min(p[0] for p in allp), max(p[0] for p in allp)
miny, maxy = min(p[1] for p in allp), max(p[1] for p in allp)
W = 1000.0
pad = 6.0
scale = (W - 2 * pad) / (maxx - minx)
H = round((maxy - miny) * scale + 2 * pad, 1)

def proj(gx, gy):
    X, Y = albers(gx / 1000, gy / 1000)
    return round((X - minx) * scale + pad, 1), round((maxy - Y) * scale + pad, 1)

def fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s

def ring_path(pts):
    out = []
    for i, (gx, gy) in enumerate(pts):
        X, Y = proj(gx, gy)
        out.append(("M" if i == 0 else "L") + fmt(X) + " " + fmt(Y))
    return "".join(out) + "Z"

# ---------------------------------------------------------------- centroid (area-weighted, largest polygon)
def area_centroid(r):
    a = cx = cy = 0.0
    for i in range(len(r)):
        x1, y1 = r[i]; x2, y2 = r[(i + 1) % len(r)]
        c = x1 * y2 - x2 * y1
        a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
    a /= 2
    return abs(a), cx / (6 * a), cy / (6 * a)

for d in districts:
    best = max((area_centroid(poly[0]) for poly in d["P"]), key=lambda t: t[0])
    d["area_grid"] = sum(area_centroid(poly[0])[0] for poly in d["P"])
    gx, gy = d["cgrid"]
    d["lonlat"] = (round(gx / 1000, 3), round(gy / 1000, 3))
    d["c"] = proj(gx, gy)

# ---------------------------------------------------------------- edges -> outline and province borders
edge_owner = defaultdict(list)
for di, d in enumerate(districts):
    for poly in d["P"]:
        for r in poly:
            for i in range(len(r)):
                a, b = r[i], r[(i + 1) % len(r)]
                if a == b:
                    continue
                k = (a, b) if a < b else (b, a)
                edge_owner[k].append(di)

outline_edges, prov_edges = [], []
for k, owners in edge_owner.items():
    if len(owners) == 1:
        outline_edges.append(k)
    elif len(owners) >= 2:
        provs = {districts[o]["prov"] for o in owners}
        if len(provs) > 1:
            prov_edges.append(k)

def chain(edges):
    """Join undirected edges into polylines; returns list of point lists."""
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    used = set()
    lines = []
    def key(a, b):
        return (a, b) if a < b else (b, a)
    # start from endpoints (degree != 2) first, then loops
    starts = [v for v in adj if len(adj[v]) != 2] + list(adj.keys())
    for s in starts:
        for nb in adj[s]:
            if key(s, nb) in used:
                continue
            line = [s, nb]; used.add(key(s, nb))
            cur, prev = nb, s
            while True:
                nxt = [w for w in adj[cur] if key(cur, w) not in used]
                if not nxt or len(adj[cur]) != 2 and cur != s:
                    if not nxt:
                        break
                    if len(adj[cur]) != 2:
                        break
                w = nxt[0]
                used.add(key(cur, w)); line.append(w)
                prev, cur = cur, w
                if cur == s:
                    break
            lines.append(line)
    return lines

def lines_path(lines):
    out = []
    for line in lines:
        for i, (gx, gy) in enumerate(line):
            X, Y = proj(gx, gy)
            out.append(("M" if i == 0 else "L") + fmt(X) + " " + fmt(Y))
    return "".join(out)

outline_lines = chain(outline_edges)
prov_lines = chain(prov_edges)

# province label anchors = area-weighted mean of district centroids
prov_anchor = defaultdict(lambda: [0.0, 0.0, 0.0])
for d in districts:
    w = d["area_grid"]
    prov_anchor[d["code"]][0] += d["c"][0] * w
    prov_anchor[d["code"]][1] += d["c"][1] * w
    prov_anchor[d["code"]][2] += w

geo = {
    "vb": [W, H],
    "src": "geoBoundaries gbOpen PAK ADM2, build 9469f09, boundaries represent 2019, public domain. "
           "Simplified (topology-preserving, ~1 km) and projected (Albers equal-area, 25N/35N).",
    "d": [{"id": d["id"], "n": d["name"], "p": d["code"], "f": 1 if d["fata"] else 0,
           "c": [d["c"][0], d["c"][1]],
           "path": "".join(ring_path(r) for poly in d["P"] for r in poly)} for d in districts],
    "outline": lines_path(outline_lines),
    "prov": lines_path(prov_lines),
    "provLabels": {k: [round(v[0] / v[2], 1), round(v[1] / v[2], 1)] for k, v in prov_anchor.items()},
}
json.dump(geo, open(os.path.join(HERE, "geo.json"), "w"), separators=(",", ":"))

# ---------------------------------------------------------------- point in polygon on the grid
def in_ring(x, y, r):
    ins = False
    j = len(r) - 1
    for i in range(len(r)):
        xi, yi = r[i]; xj, yj = r[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins

def unit_at(lon, lat):
    x, y = lon * 1000, lat * 1000
    for d in districts:
        for poly in d["P"]:
            if in_ring(x, y, poly[0]) and not any(in_ring(x, y, h) for h in poly[1:]):
                return d
    return None

# expose for other build scripts
with open(os.path.join(HERE, "districts.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pec_unit_id", "district", "province", "province_code", "ex_fata",
                "centroid_lon", "centroid_lat"])
    for d in sorted(districts, key=lambda d: (d["code"], d["name"])):
        w.writerow([d["id"], d["name"], d["prov"], d["code"], int(d["fata"]),
                    d["lonlat"][0], d["lonlat"][1]])

json.dump({"districts": [{k: v for k, v in d.items()} for d in districts]},
          open(os.path.join(HERE, "geo_internal.json"), "w"), separators=(",", ":"))

size = os.path.getsize(os.path.join(HERE, "geo.json"))
print(f"viewBox {W} x {H}; districts {len(districts)}; geo.json {size/1024:.0f} KB")
print(f"outline polylines {len(outline_lines)}; province-border polylines {len(prov_lines)}")
by = defaultdict(int)
for d in districts: by[d['code']] += 1
print("per province:", dict(by))

# quick containment sanity checks with well-known town coordinates
checks = {"Lahore": (74.34, 31.55), "Karachi": (67.01, 24.86), "Peshawar": (71.57, 34.01),
          "Quetta": (66.99, 30.18), "Larkana city": (68.21, 27.56), "Nankana Sahib town": (73.70, 31.45),
          "Chiniot town": (72.98, 31.72), "Sujawal town": (68.08, 24.61), "Gilgit": (74.31, 35.92),
          "Muzaffarabad": (73.47, 34.37), "Islamabad": (73.05, 33.69)}
for k, (lo, la) in checks.items():
    u = unit_at(lo, la)
    print(f"  {k:22s} -> {u['name'] + ' (' + u['code'] + ')' if u else 'NONE'}")
