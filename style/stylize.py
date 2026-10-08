# Applies the «Faraz11_Styled» look to an answer-key .docx:
#   page background + header band + footer page number, navy text, question boxes,
#   navy answer bars, gold tables with banded rows, inline centered pictures.
# usage: python3 stylize.py <unzipped source dir> <styled reference dir> <background.png> <out.docx>
import copy, os, re, shutil, sys, zipfile
from lxml import etree

SRC, REF, BG, OUT = sys.argv[1:5]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
q = lambda t: "{%s}%s" % (W, t)

NAVY, GOLD_LINE, BOX, HEAD, BAND1, BAND2 = "282360", "F0C45F", "FFF8E7", "FFE08A", "FCEFC5", "FFF8E7"
TO_NAVY = {None, "000000", "1F3864", "555555", "444444", "333333", "2F5D9B", "auto"}

doc_path = os.path.join(SRC, "word", "document.xml")
tree = etree.parse(doc_path)
body = tree.getroot().find(q("body"))


def txt(e):
    return "".join(x.text or "" for x in e.iter(q("t")))


def child(parent, tag, before=()):
    """get or create a child element, inserted before the first of `before`"""
    el = parent.find(q(tag))
    if el is None:
        el = etree.Element(q(tag))
        nxt = [c for c in parent if etree.QName(c).localname in before]
        if nxt:
            nxt[0].addprevious(el)
        else:
            parent.append(el)
    return el


PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
             "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
             "sectPr", "pPrChange"]


def pchild(ppr, tag):
    return child(ppr, tag, PPR_ORDER[PPR_ORDER.index(tag) + 1:])


def ppr_of(p):
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = etree.Element(q("pPr"))
        p.insert(0, ppr)
    return ppr


def spacing(p, **kw):
    sp = pchild(ppr_of(p), "spacing")
    for k, v in kw.items():
        if v is None:
            sp.attrib.pop(q(k), None)
        else:
            sp.set(q(k), str(v))


def shade(el_pr, fill, tag="shd", order=None):
    sh = pchild(el_pr, "shd") if order is None else child(el_pr, "shd", order)
    sh.attrib.clear()
    sh.set(q("val"), "clear")
    sh.set(q("color"), "auto")
    sh.set(q("fill"), fill)


def box_borders(p, sides=("top", "right", "left")):
    bdr = pchild(ppr_of(p), "pBdr")
    for s in sides:
        b = child(bdr, s, ())
        b.set(q("val"), "single"); b.set(q("sz"), "7"); b.set(q("space"), "8"); b.set(q("color"), GOLD_LINE)


RPR_AFTER_COLOR = ("spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd",
                   "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath")


def recolor(container, force=None):
    for r in container.iter(q("r")):
        rpr = r.find(q("rPr"))
        if rpr is None:
            rpr = etree.Element(q("rPr"))
            r.insert(0, rpr)
        for h in rpr.findall(q("highlight")):
            rpr.remove(h)
        c = rpr.find(q("color"))
        cur = c.get(q("val")) if c is not None else None
        new = force or (NAVY if cur in TO_NAVY else cur)
        if c is None:
            c = child(rpr, "color", RPR_AFTER_COLOR)
        for a in list(c.attrib):
            if a != q("val"):
                del c.attrib[a]
        c.set(q("val"), new)


def has_drawing(e):
    return e.find(".//" + q("drawing")) is not None or e.find(".//" + q("pict")) is not None


# ------------------------------------------------------------------ anchored pictures → inline, centered
def to_inline(anchor):
    inline = etree.Element("{%s}inline" % WP)
    for k in ("distT", "distB", "distL", "distR"):
        inline.set(k, "0")
    for tag in ("extent", "effectExtent", "docPr", "cNvGraphicFramePr"):
        el = anchor.find("{%s}%s" % (WP, tag))
        if el is not None:
            inline.append(copy.deepcopy(el))
    inline.append(copy.deepcopy(anchor.find("{http://schemas.openxmlformats.org/drawingml/2006/main}graphic")))
    return inline


