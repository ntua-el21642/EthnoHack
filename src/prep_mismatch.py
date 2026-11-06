"""Preparation-mismatch detector (the novel part): does modern research on this plant test the PREPARATION
the ancient text prescribes? For the top gap rows: ancient vehicle/form counts from the Greek sentences vs
number of modern studies (Europe PMC, plant in title) that use that vehicle/form, vs the usual modern
solvents (ethanol/methanol/aqueous). Heuristic and explainable, not a verdict."""
import json, collections, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd, europepmc as ep

MODERN = {"wine": ["wine"], "vinegar": ["vinegar"], "oil": ["oil macerate","oleate","infused oil","olive oil"],
          "honey": ["honey"], "milk": ["milk"], "decoction": ["decoction"], "juice": ["juice","fresh sap"],
          "poultice": ["poultice","cataplasm"], "water": ["aqueous extract","infusion","water extract"]}
SOLVENTS = ["ethanol","methanol","hydroalcoholic","ethyl acetate","chloroform","hexane"]
TOP = int(sys.argv[1]) if len(sys.argv) > 1 else 60

ext = {e["chapter"]: e for e in json.load(open("data/extractions/rules_all.json"))}
tmap = json.load(open("data/lexicon/taxa_map.json", encoding="utf-8"))
TERMS = json.load(open("data/lexicon/search_terms.json", encoding="utf-8"))
gap = pd.read_csv("data/processed/gap_table.csv").sort_values("priority", ascending=False)
gap = gap[gap.status != "well studied"].head(TOP)

def plant_filter(terms):
    return "(" + " OR ".join(f'TITLE:"{t}"' for t in terms) + ")"
def count(terms, mod_terms):
    q = plant_filter(terms) + " AND (" + " OR ".join(f'TITLE_ABS:"{t}"' for t in mod_terms) + ")"
    return ep._get({"query": q, "format": "json", "pageSize": 1, "resultType": "lite"})["hitCount"]

rows = []
for _, r in gap.iterrows():
    chs = [c for c, v in tmap.items() if v["genus"] == r.genus]
    cnt = collections.Counter()
    for c in chs:
        for u in ext.get(c, {"uses": []})["uses"]:
            if u["cat"] == r.category:
                for x in u["vehicles"] + u["forms"]: cnt[x] += 1
    anc = [(k, n) for k, n in cnt.most_common() if k in MODERN][:3]
    terms = TERMS.get(r.genus, [r.genus])
    anc_mod = {k: count(terms, MODERN[k]) for k, _ in anc}
    solv = {s: count(terms, [s]) for s in SOLVENTS[:2]}
    solvent_total = sum(solv.values())
    mismatch = bool(anc) and all(v <= 1 for v in anc_mod.values()) and solvent_total >= 5
    rows.append({"genus": r.genus, "category": r.category, "priority": r.priority,
                 "ancient_prep": {k: n for k, n in anc}, "modern_studies_with_ancient_prep": anc_mod,
                 "modern_studies_ethanol_methanol": solv, "prep_mismatch": mismatch})
json.dump(rows, open("data/processed/prep_mismatch.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
m = [x for x in rows if x["prep_mismatch"]]
print(len(rows), "rows;", len(m), "flagged as preparation mismatch")
for x in m[:15]: print(x["genus"], x["category"], x["ancient_prep"], x["modern_studies_with_ancient_prep"], x["modern_studies_ethanol_methanol"])
