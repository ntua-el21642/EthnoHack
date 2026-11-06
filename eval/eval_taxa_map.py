"""Pair-level (genus, category[, mode]) eval over ALL books using the LSJ/manual taxa map.
Gold rows are matched by genus (Staub chapter numbers are not comparable)."""
import json, collections, sys, pandas as pd
src = sys.argv[1] if len(sys.argv) > 1 else "all"   # all | LSJ | high
ext = {e["chapter"]: e for e in json.load(open("data/extractions/rules_all.json"))}
tm = json.load(open("data/lexicon/taxa_map.json"))
g = pd.read_excel("data/gold/staub2016_S2.xlsx"); g["genus"] = g.Taxon.str.split("_").str[0]
by = collections.defaultdict(list)
for ch, v in tm.items():
    if src == "all" or v["source"] == src or (src == "high" and v["confidence"] == "high"): by[v["genus"]].append(ch)
use = [x for x in by if x in set(g.genus)]
def run(name, kf):
    P = {(x,)+kf(u) for x in use for ch in by[x] if ch in ext for u in ext[ch]["uses"]}
    G = {(x,)+kf((r.Category, r.Mode) and {"cat": r.Category, "mode": r.Mode}) for x in use for _, r in g[g.genus == x].iterrows()}
    tp = len(P & G); p = tp/len(P); r = tp/len(G)
    print(f"{src:5s} genera={len(use):3d} {name:14s} P={p:.2f} R={r:.2f} F1={2*p*r/(p+r):.2f} (tp={tp}, ext={len(P)}, gold={len(G)})")
run("category", lambda u: (u["cat"],)); run("category+mode", lambda u: (u["cat"], u["mode"]))
