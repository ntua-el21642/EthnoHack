"""Assemble demo/data.json from the gap table, prep-mismatch flags, Greek passages and top Europe PMC papers."""
import csv, json, collections, re, sys
sys.path.insert(0, "src")
import europepmc as ep
from evidence_table_terms import CAT_TERMS, TERMS  # light import without running the table build

rows = list(csv.DictReader(open("data/processed/gap_table.csv", encoding="utf-8")))
pm = {(p["genus"], p["category"]): p for p in json.load(open("data/processed/prep_mismatch.json"))}
ext = {e["chapter"]: e for e in json.load(open("data/extractions/rules_all.json"))}
tmap = json.load(open("data/lexicon/taxa_map.json", encoding="utf-8"))
CATNAMES = {"DERM":"Skin & wounds","GAST":"Digestive","GYN":"Gynaecological","URO":"Urinary","RESP":"Respiratory","ANTI":"Antidote / bites",
 "NERV":"Nervous system","MUSK":"Muscle & joint","OTH":"Other","OPHT":"Eye","FOOD":"Food","PARA":"Parasites","OTO":"Ear","ORAL":"Mouth & teeth",
 "FEV":"Fever","LIBI":"Libido","REPE":"Repellent","POIS":"Poison","ANDR":"Andrological","RHI":"Nose","CARD":"Cardiovascular"}
MODES = {"INT":"taken by mouth","EXT":"applied to the skin","CLY":"inserted (enema, pessary, fumigation)"}

def ref(ch):
    b, n = ch.split("_"); return f"{b}.{n}"

out = []
for r in rows:
    g, c = r["genus"], r["category"]
    chs = r["chapters"].split(";")
    passages, seen = [], set()
    for ch in chs:
        for u in ext.get(ch, {"uses": []})["uses"]:
            if u["cat"] != c or u["span"] in seen: continue
            seen.add(u["span"])
            passages.append({"ref": ref(ch), "gr": u["span"], "mode": u["mode"], "part": u["part"],
                             "vehicles": u["vehicles"], "forms": u["forms"]})
    passages = [p for p in passages if len(p["gr"].split()) >= 5]
    passages.sort(key=lambda p: -(len(p["vehicles"]) + len(p["forms"]) > 0))
    heads = sorted({(tmap[ch].get("headword") or ext[ch]["plant_gr"]).strip("·.,; ") for ch in chs if ch in tmap and ch in ext})
    papers = []
    for p in ep.top_abstracts(TERMS.get(g, [g]), CAT_TERMS[c], n=3, sort=None):
        a = (p["abstract"] or "")
        a = re.sub(r"<[^>]+>", "", a)
        papers.append({"pmid": p["pmid"], "title": re.sub(r"<[^>]+>", "", p["title"] or ""), "year": p["year"], "snippet": a[:280] + ("…" if len(a) > 280 else "")})
    m = pm.get((g, c))
    out.append({
        "genus": g, "cat": c, "cat_name": CATNAMES.get(c, c), "heads": heads,
        "n_anc": int(r["ancient_statements"]), "total": int(r["modern_total"]), "clinical": int(r["modern_clinical"]),
        "safety": int(r["safety_total"]), "safety_flag": r["safety_flag"] == "True",
        "status": r["status"], "pct": float(r["modern_pct_rank"]), "priority": float(r["priority"]),
        "conf": r["name_confidence"], "modes": r["modes"].split(";"),
        "passages": passages[:4], "papers": papers,
        "prep": None if not m else {"ancient": m["ancient_prep"], "modern_same": m["modern_studies_with_ancient_prep"],
                                     "modern_alc": m["modern_studies_ethanol_methanol"], "mismatch": m["prep_mismatch"]},
        "query_terms": TERMS.get(g, [g]), "ind_terms": CAT_TERMS[c],
    })

by_cat = collections.defaultdict(lambda: collections.Counter())
for o in out: by_cat[o["cat_name"]][o["status"]] += 1
stats = {"chapters": len(ext), "uses": sum(len(e["uses"]) for e in ext.values()), "genera": len({v["genus"] for v in tmap.values()}),
         "pairs": len(out), "gaps": sum(o["status"] == "research gap" for o in out),
         "prep_checked": len(pm), "prep_flagged": sum(p["prep_mismatch"] for p in pm.values()),
         "by_cat": {k: dict(v) for k, v in by_cat.items()}}
json.dump({"stats": stats, "rows": out}, open("demo/data.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(stats["pairs"], "rows;", stats)
