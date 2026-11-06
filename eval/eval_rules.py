import json, sys, pandas as pd
ext = {e["chapter"]: e for e in json.load(open("data/extractions/rules_all.json"))}
g = pd.read_excel("data/gold/staub2016_S2.xlsx"); g["ch"] = g.Chapter.str.replace(r"_0+", "_", regex=True)
def prf(P, G):
    tp = len(P & G); p = tp/len(P) if P else 0; r = tp/len(G) if G else 0
    return round(p,2), round(r,2), round(2*p*r/(p+r),2) if p+r else 0.0, tp, len(P), len(G)
def evaluate(chs, label):
    for name, kf in [("category", lambda u: (u["cat"],)), ("category+mode", lambda u: (u["cat"], u["mode"]))]:
        P = {(c,)+kf(u) for c in chs if c in ext for u in ext[c]["uses"]}
        G = {(c, r.Category) + ((r.Mode,) if "mode" in name else ()) for c in chs for _, r in g[g.ch == c].iterrows()}
        print(f"{label:34s} {name:14s} P/R/F1/tp/ext/gold = {prf(P,G)}")
evaluate([f"III_{i}" for i in (2,3,4,5,6,7,8)], "III_2-8 (lexicon tuned on these)")
evaluate(["I_1","I_2","I_3","IV_1","IV_2","IV_3"], "I_1-3,IV_1-3 (held-out, aligned)")
