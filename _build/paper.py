# -*- coding: utf-8 -*-
"""Write and compile the data-descriptor note: paper/pec-data-note.tex -> .pdf"""
import json, os, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(HERE)
SITE = _PARENT if os.path.exists(os.path.join(_PARENT, "assets", "css", "site.css")) else os.path.join(_PARENT, "out", "pakistan-evidence-catalogue")
OUT = os.path.join(SITE, "paper")
os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.path.join(SITE, "data", "catalogue.json"), encoding="utf-8"))
P, META, C = D["programmes"], D["meta"], D["meta"]["counts"]


def tex(s):
    s = str(s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
                 ("–", "--"), ("—", "---"), ("−", "-"), ("’", "'"), ("×", r"$\times$")]:
        s = s.replace(a, b)
    return s


TQ = ["High", "Medium-high", "Medium", "Low"]
EV = ["Unstudied", "Limited", "Published causal work"]
rows1 = ""
for m in META["macro_order"]:
    ps = [p for p in P if p["macro"] == m]
    if not ps:
        continue
    cnt = collections.Counter(p["tq"] for p in ps)
    rows1 += tex(m) + " & " + " & ".join(str(cnt.get(t, 0)) for t in TQ) + f" & {len(ps)} \\\\\n"
tot = collections.Counter(p["tq"] for p in P)
rows1 += r"\midrule" + "\nAll & " + " & ".join(str(tot.get(t, 0)) for t in TQ) + f" & {len(P)} \\\\\n"

rows2 = ""
for t in TQ:
    cnt = collections.Counter(p["evidence_status"] for p in P if p["tq"] == t)
    rows2 += t + " & " + " & ".join(str(cnt.get(e, 0)) for e in EV) + " \\\\\n"

rows3 = ""
for p in [x for x in P if x["footprint"]]:
    fp = p["footprint"]
    nd = len({u for ph in fp["phases"] for u in ph["units"]})
    yrs = sorted({ph["year"] for ph in fp["phases"]})
    final = {"listed": "Full list", "scope": f"Rest of scope by {fp.get('final_year', '')}", "partial": "Partial"}[fp["final"]]
    src = fp["phases"][0]["src"]["title"] if fp["phases"][0].get("src") else ""
    rows3 += f"{p['id']} & {tex(p['short'])} & {', '.join(map(str, yrs))} & {nd} & {final} & {tex(src)} \\\\\n"

corr = "".join(f"\\item \\textbf{{{p['id']} {tex(p['short'])}.}} {tex(p['correction'])}\n" for p in P if p["correction"])

