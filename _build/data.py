# -*- coding: utf-8 -*-
"""
Build every data artefact the site and downloads need.

Reads : catalogue_raw.json (programmes, outcomes, datasets, matrix)
        geo.json, geo_internal.json (from geo.py)
Writes: out/<site>/data/*  and returns nothing. Prints a review of derived fields.
"""
import json, os, re, csv, math
from collections import defaultdict, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(HERE)
SITE = _PARENT if os.path.exists(os.path.join(_PARENT, "assets", "css", "site.css")) else os.path.join(_PARENT, "out", "pakistan-evidence-catalogue")
DATA = os.path.join(SITE, "data")
os.makedirs(DATA, exist_ok=True)
os.makedirs(os.path.join(DATA, "districts"), exist_ok=True)

raw = json.load(open(os.path.join(HERE, "catalogue_raw.json"), encoding="utf-8"))
geo = json.load(open(os.path.join(HERE, "geo.json")))
GI = json.load(open(os.path.join(HERE, "geo_internal.json")))["districts"]

VERSION, RELEASED = "2.0.0", "2026-11-04"

PF = ["id", "programme", "domain", "agency", "scope", "start_year", "rollout_window",
      "rollout_unit", "n_districts", "staggering", "assignment", "timing_source",
      "timing_quality", "identification", "threats", "evidence"]
progs = [dict(zip(PF, p)) for p in raw["programs"]]
P = {p["id"]: p for p in progs}

# =============================================================================
# 1. Corrections verified against primary sources in this release
# =============================================================================
CORRECTIONS = {
    "P33": {
        "start_year": "2011",
        "rollout_window": "Established 2010; first scheme (Skills for Employability) launched June 2011 in "
                          "four districts: Bahawalpur, Bahawalnagar, Lodhran and Muzaffargarh; later expanded "
                          "across Punjab (all 36 districts by about 2016)",
        "_note": "v2.0 correction: v1.0 listed Rahim Yar Khan instead of Muzaffargarh and dated the start to 2010. "
                 "Source: PSDF Newsletter 2012, Vol. I.",
    },
    "P40": {
        "rollout_window": "Lahore 2016; seven further cities announced January 2019: Kasur, Multan, Rawalpindi, "
                          "Faisalabad, Sargodha, Bahawalpur and Gujranwala",
        "n_districts": "8 districts",
        "_note": "v2.0 correction: v1.0 omitted Kasur. Source: Punjab Police press release, 2 January 2019.",
    },
    "P14": {
        "rollout_window": "Four pilot districts from December 2015 (Malakand, Kohat, Mardan, Chitral; poorest "
                          "~21% of households); ~24 districts by 2017; all districts and 100% of the population "
                          "from 20 August 2020",
        "_note": "v2.0: pilot districts named. Source: Dawn, 16 December 2015.",
    },
}
for pid, fix in CORRECTIONS.items():
    for k, v in fix.items():
        if not k.startswith("_"):
            P[pid][k] = v
    P[pid]["correction"] = fix["_note"]

# =============================================================================
# 2. Documented footprints (only lists confirmed in a named source)
# =============================================================================
SRC = {
    "pspa_zewar": ("Punjab Social Protection Authority — Zewar-e-Taleem Program", "https://pspa.punjab.gov.pk/zewar-e-taleem-program"),
    "dawn_kp_2015": ("Dawn — Khattak launches health insurance scheme (16 Dec 2015)", "https://www.dawn.com/news/1226678/khattak-launches-health-insurance-scheme"),
    "dawn_kp_2020": ("Dawn — KP govt launches Sehat Sahulat programme for all residents (20 Aug 2020)", "https://www.dawn.com/news/1575463"),
    "ssp_history": ("Sehat Card Plus KP — Programme history", "https://sehatsahulat.com.pk/sehat-sahulat-programme-history/"),
    "macro_punjab": ("Macro Pakistani — Universal health insurance in Punjab", "https://macropakistani.substack.com/p/universal-health-insurance-in-punjab-953871"),
    "ryk_pilot": ("Public Health (2019) — PPP in health service delivery in Sindh", "https://www.sciencedirect.com/science/article/abs/pii/S0033350619300289"),
    "pphi_sindh": ("PPHI Sindh — organisation profile (started in Kashmore)", "https://www.developmentaid.org/organizations/view/103777/pphi-sindh"),
    "dawn_phfmc": ("Dawn — Punjab to 'outsource' basic health project (14 May 2015)", "https://www.dawn.com/news/1181844"),
    "rescue": ("Punjab Emergency Service — Emergency Ambulance Service", "https://www.rescue.gov.pk/AmbulanceService.aspx"),
    "tribune_rescue": ("Express Tribune — Rescue 1122 will expand to Punjab tehsils by 2019", "https://tribune.com.pk/story/1826803/1-rescue-1122-will-expand-punjab-tehsils-2019/"),
    "news_evs15": ("The News — PEF expands voucher scheme for students (22 Oct 2015)", "https://www.thenews.com.pk/print/69009-pef-expands-voucher-scheme-for-students"),
    "psdf_2012": ("PSDF Newsletter 2012, Vol. I", "https://psdf.org.pk/wp-content/uploads/2018/11/Newsletter-Newsletter-2012-Vol-I.pdf"),
    "ary_safecity": ("ARY News — Punjab CM inaugurates Lahore Safe City project", "https://arynews.tv/punjab-cm-inaugurates-lahore-safe-city-project"),
    "police_safecity": ("Punjab Police — 7 new Safe City projects are being established (2 Jan 2019)", "https://punjabpolice.gov.pk/node/6591"),
    "amend25": ("Constitution (Twenty-fifth Amendment) Act, 2018", "https://en.wikipedia.org/wiki/Twenty-fifth_Amendment_to_the_Constitution_of_Pakistan"),
    "ispr": ("ISPR announcements, compiled in BFRS / GTD event data", "https://esoc.princeton.edu/data/bfrs-political-violence-pakistan-dataset"),
    "erra": ("Earthquake Reconstruction & Rehabilitation Authority — affected districts", "https://www.erra.gov.pk"),
}

