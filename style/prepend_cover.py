# Copies the two cover paragraphs (full-page pictures «Cover 1» and «Cover 2», the second one ending the
# cover section) of a Faraz booklet to the start of another unzipped .docx.
# usage: python3 prepend_cover.py <booklet.docx> <unzipped target dir>
import copy, os, re, sys, zipfile
from lxml import etree

BOOK, DST = sys.argv[1:3]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
q = lambda t: "{%s}%s" % (W, t)

z = zipfile.ZipFile(BOOK)
src_body = etree.fromstring(z.read("word/document.xml")).find(q("body"))
src_rels = {r.get("Id"): r.get("Target") for r in etree.fromstring(z.read("word/_rels/document.xml.rels"))}
covers = []
for p in list(src_body)[:3]:
    names = [d.get("name") for d in p.iter("{%s}docPr" % WP)]
    if any(n in ("Cover 1", "Cover 2") for n in names):
        covers.append(copy.deepcopy(p))

doc_path = os.path.join(DST, "word", "document.xml")
tree = etree.parse(doc_path)
body = tree.getroot().find(q("body"))
rels_path = os.path.join(DST, "word", "_rels", "document.xml.rels")
rels = etree.parse(rels_path)
os.makedirs(os.path.join(DST, "word", "media"), exist_ok=True)
for i, p in enumerate(covers, 1):
    for blip in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
        old = blip.get("{%s}embed" % R)
        target = src_rels[old]
        name = "media/cover%d%s" % (i, os.path.splitext(target)[1])
        open(os.path.join(DST, "word", name), "wb").write(z.read("word/" + target))
        rid = "rIdCover%d" % i
        rel = etree.SubElement(rels.getroot(), "{%s}Relationship" % PKG)
        rel.set("Id", rid); rel.set("Target", name)
        rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
        blip.set("{%s}embed" % R, rid)
for p in reversed(covers):
    body.insert(0, p)
tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)
rels.write(rels_path, xml_declaration=True, encoding="UTF-8", standalone=True)
ct_path = os.path.join(DST, "[Content_Types].xml")
ct = open(ct_path, encoding="utf-8").read()
for ext, typ in (("jpg", "image/jpeg"), ("jpeg", "image/jpeg"), ("png", "image/png")):
    if not re.search(r'Extension="%s"' % ext, ct, re.I):
        ct = ct.replace("<Default ", '<Default Extension="%s" ContentType="%s"/><Default ' % (ext, typ), 1)
open(ct_path, "w", encoding="utf-8").write(ct)
print("covers added:", len(covers))
