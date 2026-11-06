"""Minimal Europe PMC client: research-density counts split by evidence tier + citable abstracts."""
import json, os, time, hashlib, requests

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CACHE = os.path.join(os.path.dirname(__file__), "..", ".cache", "epmc")
os.makedirs(CACHE, exist_ok=True)

TIERS = {
    "total": "",
    "clinical": ' AND (PUB_TYPE:"Randomized Controlled Trial" OR PUB_TYPE:"Clinical Trial" OR PUB_TYPE:"Meta-Analysis" OR PUB_TYPE:"Systematic Review")',
}


def _get(params):
    key = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()
    fp = os.path.join(CACHE, key + ".json")
    if os.path.exists(fp):
        return json.load(open(fp))
    last = None
    for attempt in range(6):
        try:
            r = requests.get(BASE, params=params, timeout=30)
            if r.status_code == 200:
                data = r.json(); json.dump(data, open(fp, "w")); time.sleep(0.15); return data
            last = r
        except requests.RequestException as ex:  # proxy hiccups: back off and retry
            last = ex
        time.sleep(2 * (attempt + 1))
    if isinstance(last, Exception): raise last
    last.raise_for_status()


EXCLUDE_TITLE = ["cancer","carcinoma","tumor","tumour","nanoparticle","nanoparticles","feed additive","pollen","allergen","broiler","poultry","growth performance"]


EXCLUDE_TITLE_ABS = ["cattle","dairy cows","calves","fish","aquaculture","germination","seedling","nematode","sp. nov.","pollen","allergic rhinitis","immunotherapy","retracted","RETRACTED","rabbits fed","broiler"]
EXCLUDE_TITLE += ["RETRACTED","retraction","correction"]


def build_query(plant_terms, indication_terms, strict=True):
    """strict: plant name must be in the TITLE (paper is about the plant), indication in title/abstract,
    and papers about cancer/nanoparticles/feed/pollen are excluded (not the traditional use)."""
    if strict:
        p = " OR ".join(f'TITLE:"{t}"' for t in plant_terms)
        i = " OR ".join(f'TITLE_ABS:"{t}"' for t in indication_terms)
        ex = " OR ".join(f'TITLE:"{t}"' for t in EXCLUDE_TITLE)
        exa = " OR ".join(f'TITLE_ABS:"{t}"' for t in EXCLUDE_TITLE_ABS)
        return f"({p}) AND ({i}) AND NOT ({ex}) AND NOT ({exa})"
    return build_query_loose(plant_terms, indication_terms)


def build_query_loose(plant_terms, indication_terms):
    # restrict to title/abstract: bare terms also match full text/reference lists (noise)
    p = " OR ".join(f'TITLE_ABS:"{t}"' for t in plant_terms)
    i = " OR ".join(f'TITLE_ABS:"{t}"' for t in indication_terms)
    return f"({p}) AND ({i})"


def counts(plant_terms, indication_terms):
    q = build_query(plant_terms, indication_terms)
    out = {}
    for tier, extra in TIERS.items():
        d = _get({"query": q + extra, "format": "json", "pageSize": 1, "resultType": "lite"})
        out[tier] = d["hitCount"]
    return out


def top_abstracts(plant_terms, indication_terms, n=5, sort="CITED desc"):
    q = build_query(plant_terms, indication_terms)
    d = _get({"query": q + " AND HAS_ABSTRACT:Y", "format": "json", "pageSize": n,
              "resultType": "core", **({"sort": sort} if sort else {})})
    return [{"pmid": r.get("pmid"), "title": r.get("title"), "year": r.get("pubYear"),
             "abstract": r.get("abstractText"), "pubTypes": (r.get("pubTypeList") or {}).get("pubType")}
            for r in d.get("resultList", {}).get("result", [])]