FOOTPRINTS = {
    "P07": {"final": "listed", "phases": [
        {"label": "Programme districts", "year": 2017, "src": "pspa_zewar",
         "names": ["Bahawalnagar", "Bahawalpur", "Bhakkar", "Chiniot", "Dera Ghazi Khan", "Jhang", "Kasur",
                   "Khanewal", "Kot Addu", "Layyah", "Lodhran", "Muzaffargarh", "Okara", "Pakpattan",
                   "Rajanpur", "Rahim Yar Khan", "Vehari"]}]},
    "P14": {"final": "scope", "final_year": 2020, "final_src": "dawn_kp_2020", "phases": [
        {"label": "Pilot", "year": 2015, "src": "dawn_kp_2015", "names": ["Malakand", "Kohat", "Mardan", "Chitral"]}]},
    "P15": {"final": "scope", "final_year": 2022, "final_src": "macro_punjab",
            "final_note": "Remaining divisions followed during 2022; month-level dates need checking against notifications.",
            "phases": [
        {"label": "DG Khan & Sahiwal divisions", "year": 2021, "src": "ssp_history",
         "names": ["Dera Ghazi Khan", "Rajanpur", "Layyah", "Muzaffargarh", "Sahiwal", "Okara", "Pakpattan"]},
        {"label": "Lahore", "year": 2022, "src": "macro_punjab", "names": ["Lahore"]}]},
    "P16": {"final": "partial", "phases": [
        {"label": "PRSP pilot", "year": 2003, "src": "ryk_pilot", "names": ["Rahim Yar Khan"]},
        {"label": "First district in Sindh", "year": 2007, "src": "pphi_sindh", "names": ["Kashmore"]}]},
    "P17": {"final": "partial", "phases": [
        {"label": "First districts identified", "year": 2015, "src": "dawn_phfmc",
         "names": ["Nankana Sahib", "Bahawalnagar", "Narowal", "Mandi Bahauddin"]}]},
    "P18": {"final": "scope", "final_year": 2015, "final_src": "tribune_rescue", "final_regions": ["PB"],
            "final_note": "All Punjab districts by about 2015; the year is approximate. Coverage in other provinces is not dated here.", "phases": [
        {"label": "Pilot", "year": 2004, "src": "rescue", "names": ["Lahore"]}]},
    "P24": {"final": "partial", "phases": [
        {"label": "Expansion phase 15", "year": 2015, "src": "news_evs15",
         "names": ["Faisalabad", "Jhang", "Sheikhupura", "Kasur", "Okara", "Rahim Yar Khan", "Multan", "Bahawalpur",
                   "Bahawalnagar", "Khanewal", "Rajanpur", "Dera Ghazi Khan", "Vehari", "Lodhran", "Muzaffargarh", "Khushab"]}]},
    "P33": {"final": "scope", "final_year": 2016, "final_src": "psdf_2012",
            "final_note": "Year of province-wide coverage is approximate.", "phases": [
        {"label": "First scheme", "year": 2011, "src": "psdf_2012",
         "names": ["Bahawalpur", "Bahawalnagar", "Lodhran", "Muzaffargarh"]}]},
    "P40": {"final": "listed", "phases": [
        {"label": "Lahore", "year": 2016, "src": "ary_safecity", "names": ["Lahore"]},
        {"label": "Seven cities announced", "year": 2019, "src": "police_safecity",
         "names": ["Kasur", "Multan", "Rawalpindi", "Faisalabad", "Sargodha", "Bahawalpur", "Gujranwala"]}]},
    "P42": {"final": "listed", "phases": [
        {"label": "Merged tribal districts", "year": 2018, "src": "amend25",
         "names": ["Bajaur", "Mohmand", "Khyber", "Kurram", "Orakzai", "North Waziristan", "South Waziristan"]}]},
    "P58": {"final": "listed", "phases": [
        {"label": "Rah-e-Rast; Rah-e-Nijat", "year": 2009, "src": "ispr", "names": ["Swat", "South Waziristan"]},
        {"label": "Zarb-e-Azb; Khyber-I", "year": 2014, "src": "ispr", "names": ["North Waziristan", "Khyber"]}]},
    "P64": {"final": "listed", "phases": [
        {"label": "Most affected districts", "year": 2005, "src": "erra",
         "names": ["Azad Kashmir", "Mansehra", "Battagram", "Abbottabad", "Shangla", "Kohistan"]}]},
    "P43": {"final": "listed", "phases": [
        {"label": "Nankana Sahib (from Sheikhupura)", "year": 2005, "src": None, "names": ["Nankana Sahib"]},
        {"label": "Chiniot (from Jhang)", "year": 2009, "src": None, "names": ["Chiniot"]},
        {"label": "Kot Addu, Talagang, Murree, Wazirabad", "year": 2022, "src": None,
         "names": ["Kot Addu", "Talagang", "Murree", "Wazirabad"]},
        {"label": "Taunsa (from Dera Ghazi Khan)", "year": 2023, "src": None, "names": ["Taunsa"]}]},
}

# =============================================================================
# 3. District names -> boundary units (aliases and post-2019 splits)
# =============================================================================
UNITS = {d["name"]: d for d in GI}
UNIT_ID = {d["name"]: d["id"] for d in GI}

def norm(s):
    s = s.lower().replace("&", "and")
    s = re.sub(r"\b(district|agency|tribal|frontier region)\b", "", s)
    return re.sub(r"[^a-z0-9]", "", s)

# variant -> (unit name, relation, note)
ALIASES = {
    "Sheikhupura": ("Sheikhpura", "spelling", ""), "Vehari": ("Vihari", "spelling", ""),
    "Shaheed Benazirabad": ("Nawabshah", "renamed", "Renamed 2008"), "Benazirabad": ("Nawabshah", "renamed", ""),
    "Naushahro Feroze": ("Naushehro Feroze", "spelling", ""), "Naushero Feroze": ("Naushehro Feroze", "spelling", ""),
    "DG Khan": ("Dera Ghazi Khan", "abbreviation", ""), "D.G. Khan": ("Dera Ghazi Khan", "abbreviation", ""),
    "DI Khan": ("Dera Ismail Khan", "abbreviation", ""), "D.I. Khan": ("Dera Ismail Khan", "abbreviation", ""),
    "Rahimyar Khan": ("Rahim Yar Khan", "spelling", ""), "RY Khan": ("Rahim Yar Khan", "abbreviation", ""),
    "TT Singh": ("Toba Tek Singh", "abbreviation", ""), "MB Din": ("Mandi Bahauddin", "abbreviation", ""),
    "Mandi Bahaudin": ("Mandi Bahauddin", "spelling", ""),
    "Killa Abdullah": ("Qilla Abdullah", "spelling", ""), "Killa Saifullah": ("Qilla Saifullah", "spelling", ""),
    "Bolan": ("Kachhi", "renamed", "Bolan renamed Kachhi"), "Turbat": ("Kech", "alternate name", ""),
    "Jaffarabad": ("Jafarabad", "spelling", ""), "Kambar Shahdadkot": ("Qambar Shahdadkot", "spelling", ""),
    "Kambar": ("Qambar Shahdadkot", "abbreviation", ""), "Mirpur Khas": ("Mirpurkhas", "spelling", ""),
    "Islamabad": ("Islamabad Capital Territory", "abbreviation", ""), "ICT": ("Islamabad Capital Territory", "abbreviation", ""),
    "Lasbela": ("Lasbela", "same", ""), "Las Bela": ("Lasbela", "spelling", ""),
    "Malakand Agency": ("Malakand", "former name", ""),
    "Bajaur Agency": ("Bajaur", "former name", "Merged 2018"), "Mohmand Agency": ("Mohmand", "former name", "Merged 2018"),
    "Khyber Agency": ("Khyber", "former name", "Merged 2018"), "Kurram Agency": ("Kurram", "former name", "Merged 2018"),
    "Orakzai Agency": ("Orakzai", "former name", "Merged 2018"),
    "North Waziristan Agency": ("North Waziristan", "former name", "Merged 2018"),
    "South Waziristan Agency": ("South Waziristan", "former name", "Merged 2018"),
    # AJK districts are one unit in this boundary file
    **{n: ("Azad Kashmir", "part of unit", "AJK is a single unit in the 2019 boundary file")
       for n in ["Muzaffarabad", "Hattian Bala", "Neelum", "Bagh", "Haveli", "Poonch", "Rawalakot", "Sudhnoti",
                 "Kotli", "Mirpur", "Bhimber"]},
    # Karachi districts are one unit in this boundary file
    **{n: ("Karachi", "part of unit", "Karachi is a single unit in the 2019 boundary file")
       for n in ["Karachi East", "Karachi West", "Karachi Central", "Karachi South", "Malir", "Korangi", "Keamari"]},
    # Frontier Regions merged into their namesake districts in 2018
    **{f"FR {n}": (n if n != "DI Khan" else "Dera Ismail Khan", "merged into", "Frontier Region merged 2018 (verify)")
       for n in ["Peshawar", "Kohat", "Bannu", "Lakki Marwat", "Tank", "DI Khan"]},
}

