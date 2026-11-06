"""Parse First1KGreek tlg0656.tlg001 (Wellmann ed., CC BY-SA 4.0) into per-chapter Greek text.

Strips the critical apparatus (<note>), deletions (<del>), page breaks. Output keys are
'<ROMAN BOOK>_<chapter n>' (e.g. 'III_4'). Nested chapter divs are separated from their parent.
"""
import json, re, sys
from lxml import etree

NS = {"t": "http://www.tei-c.org/ns/1.0"}
ROMAN = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}


def _strip(tree):
    for tag in ("note", "del", "pb", "gap"):
        for e in tree.xpath(f"//t:{tag}", namespaces=NS):
            parent, prev, tail = e.getparent(), e.getprevious(), e.tail
            if tail:
                if prev is not None:
                    prev.tail = (prev.tail or "") + tail
                else:
                    parent.text = (parent.text or "") + tail
            parent.remove(e)


def parse(path):
    tree = etree.parse(path)
    _strip(tree)
    out = {}
    for book in tree.xpath('//t:div[@subtype="book"]', namespaces=NS):
        for ch in book.xpath('.//t:div[@subtype="chapter"]', namespaces=NS):
            ps = [p for p in ch.xpath(".//t:p", namespaces=NS)
                  if p.xpath('ancestor::t:div[@subtype="chapter"][1]', namespaces=NS)[0] is ch]
            txt = re.sub(r"\s+", " ", " ".join("".join(p.itertext()) for p in ps)).strip()
            txt = re.sub(r"^\d+\s+", "", txt)
            if txt:
                out.setdefault(f"{ROMAN[book.get('n')]}_{ch.get('n')}", []).append(txt)
    return {k: " ".join(v) for k, v in out.items()}


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    res = parse(src)
    json.dump(res, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{len(res)} chapters, {sum(len(v.split()) for v in res.values())} words -> {dst}")
