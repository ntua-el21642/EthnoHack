"""Free, reproducible baseline extractor: Greek chapter -> (category, mode, part) use records.
Lexicon of indication stems (accent/case-folded, prefix match) + keyword rules for mode and plant part.
Categories follow Staub et al. 2016 codes so the output is directly comparable.
"""
import json, re, sys, unicodedata


def fold(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("ς", "σ")

# indication stems (already folded form is computed at load) -> category. Order = priority for overlapping stems.
LEX = {
 "ORAL": ["οδοντ","ουλα","ουλων","στοματ","αφθ","παρισθμ","ουλα"],
 "OTO": ["ωτ","ωταλγ","ακο"],
 "OPHT": ["οφθαλμ","πτερυγ","αμβλυωπ","υπωπι","οφθαλμι","κορη","ονυχ","ἀργεμ"],
 "RESP": ["βηχ","ασθμ","θωρακ","πνευμον","φθισ","ορθοπνοι","δυσπνοι","πτυσ","αιμοπτυ","πλευρ","ἀρτηρι","αρτηρι","φωνη","βραγχ","ὑποχωρ"],
 "URO": ["ουρ","νεφρ","κυστ","λιθ","στραγγουρ","δυσουρ","διουρ","ψαμμ"],
 "GYN": ["υστερ","εμμην","γυναικ","λοχει","εμβρυ","μητρ","κυησ","εκτρωμ","γαλα","καταμηνι","μαστ"],
 "ANDR": ["ορχ","αιδοι"],
 "ANTI": ["θηριοδηκτ","δηγμ","ερπετ","ιοβολ","ιοδηκτ","θηριακ","αλεξιφαρμακ","φαλαγγ","σκορπι","εχιδν","θανασιμ"],
 "FEV": ["πυρετ","ριγ","περιοδ","ριγοπυρετ"],
 "PARA": ["ελμιν","ασκαριδ","πλατειαν"],
 "NERV": ["νευρ","επιληπ","παραλυ","κεφαλαλγ","κεφαλ","λιθαργ","φρενιτ","μανι","κωματ","υπν","αγρυπν"],
 "MUSK": ["ισχιαδ","αρθριτ","ποδαγρ","ρηγμ","στρεμμ","σπασμ","αρθρ","ισχι","οσφυ","πτωματ","ραμμ"],
 "GAST": ["στομαχ","κοιλι","δυσεντερ","ηπατ","σπλην","λυγμ","στροφ","κολικ","εμπνευματ","φυσ","εμετ","ναυτι","υποχονδρ","ειλε","τενεσμ","διαρρο","χολ","ελκωσ","κοιλιακ","αναγωγ"],
 "DERM": ["ελκ","τραυμ","λειχην","αλφ","ψωρ","εξανθημ","πελιωμ","εφηλ","αλωπεκ","τριχ","ερυσιπελ","ερπητ","φλεγμον","οιδημ","καυμ","εγκαυμ","γαγγραιν","σηπεδον","ακροχορδον","θυμ","σκολοπ","ακιδ","συκ","χειμετλ","κηρι","πυρκαι","δερμ","σαρκ","ιχωρ","ουλη","κονδυλωμ","ψυδρακ","λεπρ","φακ","ξυρ"],
 "CARD": ["καρδι","συγκοπ","παλμ"],
 "POIS": ["δηλητηρ","κωνει","μυκητ","θανασιμον φαρμακ"],
}
STEMS = [(cat, [fold(x) for x in stems]) for cat, stems in LEX.items()]

MODE_RULES = [  # (mode, stems) checked in order
 ("CLY", ["εγκλυσμ","κλυζ","κλυστ","πεσσ","προσθετ","προστιθ","προστεθ","προσκειμεν","κολλυρ","μητρας εγχ"]),
 ("FUMI", ["θυμιαμ","θυμια","υποθυμι","καπνιζ","ὑποκαπνι","υποκαπν","εμφυσ"]),
 ("EXT", ["καταπλασσ","επιτιθ","επιτεθ","περιχρι","καταχρι","επιχρι","χριομεν","επιχριομεν","επιπασσ","καταπασ","επιτιθεμεν","κατακλιν","προσφυμα","ενσταζ","ενσταξ","μετ μελιτος","ανατριβ","λουτρ","επιδεσ","επιθεμ","ακραν","αλειφ","σμηκτ","ειλικρινεσ","κατακαι"]),
 ("INT", ["πινομεν","ποθει","ποθεισ","πιν","ποτιζ","διδομεν","προσφερ","ροφ","βρωθ","εσθιομεν","κατεσθιομεν","διαμασ","λαμβανομεν","ποσιμ","καταποθ","πεπον"]),
]
PART_RULES = [
 ("SUBT", ["ριζ"]), ("SEED", ["σπερμ","κοκκ"]), ("FRU", ["καρπ"]), ("LEAF", ["φυλλ"]),
 ("FLOW", ["ανθ","ανθη"]), ("BARK", ["φλοι"]), ("EXUD", ["οπον","οποσ","δακρυ","κομμι","ρητιν","χυλ"]),
 ("HERB", ["βοτανη","ποα","κλων","κλημ","κλαδ"]), ("OIL", ["ελαιο"]), ("WOOD", ["ξυλ"]),
]
VEHICLES = {"wine": ["οινο","οιν"], "vinegar": ["οξει","οξους","οξος","οξυ"], "water": ["υδατ","υδωρ","υδαρ"],
            "honey": ["μελι","μελιτ","οξυμελ"], "oil": ["ελαι"], "milk": ["γαλακτ","γαλα"], "barley meal": ["αλφιτ"], "wax": ["κηρ"],
            "rose oil": ["ροδινο"], "fat": ["στεατ","αδεπ","λιπ"]}
FORMS = {"decoction": ["αφεψ","εψηθ","εψομεν","αφεψημα","αποζεμ"], "juice": ["χυλ","οπο"], "fresh": ["χλωρ","προσφατ"],
         "dried": ["ξηρ","αυανθ"], "ash": ["τεφρ","κατακαυθ","κεκαυμεν"], "soaked/macerated": ["αποβρεχ","βρεχ","προβραχ","διιει"],
         "poultice": ["καταπλασσ","καταπλασμ"], "pounded": ["κοπτ","κοπεισ","λειοτριβ","λειω","τριβ","κοψας"], "pessary": ["πεσσ"],
         "ointment/salve": ["κηρωτ","μαλαγμ","αλειφ","χρισμ","λιπαρ"]}

def prep_features(f):
    v = [k for k, st in VEHICLES.items() if any(re.search(r"(?<![α-ω])" + re.escape(x), f) for x in st)]
    fo = [k for k, st in FORMS.items() if any(re.search(r"(?<![α-ω])" + re.escape(x), f) for x in st)]
    return v, fo

SPLIT = re.compile(r"[·.;]|·")

def first(token_list, text, default=None):
    for lab, stems in token_list:
        if any(re.search(r"(?<![α-ω])" + re.escape(s), text) for s in stems):
            return lab
    return default

def extract_chapter(text):
    sentences = [s.strip() for s in SPLIT.split(text) if s.strip()]
    uses, last_mode, last_part = [], "INT", None
    for si, s in enumerate(sentences):
        if si == 0 and len(s.split()) <= 2: continue   # headword only
        f = fold(s)
        mode = first(MODE_RULES, f, last_mode)
        part = first(PART_RULES, f, last_part)
        last_mode = mode if first(MODE_RULES, f) else last_mode
        last_part = part
        cats = []
        for cat, stems in STEMS:
            if any(re.search(r"(?<![α-ω])" + re.escape(st), f) for st in stems):
                cats.append(cat)
        # one statement may carry several categories; keep all
        for c in cats:
            v, fo = prep_features(f)
            uses.append({"cat": c, "mode": mode, "part": part or "?", "span": s[:320], "vehicles": v, "forms": fo})
    return uses

def run(src, dst):
    d = json.load(open(src, encoding="utf-8"))
    out = []
    for k, txt in d.items():
        if k.endswith("preface") or "_pre" in k: continue
        out.append({"chapter": k, "plant_gr": txt.split()[0].strip("·.,;"), "uses": extract_chapter(txt)})
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False)
    n = sum(len(e["uses"]) for e in out)
    print(f"{len(out)} chapters, {n} use-records -> {dst}")

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