doc = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{graphicx}
\usepackage{caption}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\captionsetup{font=small,labelfont=bf}
\setlist{itemsep=2pt}
\title{Pakistan Evidence Catalogue: staggered district-level programmes\\for causal impact evaluation\\[4pt]\large Data note, version """ + META["version"] + r"""}
\author{Saqib Hussain\thanks{KDI School of Public Policy and Management. \href{mailto:saqibhussain@kdis.ac.kr}{saqibhussain@kdis.ac.kr}. Catalogue: \url{https://itssaqib.github.io/pakistan-evidence-catalogue/}. Released under CC BY 4.0.}}
\date{""" + META["released"] + r"""}
\begin{document}
\maketitle
\begin{abstract}\noindent
This note describes an open catalogue of """ + str(C["programmes"]) + r""" public programmes and natural experiments in Pakistan that reached districts, tehsils or similar units at different times. For each entry the catalogue records the rollout window, the unit of rollout, the assignment rule, where district-by-date treatment timing can be obtained, a graded judgement of how reliable that timing source is, the main threats to identification and the state of existing causal evidence. It maps """ + str(C["pairs"]) + r""" programme--outcome pairs onto """ + str(C["outcomes"]) + r""" outcome definitions and """ + str(C["datasets"]) + r""" datasets that measure them at district resolution or finer. For """ + str(C["footprints"]) + r""" entries the districts in each rollout phase are documented with sources. A crosswalk maps 200 district name variants onto """ + str(C["districts"]) + r""" constant 2019 boundary units. The catalogue is a research-design inventory, not a store of estimates: expected directions are hypotheses and nothing has been estimated.
\end{abstract}

\section{Purpose}
Staggered adoption designs need two facts that are rarely in the same place: when each unit was treated, and an outcome measured at the same resolution before and after. In Pakistan both facts are scattered across agency reports, provincial development programme registers, donor project documents and the press, and district boundaries change frequently enough to break naive panels. The catalogue collects both facts for each entry and says explicitly how reliable the timing information is, including where it is not reliable at all.

\section{Inclusion}
An entry qualifies if (i) it reached geographic units at or below the province level at different times, or with different intensity, and (ii) that variation can in principle be dated. Of the """ + str(C["programmes"]) + r""" entries, 61 are programmes and 6 are shocks or natural experiments. The rollout unit is the district for 46 entries, the tehsil or another sub-district unit for 17, and a former tribal agency, a province or a constituency for the rest. Coverage is uneven by design of the sources: Punjab documents its programmes far better than Balochistan or Gilgit-Baltistan, and the catalogue inherits that imbalance.

\section{Record structure}
Each programme record holds: identifier and name; implementing agency; stated scope (provinces); rollout window and the first and last years mentioned in it; unit of rollout; type of staggering; assignment rule; source for district-by-date timing; timing-data quality (four grades, below); identification note; main threats; existing evidence and an evidence status (unstudied, limited, or published causal work); suitable designs; related entries; and, where documented, the districts in each phase with a source for each phase. The programme--outcome matrix pairs each entry with outcomes, a mechanism, an expected direction, candidate datasets and a feasibility note. Dataset records give producer, unit, coverage, whether a district identifier is present, access route and panel readiness (""" + "35 panel-ready, 17 with few waves, 3 cross-sections" + r"""; 31 open downloads, 15 on request, 9 restricted).

\paragraph{Timing-data quality.} \emph{High}: dates are published or sit in a named register that has already been assembled. \emph{Medium-high}: dates exist in administrative records and can be obtained by request or document search. \emph{Medium}: dates exist but are scattered across sources that disagree. \emph{Low}: no reliable district dating is known.

\begin{table}[ht]\centering\small
\caption{Entries by domain and timing-data quality}
\begin{tabular}{lrrrrr}\toprule
Domain & High & Medium-high & Medium & Low & Total\\\midrule
""" + rows1 + r"""\bottomrule\end{tabular}
\end{table}

\begin{table}[ht]\centering\small
\caption{Timing-data quality against existing causal evidence. The upper-left cell is the short list of datable, unstudied entries.}
\begin{tabular}{lrrr}\toprule
Timing data & Unstudied & Limited & Published causal work\\\midrule
""" + rows2 + r"""\bottomrule\end{tabular}
\end{table}

\section{Geography}
Boundaries are geoBoundaries' gbOpen ADM2 polygons for Pakistan (2019 vintage, public domain), simplified to roughly one kilometre with shared edges preserved so that province and national outlines are derived exactly from district borders, and projected with an Albers equal-area projection. The vintage has three consequences users should know: Punjab appears as 34 units rather than the 36 or more districts that exist today; Azad Jammu and Kashmir and Karachi are single units; and Larkana is not a separate polygon (its headquarters falls inside the Qambar Shahdadkot unit). Boundaries shown do not imply any judgement on the legal status of any territory.

Districts created after the boundary vintage are folded into the 2019 unit that contains their headquarters. Each assignment was tested by point-in-polygon on headquarters coordinates; """ + str(len(D["lineage"])) + r""" later districts are listed, of which two (Lehri and Roundu, both with low-confidence coordinates) are flagged for checking against gazette notifications. The crosswalk normalises names to a merge key: lower case, ampersand to ``and'', the words district, agency, tribal and frontier region removed, letters and digits only.

\begin{figure}[ht]\centering
\includegraphics[width=\linewidth]{fig-density.png}
\caption{Catalogued programmes whose stated scope or documented rollout includes each district, 2010 and 2024. Scope is not treatment: national programmes count everywhere from their start year. Natural experiments are not counted.}
\end{figure}

\section{Documented footprints}
Rollout districts are shown on the map only where a named source lists them. Table~\ref{tab:fp} lists the """ + str(C["footprints"]) + r""" entries with such lists. ``Rest of scope'' means a source dates completion of the remaining districts only approximately; ``partial'' means later phases exist but are not dated here.

\begin{table}[ht]\centering\scriptsize
\caption{Entries with documented rollout districts}\label{tab:fp}
\begin{tabularx}{\linewidth}{lllllX}\toprule
ID & Entry & Phase years & Units & Final state & First source\\\midrule
""" + rows3 + r"""\bottomrule\end{tabularx}
\end{table}

\begin{figure}[ht]\centering
\includegraphics[width=\linewidth]{fig-footprints.png}
\caption{Documented footprints on 2019 boundaries.}
\end{figure}

\section{Corrections in this version}
Verifying footprints against primary sources changed """ + {1:"one record",2:"two records",3:"three records",4:"four records"}.get(sum(1 for p in P if p["correction"]), "several records") + r""" from version 1.0:
\begin{itemize}
""" + corr + r"""\end{itemize}

\section{Limitations}
\begin{itemize}
\item Secondary sources disagree on dates routinely. Every date should be checked against the primary source named on the programme page before use.
\item Expected directions in the outcome matrix are hypotheses from mechanisms, not findings.
\item Evidence status was assigned by reading the literature cited; it will miss recent and unpublished work.
\item Several bibliography entries could not be verified from this build environment and are marked as such, with search links in place of DOIs.
\item Replication status of published studies has not been assessed.
\end{itemize}

\section{Access and citation}
All files are at \url{https://itssaqib.github.io/pakistan-evidence-catalogue/toolkit/} in CSV, JSON and Stata formats, with a Stata starter kit that includes the crosswalk, heterogeneity-robust estimators and a power calculation (Burlig, Preonas and Woerman 2020). Corrections are invited through the repository's issue forms.

\medskip\noindent Hussain, S. (2026). \emph{Pakistan Evidence Catalogue: staggered district-level programmes for causal impact evaluation}, version """ + META["version"] + r""". \url{https://itssaqib.github.io/pakistan-evidence-catalogue/}

\end{document}
"""
path = os.path.join(OUT, "pec-data-note.tex")
open(path, "w", encoding="utf-8").write(doc)
for _ in range(2):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "pec-data-note.tex"], cwd=OUT, capture_output=True, text=True)
for ext in (".aux", ".log", ".out"):
    try:
        os.remove(os.path.join(OUT, "pec-data-note" + ext))
    except OSError:
        pass
print("pdflatex exit", r.returncode, "| pdf", os.path.getsize(os.path.join(OUT, "pec-data-note.pdf")) // 1024, "KB")
if r.returncode:
    print(r.stdout[-2000:])
