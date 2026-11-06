"""Indication term lists and search-term overrides shared by evidence_table and the demo builder."""
import json
CAT_TERMS = {
 "GAST": ["gastric","digestive","diarrhea","dysentery","hepatoprotective","constipation","dyspepsia"],
 "DERM": ["wound healing","dermatitis","skin ulcer","burn wound","antifungal skin"],
 "GYN": ["menstrual","emmenagogue","dysmenorrhea","uterine","lactation","labor induction"],
 "URO": ["diuretic","urolithiasis","kidney stone","urinary tract infection","cystitis"],
 "RESP": ["cough","asthma","bronchitis","expectorant","common cold"],
 "ANTI": ["antivenom","snake bite","antidote","venom neutralizing"],
 "NERV": ["epilepsy","analgesic","sedative","headache","anxiolytic","insomnia"],
 "MUSK": ["arthritis","rheumatism","gout","anti-inflammatory","sciatica"],
 "OPHT": ["conjunctivitis","ophthalmic","eye drops","cataract","trachoma"],
 "FEV": ["fever","antipyretic","malaria"],
 "PARA": ["anthelmintic","antiparasitic","helminth"],
 "ORAL": ["gingivitis","periodontitis","dental caries","mouthwash","stomatitis"],
 "OTO": ["otitis","ear infection"],
}

TERMS = json.load(open("data/lexicon/search_terms.json", encoding="utf-8"))
