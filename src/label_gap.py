"""Relative (percentile-based) status + priority score for each (genus, category) row of the gap table.
Thresholds come from the table's own distribution of strict Europe PMC counts, not from absolute truths."""
import pandas as pd, numpy as np, json
t = pd.read_csv("data/processed/gap_table.csv")
p50, p90 = t.modern_total.quantile(.5), t.modern_total.quantile(.9)
def status(r):
    if r.modern_clinical >= 3 or r.modern_total >= p90: return "well studied"
    if r.modern_total > p50 or r.modern_clinical >= 1: return "some research"
    return "research gap"
t["status"] = t.apply(status, axis=1)
t["modern_pct_rank"] = t.modern_total.rank(pct=True).round(3)
# priority: strong ancient signal AND little modern research; safety flag reported separately
t["priority"] = (t.ancient_statements * (1 - t.modern_pct_rank)).round(2)
t["safety_flag"] = t.safety_total >= t.safety_total.quantile(.9)
t = t.sort_values("priority", ascending=False)
t.to_csv("data/processed/gap_table.csv", index=False)
json.dump(t.to_dict("records"), open("data/processed/gap_table.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"thresholds: median={p50}, p90={p90}; clinical>=3 => well studied"); print(t.status.value_counts().to_dict())
print(t.head(10)[["genus","category","ancient_statements","modern_total","modern_clinical","priority","safety_flag","name_confidence"]].to_string(index=False))
