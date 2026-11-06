"""Build the gap table: per (genus, use category) ancient signal vs modern research density (Europe PMC)."""
import json, collections, csv, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import europepmc as ep

CAT_TERMS = {
 "GAST": ["gastric","digestive","diarrhea","dysentery","hepatoprotective","constipation","dyspepsia"],
 "DERM": ["wound healing","skin","dermatitis","ulcer"],
 "GYN": ["menstrual","emmenagogue","uterine","gynecological","lactation"],
 "URO": ["diuretic","urinary","kidney","urolithiasis","bladder"],
 "RESP": ["cough","asthma","bronchitis","expectorant","respiratory"],
 "ANTI": ["antivenom","snake bite","antidote","venom"],
 "NERV": ["epilepsy","analgesic","sedative","headache","anxiety","neuroprotective"],
 "MUSK": ["arthritis","rheumatism","gout","anti-inflammatory","sciatica"],
 "OPHT": ["ophthalmic","conjunctivitis","eye"],
 "FEV": ["fever","antipyretic","malaria"],
 "PARA": ["anthelmintic","antiparasitic","helminth"],
 "ORAL": ["gingivitis","dental","mouthwash","oral"],
 "OTO": ["otitis","ear"],
}
SAFETY = ["toxicity","poisoning","hepatotoxicity","nephrotoxic","carcinogenic","adverse effects"]
MIN_ANCIENT = 2

ext = {e["chapter"]: e for e in json.load(open("data/extractions/rules_all.json"))}
tax = json.load(open("data/lexicon/book3_taxa.json"))
by = collections.defaultdict(list)
for ch, gen in tax.items(): by[gen].append(ch)

rows = []
for gen in sorted(by):
    spans = collections.defaultdict(list)
    for ch in by[gen]:
        for u in ext.get(ch, {"uses": []})["uses"]:
            spans[u["cat"]].append((ch, u["mode"], u["span"]))
    cats = [c for c in spans if c in CAT_TERMS and len(spans[c]) >= MIN_ANCIENT]
    safety = ep.counts([gen], SAFETY)
    for c in cats:
        m = ep.counts([gen], CAT_TERMS[c])
        rows.append({"genus": gen, "category": c, "ancient_statements": len(spans[c]),
                     "chapters": ";".join(sorted({s[0] for s in spans[c]})),
                     "modes": ";".join(sorted({s[1] for s in spans[c]})),
                     "modern_total": m["total"], "modern_clinical": m["clinical"],
                     "safety_total": safety["total"], "example_span": spans[c][0][2]})
    print(gen, len(cats), flush=True)

def label(r):
    if r["modern_clinical"] >= 5: return "supported (clinical evidence exists)"
    if r["modern_total"] >= 30: return "studied, little clinical evidence"
    return "research gap"
for r in rows: r["status"] = label(r)
with open("data/processed/gap_table.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(rows, open("data/processed/gap_table.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(rows), collections.Counter(r["status"] for r in rows))
