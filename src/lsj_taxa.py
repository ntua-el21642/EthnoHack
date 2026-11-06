"""Ready-made name->taxon: look up each Dioscorides headword in the Liddell-Scott-Jones lexicon
(Perseus, CC BY-SA) and extract Latin binomials/genera from the entry. LSJ files are downloaded
separately (see CLAUDE.md); keys are Beta Code, so Greek headwords are transliterated to match."""
import json, re, sys, glob, unicodedata, collections

B = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", "abgdezhqiklmncoprstufxyw"))
def to_key(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("ς", "σ")
    return "".join(B.get(c, "") for c in s)
def lsj_key(k):
    return re.sub(r"[^a-z]", "", k.lower())

def headwords(chapters_json):
    d = json.load(open(chapters_json, encoding="utf-8"))
    hw = collections.defaultdict(list)
    for ch, txt in d.items():
        tok = re.sub(r"[·.,;()]", "", txt.split()[0]) if txt.split() else ""
        if tok and re.search(r"[α-ωΑ-Ω]", tok):
            hw[to_key(tok)].append(ch)
    return hw

LAT = re.compile(r"\b([A-Z][a-z]{3,})(?:\s+([a-z]{3,}))?")
STOP = set("Theophr Hippocr Dsc Diosc Plin Gal Ath Nic Hdt Hom Arist Thphr Orph Ar Eur Soph Pl Hp Dioscorides Greek Latin Gloss Hsch Suid Ael Plut Strab Pherecr Sapph Alcm Cratin Eub Nic".split())

def scan(lsj_glob, wanted):
    hits = collections.defaultdict(list)
    for fn in sorted(glob.glob(lsj_glob)):
        t = open(fn, encoding="utf-8").read()
        for m in re.finditer(r'<entryFree[^>]*key="([^"]*)"[^>]*>(.*?)</entryFree>', t, re.S):
            k = lsj_key(m.group(1))
            if k not in wanted: continue
            body = re.sub(r"<foreign lang=\"greek\".*?</foreign>", " ", m.group(2), flags=re.S)
            body = re.sub(r"<bibl.*?</bibl>", " ", body, flags=re.S)
            txt = re.sub(r"<[^>]+>", " ", body)
            cands = []
            for g, s in LAT.findall(txt):
                if g in STOP: continue
                cands.append(f"{g} {s}".strip())
            plantish = bool(re.search(r"\b(plant|herb|tree|shrub|wort|flower|grass|root|fruit|resin|gum|juice|seed|bulb)\b", txt))
            hits[k].append({"lsj_key": m.group(1), "plantish": plantish, "latin": cands[:8], "gloss": re.sub(r"\s+", " ", txt)[:160]})
    return hits

if __name__ == "__main__":
    hw = headwords("data/processed/dio_chapters.json")
    hits = scan(sys.argv[1], set(hw))
    out = {k: {"chapters": hw[k], "entries": hits.get(k, [])} for k in hw}
    json.dump(out, open("data/lexicon/lsj_candidates.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(len(hw), "headword keys;", sum(1 for k in out if out[k]["entries"]), "found in LSJ;",
          sum(1 for k in out if any(e["latin"] and e["plantish"] for e in out[k]["entries"])), "with Latin names")
