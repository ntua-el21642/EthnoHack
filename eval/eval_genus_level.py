"""Book III pair-level eval independent of chapter numbering: link Wellmann chapters to Staub rows by genus
(genus mapping = hand-made, data/lexicon/book3_taxa.json, medium confidence)."""
import json, collections, pandas as pd
ext = {e["chapter"]: e for e in json.load(open("data/extractions/rules_all.json"))}
tax = json.load(open("data/lexicon/book3_taxa.json"))
g = pd.read_excel("data/gold/staub2016_S2.xlsx")
g = g[g.Chapter.str.startswith("III_")].copy(); g["genus"] = g.Taxon.str.split("_").str[0]
gold_genera = set(g.genus)
by = collections.defaultdict(list)
for ch, gen in tax.items():
    by[gen].append(ch)
def prf(P, G):
    tp = len(P & G); p = tp/len(P) if P else 0; r = tp/len(G) if G else 0
    return round(p,2), round(r,2), round(2*p*r/(p+r),2) if p+r else 0.0, tp, len(P), len(G)
use = [gen for gen in by if gen in gold_genera]
print("genera mapped:", len(by), "| also in Staub Book III:", len(use))
for name, kf in [("category", lambda c,m: (c,)), ("category+mode", lambda c,m: (c,m))]:
    P = {(gen,)+kf(u["cat"],u["mode"]) for gen in use for ch in by[gen] if ch in ext for u in ext[ch]["uses"]}
    G = {(gen,)+kf(r.Category, r.Mode) for gen in use for _, r in g[g.genus==gen].iterrows()}
    print(name, "P/R/F1/tp/ext/gold =", prf(P,G))
