"""Combine manual Book-III map with LSJ-derived names. LSJ-only mappings must look like a plant chapter."""
import json, sys, collections, re
sys.path.insert(0, "src")
from lsj_taxa import to_key
import pandas as pd
L = json.load(open("data/lexicon/lsj_candidates.json")); man = json.load(open("data/lexicon/book3_taxa.json"))
d = json.load(open("data/processed/dio_chapters.json"))
staub_gen = set(pd.read_excel("data/gold/staub2016_S2.xlsx").Taxon.str.split("_").str[0])
PLANTY = re.compile(r"ῥίζ|ρίζ|φύλλ|καρπ|καυλ|ἄνθ|ἀνθ|βοτάν|δένδρ|θάμν|σπέρμ|κλῆμ|κλων|φυτ")
def lsj_g(k):
    c = collections.Counter()
    for x in L.get(k, {}).get("entries", []):
        for t in x["latin"]:
            g = t.split()[0]
            if g in staub_gen: c[g] += 1
    return c
out = {}
for ch, txt in d.items():
    if not txt.split(): continue
    tok = txt.split()[0].strip("·.,;"); g = lsj_g(to_key(tok)); m = man.get(ch)
    top = g.most_common(1)[0][0] if g else None
    if m and top: out[ch] = dict(genus=m, lsj=top, source="manual+LSJ", confidence="high" if m in g else "review")
    elif m: out[ch] = dict(genus=m, source="manual", confidence="medium")
    elif top and PLANTY.search(txt[:700]): out[ch] = dict(genus=top, source="LSJ", confidence="medium")
    if ch in out: out[ch]["headword"] = tok
json.dump(out, open("data/lexicon/taxa_map.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(out), dict(collections.Counter((v["source"], v["confidence"]) for v in out.values())), "genera", len({v["genus"] for v in out.values()}))
