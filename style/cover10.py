# Cover tweaks for the 10th-grade key: new first-page cover picture, and the second cover page replaced
# by a full-page picture (or removed when no picture is given).
# usage: python3 cover10.py <in.docx> <new cover.jpg|-> <out.docx> [page-2 picture.jpg]
import os, re, sys, zipfile
from lxml import etree

SRC, COVER, OUT = sys.argv[1:4]
PAGE2 = sys.argv[4] if len(sys.argv) > 4 else None
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
PAGE2_NAME = "media/page2_credits" + (os.path.splitext(PAGE2)[1].lower() if PAGE2 else "")
for p in list(body)[:3]:
    for d in p.iter("{%s}docPr" % WP):
        name = d.get("name") or ""
        run = d.getparent().getparent().getparent()          # docPr → anchor → drawing → r
        blip = run.find(".//{%s}blip" % A)
        if name == "Cover 1":
            cover1 = "word/" + target[blip.get("{%s}embed" % R)]
        elif name == "Cover 2" and PAGE2:                     # second page: the given full-page picture
            rel = etree.SubElement(rels, "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
            rel.set("Id", "rIdPage2"); rel.set("Target", PAGE2_NAME)
            rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
            blip.set("{%s}embed" % R, "rIdPage2")
        elif name == "Cover 2":                               # no picture: drop the second cover page
            run.getparent().remove(run)
            ppr = p.find(q("pPr"))
            for pb in ppr.findall(q("pageBreakBefore")):
                ppr.remove(pb)
            pn = body.find(q("sectPr")).find(q("pgNumType"))
            if pn is not None:
                pn.set(q("start"), "2")

ct = zin.read("[Content_Types].xml").decode("utf-8")
if PAGE2 and not re.search(r'Extension="jpg"', ct, re.I):
    ct = ct.replace("<Default ", '<Default Extension="jpg" ContentType="image/jpeg"/><Default ', 1)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            data = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif item.filename == "word/_rels/document.xml.rels":
            data = etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif item.filename == "[Content_Types].xml":
            data = ct.encode("utf-8")
        elif item.filename == cover1 and COVER != "-":
            data = open(COVER, "rb").read()
        zout.writestr(item, data)
    if PAGE2:
        zout.write(PAGE2, "word/" + PAGE2_NAME)
print("ok", OUT, "cover:", cover1, "page 2:", PAGE2 or "removed")
