"""Pair-level F1 of extracted (genus, category[, mode]) against Staub 2016 gold.
usage: python eval/pair_f1.py data/extractions/<file>.json --aligned   (chapter-level; only for aligned chapters)
"""
import json, sys, pandas as pd
ext = json.load(open(sys.argv[1]))
g = pd.read_excel("data/gold/staub2016_S2.xlsx")
g["ch"] = g.Chapter.str.replace(r"_0+", "_", regex=True)
g["genus"] = g.Taxon.str.split("_").str[0]
def prf(P, G):
    tp = len(P & G); p = tp / len(P) if P else 0; r = tp / len(G) if G else 0
    return p, r, (2*p*r/(p+r) if p+r else 0), tp, len(P), len(G)
for label, key in [("(genus,category)", lambda g_, c, m: (g_, c)), ("(genus,category,mode)", lambda g_, c, m: (g_, c, m))]:
    P, G = set(), set()
    for e in ext:
        for u in e["uses"]:
            P.add((e["chapter"],) + key(e["genus"], u["cat"], u["mode"]))
    for ch in {e["chapter"] for e in ext}:
        for _, r in g[g.ch == ch].iterrows():
            G.add((ch,) + key(r.genus, r.Category, r.Mode))
    p, r, f, tp, np_, ng = prf(P, G)
    print(f"{label}: P={p:.2f} R={r:.2f} F1={f:.2f}  (tp={tp}, extracted={np_}, gold={ng})")