def picture_para(drawing_runs):
    p = etree.Element(q("p"))
    ppr = etree.SubElement(p, q("pPr"))
    etree.SubElement(ppr, q("keepLines"))
    sp = etree.SubElement(ppr, q("spacing"))
    sp.set(q("before"), "100"); sp.set(q("after"), "100"); sp.set(q("line"), "240"); sp.set(q("lineRule"), "auto")
    etree.SubElement(ppr, q("jc")).set(q("val"), "center")
    for r in drawing_runs:
        p.append(r)
    return p


for p in list(body.iter(q("p"))):
    anchors = [a for a in p.iter("{%s}anchor" % WP)]
    anchors = [a for a in anchors if a.get("behindDoc") != "1"]
    if not anchors:
        continue
    runs = []
    for a in anchors:
        a.getparent().replace(a, to_inline(a))
    for r in list(p.findall(q("r"))):
        if r.find(q("drawing")) is not None:
            p.remove(r)
            runs.append(r)
    if txt(p).strip():
        p.addprevious(picture_para(runs))
    else:
        for r in runs:
            p.append(r)
        ppr = ppr_of(p)
        for k in ("ind",):
            for el in ppr.findall(q(k)):
                ppr.remove(el)
        spacing(p, before=100, after=100, line=240, lineRule="auto")
        pchild(ppr, "jc").set(q("val"), "center")

# ------------------------------------------------------------------ tables
CELLMAR = '<w:tblCellMar xmlns:w="%s"><w:top w:w="85" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>' \
          '<w:bottom w:w="85" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar>' % W
TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize",
               "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"]
TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
              "textDirection", "tcFitText", "vAlign", "hideMark"]


def gold_grid(tbl):
    pr = tbl.find(q("tblPr"))
    b = child(pr, "tblBorders", TBLPR_ORDER[TBLPR_ORDER.index("tblBorders") + 1:])
    for c in list(b):
        b.remove(c)
    for s in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = etree.SubElement(b, q(s))
        e.set(q("val"), "single"); e.set(q("sz"), "4"); e.set(q("space"), "0"); e.set(q("color"), GOLD_LINE)
    old = pr.find(q("tblCellMar"))
    new = etree.fromstring(CELLMAR)
    if old is not None:
        old.addprevious(new); pr.remove(old)
    else:
        child(pr, "tblCellMar", TBLPR_ORDER[TBLPR_ORDER.index("tblCellMar") + 1:]).addprevious(new)
        pr.remove(pr.findall(q("tblCellMar"))[-1])


def cell_fill(tc, fill):
    pr = tc.find(q("tcPr"))
    if pr is None:
        pr = etree.Element(q("tcPr")); tc.insert(0, pr)
    shade(pr, fill, order=TCPR_ORDER[TCPR_ORDER.index("shd") + 1:])
    child(pr, "vAlign", TCPR_ORDER[TCPR_ORDER.index("vAlign") + 1:]).set(q("val"), "center")


def is_data_table(tbl):
    b = tbl.find(q("tblPr") + "/" + q("tblBorders"))
    return b is not None and any(c.get(q("color")) == "8FA9C9" for c in b)


def is_diagram(tbl):
    return tbl.find(q("tblPr") + "/" + q("tblBorders")) is None and tbl.find(".//" + q("tcBorders")) is not None