# districts created or split after the boundary vintage, with approximate HQ
# coordinates used to test which 2019 unit actually contains them
LINEAGE = [
    # child, province, year, parent_named, hq_lon, hq_lat, confidence
    ("Nankana Sahib", "Punjab", 2005, "Sheikhpura", 73.70, 31.45, "high"),
    ("Chiniot", "Punjab", 2009, "Jhang", 72.98, 31.72, "high"),
    ("Kot Addu", "Punjab", 2022, "Muzaffargarh", 70.97, 30.47, "medium"),
    ("Talagang", "Punjab", 2022, "Chakwal", 72.42, 32.93, "medium"),
    ("Murree", "Punjab", 2022, "Rawalpindi", 73.39, 33.91, "medium"),
    ("Wazirabad", "Punjab", 2022, "Gujranwala", 74.12, 32.44, "medium"),
    ("Taunsa", "Punjab", 2023, "Dera Ghazi Khan", 70.65, 30.70, "medium"),
    ("Larkana", "Sindh", None, "Qambar Shahdadkot", 68.21, 27.56, "boundary-file artefact"),
    ("Sujawal", "Sindh", 2013, "Thatta", 68.08, 24.61, "medium"),
    ("Tor Ghar", "Khyber Pakhtunkhwa", 2011, "Mansehra", 72.82, 34.62, "low"),
    ("Upper Chitral", "Khyber Pakhtunkhwa", 2018, "Chitral", 72.25, 36.27, "medium"),
    ("Lower Chitral", "Khyber Pakhtunkhwa", 2018, "Chitral", 71.79, 35.85, "medium"),
    ("Upper Kohistan", "Khyber Pakhtunkhwa", 2014, "Kohistan", 73.30, 35.29, "low"),
    ("Lower Kohistan", "Khyber Pakhtunkhwa", 2014, "Kohistan", 73.03, 35.03, "low"),
    ("Kolai Palas", "Khyber Pakhtunkhwa", 2017, "Kohistan", 73.05, 34.95, "low"),
    ("Washuk", "Balochistan", 2005, "Kharan", 64.79, 27.72, "medium"),
    ("Sherani", "Balochistan", 2006, "Zhob", 69.85, 31.30, "low"),
    ("Harnai", "Balochistan", 2007, "Sibi", 67.94, 30.10, "medium"),
    ("Lehri", "Balochistan", 2013, "Sibi", 68.00, 29.25, "low"),
    ("Sohbatpur", "Balochistan", 2013, "Jafarabad", 68.55, 28.52, "low"),
    ("Duki", "Balochistan", 2016, "Loralai", 68.56, 30.15, "medium"),
    ("Surab", "Balochistan", 2017, "Kalat", 66.26, 28.49, "medium"),
    ("Chaman", "Balochistan", 2021, "Qilla Abdullah", 66.45, 30.92, "high"),
    ("Hub", "Balochistan", 2022, "Lasbela", 66.88, 25.05, "medium"),
    ("Usta Muhammad", "Balochistan", 2022, "Jafarabad", 68.04, 28.18, "medium"),
    ("Roundu", "Gilgit-Baltistan", 2019, "Skardu", 75.20, 35.70, "low"),
    ("Darel", "Gilgit-Baltistan", 2019, "Diamer", 73.50, 35.60, "low"),
    ("Tangir", "Gilgit-Baltistan", 2019, "Diamer", 73.30, 35.65, "low"),
    ("Gupis-Yasin", "Gilgit-Baltistan", 2019, "Ghizer", 73.40, 36.20, "low"),
]

