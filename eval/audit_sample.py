import sys, json, re
sys.path.insert(0, "src")
import pandas as pd, europepmc as ep
ns = {"__file__": "src/evidence_table.py"}
exec(open("src/evidence_table.py").read().split("MIN_ANCIENT")[0], ns); CAT = ns["CAT_TERMS"]
TERMS = json.load(open("data/lexicon/search_terms.json", encoding="utf-8"))
t = pd.read_csv("data/processed/gap_table.csv")
sample = t[t.modern_total > 0].sample(30, random_state=int(sys.argv[1]) if len(sys.argv) > 1 else 7)
out = []
for i, (_, r) in enumerate(sample.iterrows()):
    pt = TERMS.get(r.genus, [r.genus]); q = ep.build_query(pt, CAT[r.category])
    d = ep._get({"query": q + " AND HAS_ABSTRACT:Y", "format": "json", "pageSize": 3, "resultType": "core"})
    res = d.get("resultList", {}).get("result", [])
    print(f"\n#{i} {r.genus}/{r.category} total={r.modern_total}")
    for x in res:
        print("  -", x.get("pubYear") or "", (x.get("title") or "")[:95])
    out.append({"i": i, "genus": r.genus, "category": r.category, "papers": [{"pmid": x.get("pmid"), "title": x.get("title")} for x in res]})
json.dump(out, open(f"eval/relevance_audit_sample_seed{sys.argv[1] if len(sys.argv)>1 else 7}.json", "w"), ensure_ascii=False)