# ------------------------------------------------------------------ walk the body
STEM = re.compile(r"^[۰-۹0-9]+\s*-\s*\t?")
state = None                      # None | "q" (inside a question) | "a" (inside the answer)
last_box = None
for el in list(body):
    if el.tag == q("tbl"):
        if is_data_table(el):
            gold_grid(el)
            for i, tr in enumerate(el.findall(q("tr"))):
                for tc in tr.findall(q("tc")):
                    cell_fill(tc, HEAD if i == 0 else (BAND1 if i % 2 else BAND2))
            recolor(el)
        elif is_diagram(el):
            recolor(el)
        elif state == "q":
            gold_grid(el)
            for tc in el.iter(q("tc")):
                cell_fill(tc, BOX)
            recolor(el)
            last_box = None
        else:
            recolor(el)
        continue
    if el.tag != q("p"):
        continue
    p, t = el, txt(el).strip()
    ppr = ppr_of(p)
    shd = ppr.find(q("shd"))
    if shd is not None and shd.get(q("fill")) == "1F3864":                    # banner
        shd.set(q("fill"), NAVY)
        spacing(p, before=200, after=120, line=370, lineRule="auto")
        recolor(p, None)
        for r in p.iter(q("r")):                                            # banner runs keep white / gold
            c = r.find(q("rPr") + "/" + q("color"))
            if c is not None and c.get(q("val")) == NAVY:
                c.set(q("val"), "FFFFFF")
        state = "a"
        continue
    if not t and not has_drawing(p):                                        # empty spacer
        spacing(p, before=0, after=20, line=20, lineRule="exact")
        continue
    if has_drawing(p) and not t:                                            # picture
        recolor(p)
        continue
    if STEM.match(t):                                                       # question stem
        state = "q"
        shade(ppr, BOX)
        box_borders(p)
        spacing(p, before=80, after=80, line=280, lineRule="auto")
        pchild(ppr, "keepNext")
        recolor(p)
        continue
    if t.startswith("پاسخ"):                                                # answer bar
        state = "a"
        shade(ppr, NAVY)
        spacing(p, before=150, after=120, line=340, lineRule="auto")
        pchild(ppr, "keepNext")
        recolor(p, "FFFFFF")
        continue
    if state == "q":                                                        # options / items of the question
        shade(ppr, BOX)
        spacing(p, after=65)
        pchild(ppr, "keepNext")
        recolor(p)
        continue
    spacing(p, after=65)                                                    # explanation, headings, sources …
    if t.startswith(("بررسی", "جدول جمع", "نمودار")) and len(t) < 40:
        pchild(ppr, "keepNext")
    recolor(p)

# ------------------------------------------------------------------ header / footer / background
rels_path = os.path.join(SRC, "word", "_rels", "document.xml.rels")
rels = etree.parse(rels_path)
hdr_target = None
for rel in rels.getroot():
    if rel.get("Type").endswith("/header"):
        hdr_target = rel.get("Target")
    if rel.get("Type").endswith("/footer"):
        rel.getparent().remove(rel)
shutil.copy(os.path.join(REF, "word", "header1.xml"), os.path.join(SRC, "word", hdr_target))
os.makedirs(os.path.join(SRC, "word", "_rels"), exist_ok=True)
shutil.copy(os.path.join(REF, "word", "_rels", "header1.xml.rels"),
            os.path.join(SRC, "word", "_rels", os.path.basename(hdr_target) + ".rels"))
shutil.copy(BG, os.path.join(SRC, "word", "media", "page_design.png"))
shutil.copy(os.path.join(REF, "word", "footer1.xml"), os.path.join(SRC, "word", "footer_design.xml"))
fr = etree.SubElement(rels.getroot(), "{%s}Relationship" % PKG)
fr.set("Id", "rIdFooterDesign")
fr.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer")
fr.set("Target", "footer_design.xml")
rels.write(rels_path, xml_declaration=True, encoding="UTF-8", standalone=True)

sect = body.find(q("sectPr"))
ref_sect = etree.parse(os.path.join(REF, "word", "document.xml")).getroot().find(q("body")).find(q("sectPr"))
for f in sect.findall(q("footerReference")):
    sect.remove(f)
fref = etree.Element(q("footerReference"))
fref.set(q("type"), "default"); fref.set("{%s}id" % R, "rIdFooterDesign")
sect.find(q("headerReference")).addnext(fref)
for tag in ("pgMar",):
    old = sect.find(q(tag))
    old.addprevious(copy.deepcopy(ref_sect.find(q(tag)))); sect.remove(old)
pn = sect.find(q("pgNumType"))
if pn is not None:
    pn.set(q("start"), "1")

ct_path = os.path.join(SRC, "[Content_Types].xml")
ct = open(ct_path, encoding="utf-8").read()
if "footer_design.xml" not in ct:
    ct = ct.replace("</Types>", '<Override PartName="/word/footer_design.xml" ContentType="application/'
                    'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
if not re.search(r'Extension="png"', ct, re.I):
    ct = ct.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1)
open(ct_path, "w", encoding="utf-8").write(ct)

tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(ct_path, "[Content_Types].xml")
    for base, _, files in os.walk(SRC):
        for f in sorted(files):
            full = os.path.join(base, f)
            rel = os.path.relpath(full, SRC)
            if rel != "[Content_Types].xml":
                z.write(full, rel)
print("ok", OUT)