def in_ring(x, y, r):
    ins, j = False, len(r) - 1
    for i in range(len(r)):
        xi, yi = r[i]; xj, yj = r[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins

def unit_at(lon, lat):
    x, y = lon * 1000, lat * 1000
    for d in GI:
        for poly in d["P"]:
            if in_ring(x, y, poly[0]) and not any(in_ring(x, y, h) for h in poly[1:]):
                return d
    return None

lineage_rows = []
for child, prov, yr, parent, lo, la, conf in LINEAGE:
    u = unit_at(lo, la)
    contained = u["name"] if u else ""
    status = "consistent" if contained == parent else ("check" if contained else "point outside map")
    lineage_rows.append({"district": child, "province": prov, "created": yr or "",
                         "parent_named": parent, "contained_in_unit": contained,
                         "pec_unit_id": UNIT_ID.get(contained, ""), "hq_lon": lo, "hq_lat": la,
                         "check": status, "confidence": conf})
    rel = "boundary-file artefact" if yr is None else "created after boundary vintage"
    target = contained if status == "consistent" else parent
    ALIASES.setdefault(child, (target, rel, f"Created {yr} from {parent}" if yr else
                               "Not a separate polygon in the 2019 boundary file; contained in the Qambar Shahdadkot unit"))

def resolve(name):
    if name in UNITS:
        return name
    if name in ALIASES:
        return ALIASES[name][0]
    k = norm(name)
    for u in UNITS:
        if norm(u) == k:
            return u
    for a, (u, _, _) in ALIASES.items():
        if norm(a) == k:
            return u
    raise KeyError(f"Unresolved district name: {name}")

# crosswalk table
cw = []
for u in sorted(UNITS):
    d = UNITS[u]
    cw.append({"name_variant": u, "key": norm(u), "pec_unit": u, "pec_unit_id": d["id"],
               "province": d["prov"], "relation": "boundary unit", "note": ""})
for a, (u, rel, note) in sorted(ALIASES.items()):
    d = UNITS[u]
    cw.append({"name_variant": a, "key": norm(a), "pec_unit": u, "pec_unit_id": d["id"],
               "province": d["prov"], "relation": rel, "note": note})

_seen, _cw = set(), []
for r in cw:
    if r["key"] in _seen:
        continue
    _seen.add(r["key"]); _cw.append(r)
cw = _cw

# =============================================================================
# 4. Derived programme fields
# =============================================================================
def macro_of(domain):
    d = domain.lower()
    first = d.split("/")[0].strip()
    if first.startswith("shock"): return "Shocks & natural experiments"
    if first.startswith("social protection"): return "Social protection"
    if first.startswith("health"): return "Health"
    if first.startswith("education") or first.startswith("skills"): return "Education & skills"
    if first.startswith("conflict"): return "Conflict & security"
    if "infrastructure" in first: return "Infrastructure"
    if first.startswith(("financ", "agriculture finance", "markets")): return "Finance & markets"
    if first.startswith(("governance", "political")): return "Governance & state capacity"
    return "Other"

MACRO_ORDER = ["Social protection", "Health", "Education & skills", "Governance & state capacity",
               "Infrastructure", "Finance & markets", "Conflict & security", "Shocks & natural experiments"]

def years_in(s):
    return [int(y) for y in re.findall(r"\b(19[89]\d|20[0-2]\d)\b", s)]

def region_codes(scope):
    s = scope.lower()
    if "national" in s:
        return ["ALL"]
    codes = []
    if "punjab" in s: codes.append("PB")
    if "sindh" in s: codes.append("SD")
    if "khyber" in s or re.search(r"\bkp\b", s): codes.append("KP")
    if "balochistan" in s: codes.append("BA")
    if "fata" in s and "KP" not in codes: codes.append("FATA")
    if "ajk" in s or "kashmir" in s: codes.append("AJK")
    if re.search(r"\bgb\b", s) or "gilgit" in s: codes.append("GB")
    if "ict" in s or "islamabad" in s: codes.append("ICT")
    return codes or ["ALL"]

def units_for(codes):
    if "ALL" in codes:
        return [d["id"] for d in GI]
    out = []
    for d in GI:
        if d["code"] in codes or ("FATA" in codes and d["fata"]):
            out.append(d["id"])
    return out

def unit_class(u):
    u = u.lower()
    if "tehsil" in u: return "Tehsil"
    if "constituency" in u: return "Constituency"
    if "agency" in u or "tribal" in u: return "Agency / tribal district"
    if "province" in u: return "Province"
    if any(k in u for k in ["facility", "school", "plant", "lot", "scheme", "watercourse", "market",
                            "road section", "claim", "city"]):
        return "Sub-district"
    return "District"

def tq_rank(q):
    q = q.lower()
    return 3 if q.startswith("high") else 2 if q.startswith("medium-high") else 1 if q.startswith("medium") else 0

TQ_LABEL = {3: "High", 2: "Medium-high", 1: "Medium", 0: "Low"}

def evidence_status(ev):
    e = ev.lower()
    unstudied = ["none known", "a clear gap", "a clear opening", "very thin", "unwritten", "almost nothing",
                 "no published causal", "essentially open", "under-studied", "largely unstudied",
                 "under-used", "little independent", "no causal evaluation", "thin - a"]
    limited = ["limited", "descriptive", "process evaluation", "supervision report", "rapid assessment",
               "icr", "no strong causal", "audit", "some ", "reports", "emerging", "case stud", "thin",
               "no rigorous"]
    if any(k in e for k in unstudied): return "Unstudied"
    if any(k in e for k in limited) and not re.search(r"\(\d{4}", ev): return "Limited"
    if re.search(r"\(\d{4}|\d{4}\)", ev): return "Published causal work"
    return "Limited"

# Hand-checked after reading each evidence note (keyword rules misfile about a tenth)
EV_OVERRIDE = {"P07": "Unstudied", "P58": "Limited", "P26": "Limited", "P62": "Published causal work",
               "P33": "Published causal work", "P27": "Published causal work", "P18": "Unstudied",
               "P35": "Published causal work", "P39": "Limited", "P53": "Limited", "P14": "Limited"}

RELATED_GROUPS = [
    ["P01", "P02", "P03", "P04", "P05", "P09", "P12", "P06", "P10"],
    ["P13", "P14", "P15"], ["P16", "P17", "P19", "P18", "P21"], ["P20", "P22", "P21"],
    ["P04", "P05", "P07", "P08"], ["P23", "P24", "P25", "P28"], ["P26", "P27", "P29", "P30"],
    ["P31", "P32", "P33", "P34"], ["P35", "P36", "P55", "P54"], ["P37", "P38", "P39", "P40", "P36"],
    ["P41", "P42", "P43", "P44", "P67"], ["P45", "P46", "P52", "P53", "P03"], ["P47", "P48", "P49", "P50", "P51"],
    ["P58", "P59", "P60", "P61", "P66", "P42"], ["P62", "P63", "P64", "P65"], ["P53", "P54", "P55", "P56", "P10"],
    ["P11", "P12", "P57"],
]

def related(pid):
    out = []
    for g in RELATED_GROUPS:
        if pid in g:
            out += [x for x in g if x != pid and x not in out]
    return out[:6]

def short_name(name):
    s = re.split(r" \(", name)[0]
    s = s.replace(" / ", " / ")
    return s

SHORT = {
    "P01": "BISP poverty census rollout", "P02": "BISP Kafaalat cash transfer", "P03": "BISP payment modernisation",
    "P04": "Waseela-e-Taleem", "P05": "Ehsaas Taleemi Wazaif", "P06": "Ehsaas Nashonuma", "P07": "Zewar-e-Taleem",
    "P08": "Punjab Female School Stipend", "P09": "NSER re-survey", "P10": "Ehsaas interest-free loans",
    "P11": "Khidmat / Himmat Card", "P12": "Ehsaas Emergency Cash", "P13": "Federal Sehat Sahulat",
    "P14": "KP Sehat Card Plus", "P15": "Punjab health card", "P16": "Contracting out health units",
    "P17": "PHFMC outsourcing", "P18": "Rescue 1122", "P19": "Lady Health Workers", "P20": "Saaf Pani filtration plants",
    "P21": "EPI and polio campaigns", "P22": "COVID lockdowns and vaccination", "P23": "PEF Foundation Assisted Schools",
    "P24": "PEF Education Vouchers", "P25": "PEF New School Program", "P26": "Punjab education reform roadmap",
    "P27": "School monitoring app", "P28": "Public School Support Programme", "P29": "KP Independent Monitoring Unit",
    "P30": "Sindh Education Reform", "P31": "Daanish Schools", "P32": "New universities and campuses",
    "P33": "Punjab Skills Development Fund", "P34": "NAVTTC skills programmes", "P35": "Punjab land records (LRMIS)",
    "P36": "Punjab e-Stamping", "P37": "Citizen Feedback Monitoring", "P38": "e-Khidmat Markaz",
    "P39": "Police record digitisation", "P40": "Punjab Safe Cities", "P41": "Local government elections",
    "P42": "FATA–KP merger", "P43": "New district creation", "P44": "Right to Information laws",
    "P45": "3G/4G mobile broadband", "P46": "Universal Service Fund broadband", "P47": "Motorway expansion",
    "P48": "Punjab rural roads", "P49": "Rural electrification", "P50": "Gas network expansion",
    "P51": "Punjab irrigation productivity", "P52": "Branchless banking agents", "P53": "Microfinance expansion",
    "P54": "Agricultural credit targets", "P55": "Punjab Kisan Card", "P56": "Kamyab Jawan loans",
    "P57": "Model Bazaars", "P58": "Military operations", "P59": "Drone strike campaign", "P60": "National Action Plan",
    "P61": "IDP returns to merged districts", "P62": "2010 floods", "P63": "2022 floods", "P64": "2005 earthquake",
    "P65": "Locust invasion", "P66": "Bin Laden killing shock", "P67": "Census and delimitation",
}

matrix_by = defaultdict(list)
for row in raw["matrix"]:
    matrix_by[row[0]].append(row)

SHOCK_IDS = {"P62", "P63", "P64", "P65", "P66", "P67"}
NON_ABSORBING = {"P16", "P20", "P41"}

out_progs = []
for p in progs:
    pid = p["id"]
    ys = years_in(p["rollout_window"] + " " + p["start_year"])
    sy = years_in(p["start_year"])
    start_y = sy[0] if sy else (min(ys) if ys else None)
    end_y = max(ys) if ys else start_y
    codes = region_codes(p["scope"])
    scope_units = units_for(codes)
    txt = (p["identification"] + " " + p["assignment"] + " " + p["staggering"]).lower()
    methods = ["Staggered DiD"]
    if any(k in txt for k in ["discontinuity", "cut-off", "cutoff", "threshold", "fuzzy rd", " rd "]): methods.append("Regression discontinuity")
    if "synthetic control" in txt or "small n" in txt or "few treated" in txt: methods.append("Synthetic control")
    if "instrument" in txt or "first stage" in txt: methods.append("Instrumental variables")
    if any(k in txt for k in ["dose", "intensity", "continuous"]): methods.append("Continuous treatment")
    if "randomis" in txt or "rct" in txt: methods.append("Embedded RCT")
    if pid in NON_ABSORBING: methods.append("Treatment switches off")

    fp = None
    if pid in FOOTPRINTS:
        F = FOOTPRINTS[pid]
        phases = []
        for ph in F["phases"]:
            units = sorted({UNIT_ID[resolve(n)] for n in ph["names"]})
            s = SRC.get(ph["src"]) if ph.get("src") else None
            phases.append({"label": ph["label"], "year": ph["year"], "names": ph["names"], "units": units,
                           "src": {"title": s[0], "url": s[1]} if s else None})
        fp = {"final": F["final"], "phases": phases}
        if F.get("final_year"):
            fs = SRC.get(F.get("final_src"))
            fp["final_year"] = F["final_year"]
            fp["final_src"] = {"title": fs[0], "url": fs[1]} if fs else None
        if F.get("final_note"):
            fp["final_note"] = F["final_note"]
        if F.get("final_regions"):
            fp["final_regions"] = F["final_regions"]

    J = len(scope_units)
    if fp and fp["final"] == "listed":
        n_tr = len({u for ph in fp["phases"] for u in ph["units"]})
        Pshare = round(min(max(n_tr / J, 0.02), 0.98), 2)
    else:
        Pshare = 0.5
    rows = matrix_by.get(pid, [])
    rec = OrderedDict(
        id=pid, slug=pid.lower(), name=p["programme"], short=SHORT.get(pid, short_name(p["programme"])),
        domain=p["domain"], macro=macro_of(p["domain"]), agency=p["agency"], scope=p["scope"],
        start=p["start_year"], start_y=start_y, end_y=end_y, years=sorted(set(ys)),
        window=p["rollout_window"], unit=p["rollout_unit"], unit_class=unit_class(p["rollout_unit"]),
        treated=p["n_districts"], stagger=p["staggering"], assign=p["assignment"],
        timing_src=p["timing_source"], tq=TQ_LABEL[tq_rank(p["timing_quality"])], tq_rank=tq_rank(p["timing_quality"]),
        tq_note=p["timing_quality"], ident=p["identification"], threats=p["threats"], evidence=p["evidence"],
        evidence_status=EV_OVERRIDE.get(pid, evidence_status(p["evidence"])), regions=codes, methods=methods,
        kind="Shock / natural experiment" if (pid in SHOCK_IDS or p["domain"].lower().startswith("shock")) else "Programme",
        related=related(pid), footprint=fp, n_outcomes=len(rows), mde={"J": J, "P": Pshare},
        correction=p.get("correction", ""),
    )
    out_progs.append(rec)

# =============================================================================
# 5. Outcomes, datasets, matrix, survey calendar, bibliography
# =============================================================================
OF = ["id", "domain", "outcome", "definition", "unit", "frequency", "datasets"]
outcomes = [dict(zip(OF, o)) for o in raw["outcomes"]]
DF = ["key", "dataset", "producer", "type", "unit", "coverage", "district_id", "access", "url", "notes"]
datasets = [dict(zip(DF, d)) for d in raw["datasets"]]
DS = {d["key"]: d for d in datasets}

DS_GRADE = {}
for k in ["PSLM", "LFS", "MICS_PB", "ASER", "PIE", "SIS_PB", "DHIS", "EPI_NEOC", "SBP_CRED", "PMN", "ECP", "GTD",
          "BFRS", "ACLED", "NTL", "MODIS", "CHIRPS", "CROPREP", "AMIS", "PLRA", "BISP_MIS", "SSP_MIS", "PITB",
          "POLICE", "COURTS", "USF", "OCID", "NADRA_ROLL", "BOR", "EMIS_OTH", "SBP_BB", "WORLDPOP", "OSM", "FLOOD", "PIPS"]:
    DS_GRADE[k] = "Panel-ready"
for k in ["HIES", "MICS_SD", "MICS_KP", "MICS_BL", "PDHS", "CENSUS", "AGCEN", "SPI", "FBR", "CMI", "PSDF", "PDMA",
          "MPI", "HDX", "PPHS", "WBMD", "OOKLA"]:
    DS_GRADE[k] = "Few waves"
for k in ["NNS", "RWI", "HDI"]:
    DS_GRADE[k] = "Cross-section"
for d in datasets:
    d["panel"] = DS_GRADE.get(d["key"], "Few waves")
    d["access_class"] = ("Open download" if re.search(r"free", d["access"], re.I) and not re.search(r"request|restricted|agreement", d["access"], re.I)
                         else "On request" if re.search(r"request|rti|registration", d["access"], re.I) and not re.search(r"restricted", d["access"], re.I)
                         else "Restricted")
    d["district"] = ("Yes" if d["district_id"].lower().startswith("yes") else
                     "Derivable" if re.search(r"aggregate", d["district_id"], re.I) else "Partial")

RANK = {"Panel-ready": 3, "Few waves": 2, "Cross-section": 1}
for o in outcomes:
    keys = [k.strip().split(" ")[0] for k in re.split(r";", o["datasets"])]
    grades = [DS_GRADE.get(k) for k in keys if DS_GRADE.get(k)]
    o["panel"] = max(grades, key=lambda g: RANK[g]) if grades else "Needs primary data"

prog_name = {p["id"]: p for p in out_progs}
out_dom = {o["id"]: o["domain"] for o in outcomes}
matrix = []
for row in raw["matrix"]:
    pid, oid, outcome, mech, sign, keys, feas = row
    names, srcs = [], []
    for part in keys.split("|"):
        part = part.strip(); k = part.split(" ")[0]
        if k in DS:
            sfx = part[len(k):].strip()
            names.append(DS[k]["dataset"] + (" " + sfx if sfx else "")); srcs.append(k)
        else:
            names.append(part)
    s = sign.lower()
    grp = ("Ambiguous" if "ambiguous" in s else
           "Decrease" if s.startswith("-") or "reduction" in s or "faster" in s or "shorter" in s else
           "Null or small" if s.startswith("0") else "Increase")
    matrix.append({"pid": pid, "oid": oid, "outcome": outcome, "odomain": out_dom.get(oid, ""),
                   "mech": mech, "sign": sign, "sign_group": grp, "keys": srcs, "ds": names, "feas": feas})

# survey calendar: dots for discrete waves, bands for near-continuous series.
CALENDAR = [
    {"key": "PSLM", "label": "PSLM (district rounds)", "dist": True,
     "waves": [[2004, "2004–05"], [2006, "2006–07"], [2008, "2008–09"], [2010, "2010–11"], [2012, "2012–13"],
               [2014, "2014–15"], [2018, "2018–19"], [2019, "2019–20"]]},
    {"key": "MICS_PB", "label": "MICS Punjab", "dist": True,
     "waves": [[2003, "2003–04"], [2007, "2007–08"], [2011, "2011"], [2014, "2014"], [2017, "2017–18"], [2024, "2024"]]},
    {"key": "MICS_SD", "label": "MICS Sindh", "dist": True, "waves": [[2003, "2003–04"], [2014, "2014"], [2018, "2018–19"]]},
    {"key": "MICS_KP", "label": "MICS Khyber Pakhtunkhwa", "dist": True, "waves": [[2008, "2008"], [2016, "2016–17"], [2019, "2019"]]},
    {"key": "MICS_BL", "label": "MICS Balochistan", "dist": True, "waves": [[2004, "2004"], [2010, "2010"], [2019, "2019–20"]]},
    {"key": "ASER", "label": "ASER Pakistan (rural)", "dist": True, "band": [2008, 2023], "band_note": "near-annual"},
    {"key": "LFS", "label": "Labour Force Survey", "dist": True, "band": [1990, 2021], "band_note": "annual"},
    {"key": "HIES", "label": "HIES (province)", "dist": False,
     "waves": [[2001, "2001–02"], [2004, "2004–05"], [2005, "2005–06"], [2007, "2007–08"], [2010, "2010–11"],
               [2011, "2011–12"], [2013, "2013–14"], [2015, "2015–16"], [2018, "2018–19"]]},
    {"key": "PDHS", "label": "Pakistan DHS (province)", "dist": False,
     "waves": [[1990, "1990–91"], [2006, "2006–07"], [2012, "2012–13"], [2017, "2017–18"]]},
    {"key": "NNS", "label": "National Nutrition Survey", "dist": True, "waves": [[2011, "2011 (province)"], [2018, "2018 (district)"]]},
    {"key": "CENSUS", "label": "Population census", "dist": True, "waves": [[1998, "1998"], [2017, "2017"], [2023, "2023"]]},
    {"key": "PIE", "label": "Education statistics (NEMIS)", "dist": True, "band": [2005, 2022], "band_note": "annual"},
    {"key": "DHIS", "label": "DHIS facility data", "dist": True, "band": [2005, 2025], "band_note": "monthly"},
    {"key": "PMN", "label": "MicroWatch", "dist": True, "band": [2007, 2025], "band_note": "quarterly"},
    {"key": "NTL", "label": "Night-time lights", "dist": True, "band": [1992, 2025], "band_note": "monthly / annual"},
    {"key": "GTD", "label": "Global Terrorism Database", "dist": True, "band": [1970, 2020], "band_note": "event data"},
]

BIB = [
    {"id": "malik2017", "pids": ["P16"], "authors": "Malik, M. A., Van de Poel, E. and Van Doorslaer, E.", "year": 2017,
     "title": "Did contracting effect the use of primary health care units in Pakistan?",
     "venue": "Health Policy and Planning", "vol": "32(7)", "pages": "1032–1041",
     "url": "https://academic.oup.com/heapol/article/32/7/1032/3793093", "verified": True},
    {"id": "opm2016", "pids": ["P01", "P02", "P04"], "authors": "Oxford Policy Management", "year": 2016,
     "title": "Benazir Income Support Programme: Final impact evaluation report", "venue": "OPM, Oxford",
     "url": "https://www.opml.co.uk/files/Publications/7328-evaluating-pakistans-flagship-social-protection-programme-bisp/bisp-final-impact-evaluation-report.pdf",
     "verified": True},
    {"id": "opm2015", "pids": ["P01", "P02"], "authors": "Oxford Policy Management", "year": 2015,
     "title": "Benazir Income Support Programme: Second impact evaluation report", "venue": "OPM, Oxford",
     "url": "https://www.opml.co.uk/sites/default/files/migrated_bolt_files/bisp-second-impact-evaluation-report.pdf",
     "verified": True},
    {"id": "bisp2020", "pids": ["P02"], "authors": "Benazir Income Support Programme", "year": 2020,
     "title": "Benazir Income Support Programme evaluation report (2011–2019)", "venue": "BISP, Islamabad",
     "url": "https://www.bisp.gov.pk/SiteImage/Misc/files/BISP_EvaluationReport_Ver%20without_FINAL.pdf", "verified": True},
    {"id": "kmuj2022", "pids": ["P14"], "authors": "Khyber Medical University Journal (review)", "year": 2022,
     "title": "Contextualising Sehat Sahulat Programme in the drive towards universal health coverage in Khyber Pakhtunkhwa, Pakistan",
     "venue": "Khyber Medical University Journal", "url": "https://www.kmuj.kmu.edu.pk/article/view/21481", "verified": True},
    {"id": "ijerph2022", "pids": ["P13", "P14", "P15"], "authors": "IJERPH (review article)", "year": 2022,
     "title": "“Sehat Sahulat Program”: A leap into the universal health coverage in Pakistan",
     "venue": "International Journal of Environmental Research and Public Health", "vol": "19(12)", "pages": "6998",
     "url": "https://www.mdpi.com/1660-4601/19/12/6998", "verified": True},
    {"id": "lancet2022", "pids": ["P14"], "authors": "The Lancet Regional Health – Southeast Asia (commentary)", "year": 2022,
     "title": "Sehat sahulat: A social health justice policy leaving no one behind",
     "venue": "The Lancet Regional Health – Southeast Asia",
     "url": "https://www.thelancet.com/journals/lansea/article/PIIS2772-36822200095-6/fulltext", "verified": True},
    {"id": "kdis2021", "pids": ["P35"], "authors": "KDI School of Public Policy and Management", "year": 2021,
     "title": "Impact evaluation of the Land Record Management Information System in the Punjab Province, Pakistan",
     "venue": "KDI School Working Paper DP21-12", "url": "https://archives.kdischool.ac.kr/handle/11125/43185", "verified": True},
    {"id": "egov2020", "pids": ["P35"], "authors": "EGOV-CeDEM-ePart 2020 (conference paper)", "year": 2020,
     "title": "The e-governance of land record and social dispute resolution: An impact evaluation of the Punjab Land Record Management Information System",
     "venue": "CEUR Workshop Proceedings, Vol. 2797", "url": "https://ceur-ws.org/Vol-2797/paper23.pdf", "verified": True},
    {"id": "chaudhury2010", "pids": ["P08"], "authors": "Chaudhury, N. and Parajuli, D.", "year": 2010,
     "title": "Conditional cash transfers and female schooling: the impact of the female school stipend programme on public school enrolments in Punjab, Pakistan",
     "venue": "Applied Economics", "vol": "42(28)", "pages": "3565–3583", "url": "", "verified": False},
    {"id": "alam2011", "pids": ["P08"], "authors": "Alam, A., Baez, J. E. and Del Carpio, X. V.", "year": 2011,
     "title": "Does cash for school influence young women's behavior in the longer term? Evidence from Pakistan",
     "venue": "IZA Discussion Paper 5703", "url": "", "verified": False},
    {"id": "andrabi2017", "pids": ["P64"], "authors": "Andrabi, T. and Das, J.", "year": 2017,
     "title": "In aid we trust: Hearts and minds and the Pakistan earthquake of 2005",
     "venue": "Review of Economics and Statistics", "vol": "99(3)", "pages": "371–386", "url": "", "verified": False},
    {"id": "johnston2016", "pids": ["P59"], "authors": "Johnston, P. B. and Sarbahi, A. K.", "year": 2016,
     "title": "The impact of US drone strikes on terrorism in Pakistan",
     "venue": "International Studies Quarterly", "vol": "60(2)", "pages": "203–219", "url": "", "verified": False},
    {"id": "barrera2017", "pids": ["P23"], "authors": "Barrera-Osorio, F. and Raju, D.", "year": 2017,
     "title": "Teacher performance pay: Experimental evidence from Pakistan",
     "venue": "Journal of Public Economics", "vol": "148", "pages": "75–91", "url": "", "verified": False},
    {"id": "callen2020", "pids": ["P27", "P26"], "authors": "Callen, M., Gulzar, S., Hasanain, A., Khan, Y. and Rezaee, A.", "year": 2020,
     "title": "Data and policy decisions: Experimental evidence from Pakistan",
     "venue": "Journal of Development Economics", "vol": "146", "pages": "102523", "url": "", "verified": False},
    {"id": "ambler2017", "pids": ["P01", "P02"], "authors": "Ambler, K. and de Brauw, A.", "year": 2017,
     "title": "The impacts of cash transfers on women's empowerment: Learning from Pakistan's BISP program",
     "venue": "World Bank Social Protection & Labor Discussion Paper 1702", "url": "", "verified": False},
]
for b in BIB:
    if not b["url"]:
        b["find"] = "https://scholar.google.com/scholar?q=" + re.sub(r"\s+", "+", b["title"])

# =============================================================================
# 6. Density by year (catalogued programmes whose documented footprint or
#    stated scope includes each district) for the hero and atlas
# =============================================================================
unit_ids = [d["id"] for d in GI]
YEARS = list(range(2000, 2025))
dens = {u: [0] * len(YEARS) for u in unit_ids}
for p in out_progs:
    if p["kind"] != "Programme":
        continue
    scope = set(units_for(p["regions"]))
    for yi, y in enumerate(YEARS):
        lit = set()
        if p["footprint"]:
            for ph in p["footprint"]["phases"]:
                if ph["year"] <= y:
                    lit |= set(ph["units"])
            if p["footprint"]["final"] == "scope" and y >= p["footprint"].get("final_year", 9999):
                fr = p["footprint"].get("final_regions")
                lit |= set(units_for(fr)) if fr else scope
        else:
            sy = p["start_y"] or 2000
            if y >= sy:
                lit = scope
        for u in lit:
            dens[u][yi] += 1
max_dens = max(max(v) for v in dens.values())

# =============================================================================
# 7. Write outputs
# =============================================================================
meta = {"title": "Pakistan Evidence Catalogue", "version": VERSION, "released": RELEASED, "licence": "CC BY 4.0",
        "counts": {"programmes": len(out_progs), "outcomes": len(outcomes), "pairs": len(matrix),
                   "datasets": len(datasets), "high": sum(1 for p in out_progs if p["tq_rank"] == 3),
                   "ready": sum(1 for p in out_progs if p["tq_rank"] >= 2),
                   "footprints": sum(1 for p in out_progs if p["footprint"]),
                   "unstudied": sum(1 for p in out_progs if p["evidence_status"] == "Unstudied"),
                   "districts": len(GI)},
        "macro_order": MACRO_ORDER, "years": YEARS, "max_density": max_dens}

PEC = {"meta": meta, "programmes": out_progs, "outcomes": outcomes, "datasets": datasets, "matrix": matrix,
       "calendar": CALENDAR, "bib": BIB, "density": dens, "lineage": lineage_rows, "sources": {k: {"title": v[0], "url": v[1]} for k, v in SRC.items()}}

with open(os.path.join(DATA, "catalogue.js"), "w", encoding="utf-8") as f:
    f.write("/* Pakistan Evidence Catalogue v" + VERSION + " — CC BY 4.0. Generated; do not edit by hand. */\n")
    f.write("window.PEC=" + json.dumps(PEC, ensure_ascii=False, separators=(",", ":")) + ";\n")
with open(os.path.join(DATA, "geo.js"), "w", encoding="utf-8") as f:
    f.write("/* District boundaries: geoBoundaries gbOpen PAK ADM2 (2019), public domain. Simplified and projected. */\n")
    f.write("window.PEC_GEO=" + json.dumps(geo, separators=(",", ":")) + ";\n")
json.dump(PEC, open(os.path.join(DATA, "catalogue.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            r = dict(r)
            for k, v in list(r.items()):
                if isinstance(v, list):
                    r[k] = "; ".join(str(x) for x in v)
                elif isinstance(v, dict):
                    r[k] = json.dumps(v, ensure_ascii=False)
                elif v is None:
                    r[k] = ""
            w.writerow(r)

PROG_FIELDS = ["id", "name", "short", "domain", "macro", "agency", "scope", "start", "start_y", "end_y", "window",
               "unit", "unit_class", "treated", "stagger", "assign", "timing_src", "tq", "tq_rank", "tq_note",
               "ident", "threats", "evidence", "evidence_status", "regions", "methods", "kind", "related", "n_outcomes",
               "correction"]
write_csv(os.path.join(DATA, "programmes.csv"), out_progs, PROG_FIELDS)
write_csv(os.path.join(DATA, "outcomes.csv"), outcomes, OF + ["panel"])
write_csv(os.path.join(DATA, "datasets.csv"), datasets, DF + ["panel", "access_class", "district"])
mx_rows = [{"programme_id": m["pid"], "programme": prog_name[m["pid"]]["name"], "outcome_id": m["oid"],
            "outcome": m["outcome"], "outcome_domain": m["odomain"], "mechanism": m["mech"], "expected_sign": m["sign"],
            "dataset_keys": "; ".join(m["keys"]), "datasets": "; ".join(m["ds"]), "feasibility": m["feas"]} for m in matrix]
write_csv(os.path.join(DATA, "programme_outcome_matrix.csv"), mx_rows, list(mx_rows[0].keys()))

fp_rows = []
for p in out_progs:
    if not p["footprint"]:
        continue
    for ph in p["footprint"]["phases"]:
        for n in ph["names"]:
            u = resolve(n)
            fp_rows.append({"programme_id": p["id"], "programme": p["short"], "phase": ph["label"], "year": ph["year"],
                            "district_as_named": n, "pec_unit": u, "pec_unit_id": UNIT_ID[u],
                            "source": ph["src"]["title"] if ph["src"] else "", "source_url": ph["src"]["url"] if ph["src"] else ""})
write_csv(os.path.join(DATA, "documented_footprints.csv"), fp_rows, list(fp_rows[0].keys()))

write_csv(os.path.join(DATA, "districts", "boundary_units.csv"),
          [{"pec_unit_id": d["id"], "district": d["name"], "province": d["prov"], "province_code": d["code"],
            "ex_fata": int(d["fata"]), "centroid_lon": d["lonlat"][0], "centroid_lat": d["lonlat"][1]}
           for d in sorted(GI, key=lambda d: (d["code"], d["name"]))],
          ["pec_unit_id", "district", "province", "province_code", "ex_fata", "centroid_lon", "centroid_lat"])
write_csv(os.path.join(DATA, "districts", "district_crosswalk.csv"), cw,
          ["name_variant", "key", "pec_unit", "pec_unit_id", "province", "relation", "note"])
write_csv(os.path.join(DATA, "districts", "district_lineage.csv"), lineage_rows, list(lineage_rows[0].keys()))

# BibTeX
def bibtex(b):
    kind = "article" if b.get("vol") else "techreport"
    fields = [f"  author = {{{b['authors']}}}", f"  year = {{{b['year']}}}", f"  title = {{{b['title']}}}"]
    fields.append(f"  {'journal' if kind == 'article' else 'institution'} = {{{b['venue']}}}")
    if b.get("vol"):
        m = re.match(r"(\d+)(?:\((\d+)\))?", b["vol"])
        fields.append(f"  volume = {{{m.group(1)}}}")
        if m.group(2): fields.append(f"  number = {{{m.group(2)}}}")
    if b.get("pages"): fields.append(f"  pages = {{{b['pages'].replace('–', '--')}}}")
    if b.get("url"): fields.append(f"  url = {{{b['url']}}}")
    if not b["verified"]: fields.append("  note = {Details from compiler's records; verify before citing}")
    return f"@{kind}{{{b['id']},\n" + ",\n".join(fields) + "\n}"
cat_bib = ("@misc{hussain2026pec,\n  author = {Hussain, Saqib},\n  year = {2026},\n"
           "  title = {Pakistan Evidence Catalogue: Staggered District-Level Programmes for Causal Impact Evaluation},\n"
           f"  note = {{Version {VERSION}}},\n  url = {{https://itssaqib.github.io/pakistan-evidence-catalogue/}}\n}}")
open(os.path.join(DATA, "references.bib"), "w", encoding="utf-8").write(cat_bib + "\n\n" + "\n\n".join(bibtex(b) for b in BIB) + "\n")

# Stata .dta exports
import pandas as pd
def to_dta(rows, fields, path, labels):
    df = pd.DataFrame([{k: (("; ".join(map(str, r.get(k))) if isinstance(r.get(k), list) else r.get(k)) if r.get(k) is not None else "") for k in fields} for r in rows])
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str)
    df.columns = [("shortname" if c == "short" else c)[:32] for c in df.columns]
    strl = [c for c in df.columns if df[c].dtype == object and df[c].str.len().max() > 2000]
    df.to_stata(path, write_index=False, version=118, convert_strl=strl,
                variable_labels={k[:32]: v[:80] for k, v in labels.items() if k[:32] in df.columns},
                data_label="Pakistan Evidence Catalogue v" + VERSION)
to_dta(out_progs, ["id", "short", "name", "macro", "domain", "agency", "scope", "start_y", "end_y", "unit_class",
                   "treated", "tq", "tq_rank", "evidence_status", "kind", "n_outcomes", "window", "assign", "timing_src",
                   "ident", "threats", "evidence"],
       os.path.join(DATA, "programmes.dta"),
       {"id": "Programme ID", "shortname": "Short name", "macro": "Macro domain", "start_y": "Start year (parsed)",
        "end_y": "Latest year in rollout window (parsed)", "tq": "Timing-data quality", "tq_rank": "Timing quality rank 0-3",
        "evidence_status": "Existing evidence", "timing_src": "Where to get treatment timing"})
to_dta(mx_rows, list(mx_rows[0].keys()), os.path.join(DATA, "programme_outcome_matrix.dta"),
       {"programme_id": "Programme ID", "outcome_id": "Outcome ID", "expected_sign": "Hypothesised direction"})
to_dta(cw, ["name_variant", "key", "pec_unit", "pec_unit_id", "province", "relation", "note"],
       os.path.join(DATA, "districts", "district_crosswalk.dta"),
       {"key": "Normalised merge key", "pec_unit": "2019 boundary unit (constant boundaries)"})
to_dta(fp_rows, list(fp_rows[0].keys()), os.path.join(DATA, "documented_footprints.dta"),
       {"pec_unit": "2019 boundary unit", "year": "Year of phase"})

# ---------------------------------------------------------------- review print
print("counts:", meta["counts"], "max density:", max_dens)
print("\nlineage containment checks:")
for r in lineage_rows:
    flag = "" if r["check"] == "consistent" else "   <-- " + r["check"]
    print(f"  {r['district']:16s} parent {r['parent_named']:18s} contained {r['contained_in_unit']:18s} [{r['confidence']}]{flag}")
print("\nevidence status:")
for st in ["Unstudied", "Limited", "Published causal work"]:
    print(f"  {st}: " + ", ".join(p["id"] for p in out_progs if p["evidence_status"] == st))
print("\nmacro domains:", {m: sum(1 for p in out_progs if p["macro"] == m) for m in MACRO_ORDER + ['Other']})
print("crosswalk rows:", len(cw), "| footprint rows:", len(fp_rows))
