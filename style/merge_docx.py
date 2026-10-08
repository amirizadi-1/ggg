# Appends the body of a second styled answer key to a first one (same reference styles):
# pictures/relationships, list numbering and drawing ids of the second file are remapped;
# the first file keeps its covers, header, footer and page setup.
# usage: python3 merge_docx.py <first.docx> <second.docx> <out.docx>
import copy, os, re, sys, zipfile
from lxml import etree

A_PATH, B_PATH, OUT = sys.argv[1:4]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
q = lambda t: "{%s}%s" % (W, t)

za, zb = zipfile.ZipFile(A_PATH), zipfile.ZipFile(B_PATH)
docA = etree.fromstring(za.read("word/document.xml"))
docB = etree.fromstring(zb.read("word/document.xml"))
relsA = etree.fromstring(za.read("word/_rels/document.xml.rels"))
relsB = {r.get("Id"): r for r in etree.fromstring(zb.read("word/_rels/document.xml.rels"))}
numA = etree.fromstring(za.read("word/numbering.xml"))
numB = etree.fromstring(zb.read("word/numbering.xml"))
bodyA, bodyB = docA.find(q("body")), docB.find(q("body"))

# ---- numbering: append B's abstract numbers and lists with shifted ids
abs_off = 1 + max([int(a.get(q("abstractNumId"))) for a in numA.findall(q("abstractNum"))] or [-1])
num_off = max([int(n.get(q("numId"))) for n in numA.findall(q("num"))] or [0])
first_num = numA.find(q("num"))
for a in numB.findall(q("abstractNum")):
    a = copy.deepcopy(a)
    a.set(q("abstractNumId"), str(int(a.get(q("abstractNumId"))) + abs_off))
    for nsid in a.findall(q("nsid")):
        a.remove(nsid)
    (first_num.addprevious(a) if first_num is not None else numA.append(a))
for n in numB.findall(q("num")):
    n = copy.deepcopy(n)
    n.set(q("numId"), str(int(n.get(q("numId"))) + num_off))
    an = n.find(q("abstractNumId"))
    an.set(q("val"), str(int(an.get(q("val"))) + abs_off))
    numA.append(n)

# ---- body of B
new_files = {}
rid_map = {}
max_doc = max([int(d.get("id")) for d in docA.iter("{%s}docPr" % WP)] or [0])
sectA = bodyA.find(q("sectPr"))
first_stem = True
STEM = re.compile(r"^[۰-۹0-9]+\s*-")
for el in list(bodyB):
    if el.tag == q("sectPr"):
        continue
    el = copy.deepcopy(el)
    for node in el.iter():
        for attr in ("{%s}embed" % "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
                     "{%s}id" % R, "{%s}link" % R):
            old = node.get(attr)
            if old is None or old not in relsB:
                continue
            if old not in rid_map:
                rel = relsB[old]
                target = rel.get("Target")
                new_target = "media/b2_" + os.path.basename(target)
                new_files["word/" + new_target] = zb.read("word/" + target)
                rid = "rIdB2_%d" % (len(rid_map) + 1)
                nr = etree.SubElement(relsA, "{%s}Relationship" % PKG)
                nr.set("Id", rid); nr.set("Type", rel.get("Type")); nr.set("Target", new_target)
                rid_map[old] = rid
            node.set(attr, rid_map[old])
    for d in el.iter("{%s}docPr" % WP):
        max_doc += 1
        d.set("id", str(max_doc))
    for c in el.iter("{%s}cNvPr" % PIC):
        c.set("id", "0")
    for nid in el.iter(q("numId")):
        nid.set(q("val"), str(int(nid.get(q("val"))) + num_off))
    if first_stem and el.tag == q("p") and STEM.match("".join(t.text or "" for t in el.iter(q("t"))).strip()):
        ppr = el.find(q("pPr"))
        if ppr.find(q("pageBreakBefore")) is None:
            kl = ppr.find(q("keepLines"))
            pb = etree.Element(q("pageBreakBefore"))
            (kl.addnext(pb) if kl is not None else ppr.insert(0, pb))
        first_stem = False
    sectA.addprevious(el)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in za.infolist():
        data = za.read(item.filename)
        if item.filename == "word/document.xml":
            data = etree.tostring(docA, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif item.filename == "word/_rels/document.xml.rels":
            data = etree.tostring(relsA, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif item.filename == "word/numbering.xml":
            data = etree.tostring(numA, xml_declaration=True, encoding="UTF-8", standalone=True)
        zout.writestr(item, data)
    for name, data in new_files.items():
        zout.writestr(name, data)
print("merged:", len(new_files), "files,", len(rid_map), "relationships")
