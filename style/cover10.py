# Cover tweaks for the 10th-grade key: new first-page cover picture and no second cover page.
# usage: python3 cover10.py <in.docx> <new cover.jpg> <out.docx>
import re, sys, zipfile
from lxml import etree

SRC, COVER, OUT = sys.argv[1:4]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
q = lambda t: "{%s}%s" % (W, t)

zin = zipfile.ZipFile(SRC)
rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))
target = {r.get("Id"): r.get("Target") for r in rels}
doc = etree.fromstring(zin.read("word/document.xml"))
body = doc.find(q("body"))

cover1 = None
for p in list(body)[:3]:
    for d in p.iter("{%s}docPr" % WP):
        name = d.get("name") or ""
        run = d.getparent().getparent().getparent()          # docPr → anchor → drawing → r
        blip = run.find(".//{%s}blip" % A)
        if name == "Cover 1":
            cover1 = "word/" + target[blip.get("{%s}embed" % R)]
        elif name == "Cover 2":                               # second cover page: drop the picture
            run.getparent().remove(run)
            ppr = p.find(q("pPr"))
            for pb in ppr.findall(q("pageBreakBefore")):
                ppr.remove(pb)

# one cover page left → the first answer page is page 2
pn = body.find(q("sectPr")).find(q("pgNumType"))
if pn is not None:
    pn.set(q("start"), "2")

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            data = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif item.filename == cover1:
            data = open(COVER, "rb").read()
        zout.writestr(item, data)
print("ok", OUT, "cover:", cover1)
