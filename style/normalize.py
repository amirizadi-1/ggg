# Applies the global spelling/punctuation rules (docxtext.norm) to every paragraph of an unzipped .docx.
# usage: python3 normalize.py <unzipped dir> [change log]
import os, sys
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from docxtext import q, text_of, retext, ensure_rtl, norm

path = os.path.join(sys.argv[1], "word", "document.xml")
tree = etree.parse(path)
log = []
for p in tree.getroot().iter(q("p")):
    old = text_of(p)
    new = norm(old)
    if new != old:
        retext(p, new)
        log.append("  - %s\n  + %s" % (old, new))
    for r in p.iter(q("r")):
        ensure_rtl(r)
tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8").write("\n".join(log))
print("normalized", len(log), "paragraphs")
