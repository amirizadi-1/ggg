# Builds a completed answer key from a source .docx:
# fixes spelling/punctuation, then adds to every question
#   1) an option-review table right after the answer line,
#   2) a summary table and 3) a chart section (PNG charts) after the explanation.
# usage: python3 buildkey.py <config module> <unzipped source docx dir> <out.docx> <charts dir> [change log]
# The config module (fixes11.py, fixes51.py) provides TXT, DELETE, ANSWER, END, MOVES and Q.
import copy, importlib, os, re, struct, sys, zipfile
from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsl
from docxtext import q, text_of, retext, ensure_rtl, norm, make_rtl, FA
CFG = importlib.import_module(sys.argv[1])
TXT, DELETE, ANSWER, END, MOVES, Q = CFG.TXT, CFG.DELETE, CFG.ANSWER, CFG.END, CFG.MOVES, CFG.Q

SRC_DIR, OUT, CHART_DIR = sys.argv[2], sys.argv[3], sys.argv[4]
LOG = sys.argv[5] if len(sys.argv) > 5 else None
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"

doc_path = os.path.join(SRC_DIR, "word", "document.xml")
tree = etree.parse(doc_path)
root = tree.getroot()
body = root.find(q("body"))
orig = list(body)
NSDECL = " ".join('xmlns:%s="%s"' % (k, v) for k, v in root.nsmap.items() if k)


def E(xml):
    return etree.fromstring("<x %s>%s</x>" % (NSDECL, xml))[0]


# ------------------------------------------------------------------ addressing
def get(key):
    if key.startswith("T"):
        t, k = key[1:].split(":")
        tc = orig[int(t)].findall(".//" + q("tc"))[0]
        return tc.findall(q("p"))[int(k)]
    return orig[int(key)]


# keep the anchors before anything moves
ANS_EL = {n: get(k) for n, k in ANSWER.items()}
END_EL = {n: (get(k) if k else None) for n, k in END.items()}

# ------------------------------------------------------------------ 1. explicit corrections
log = []
explicit = set()
for key, new in TXT.items():
    p = get(key)
    assert p.tag == q("p"), key
    old = text_of(p)
    retext(p, new)
    explicit.add(id(p))
    log.append("[%s]\n  - %s\n  + %s" % (key, old, new))

for key in DELETE:
    p = get(key)
    log.append("[%s] (deleted)\n  - %s" % (key, text_of(p)))
    p.getparent().remove(p)

# paragraphs typed in the wrong place
for key, before in getattr(CFG, "MOVE_BEFORE", {}).items():
    get(before).addprevious(get(key))

# answer paragraphs that sit inside a question table → move them below the table
moved = []
for qn, (tbl, first) in MOVES.items():
    tc = orig[tbl].findall(".//" + q("tc"))[0]
    anchor = orig[tbl]
    mine = []
    for p in tc.findall(q("p"))[first:]:
        tc.remove(p)
        if not text_of(p).strip():
            continue
        anchor.addnext(p)
        anchor = p
        mine.append(p)
    moved += mine
    if END_EL[qn] is None:
        END_EL[qn] = mine[-1]

# ------------------------------------------------------------------ 2. global rules on every paragraph
answer_paras = set()
for p in body.iter(q("p")):
    old = text_of(p)
    new = norm(old)
    if new != old:
        retext(p, new)
        if id(p) not in explicit:
            log.append("[auto]\n  - %s\n  + %s" % (old, new))
    if re.search("[%s]" % FA, new):
        ppr = p.find(q("pPr"))
        style = ppr.find(q("pStyle")) if ppr is not None else None
        in_table = p.getparent().tag == q("tc")
        justify = not in_table and (style is not None and style.get(q("val")) == "ab" or p in moved
                                    or ppr is None or ppr.find(q("bidi")) is None)
        make_rtl(p, justify=justify)
    for r in p.iter(q("r")):
        ensure_rtl(r)

# ------------------------------------------------------------------ 3. chart images
rels_path = os.path.join(SRC_DIR, "word", "_rels", "document.xml.rels")
rels = etree.parse(rels_path)
media_dir = os.path.join(SRC_DIR, "word", "media")
_img_no = [0]


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def image_para(png, width_cm=16.0):
    _img_no[0] += 1
    n = _img_no[0]
    name = "chart%02d.png" % n
    data = open(png, "rb").read()
    open(os.path.join(media_dir, name), "wb").write(data)
    rid = "rIdChart%02d" % n
    rel = etree.SubElement(rels.getroot(), "{%s}Relationship" % PKG)
    rel.set("Id", rid)
    rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel.set("Target", "media/" + name)
    w, h = png_size(png)
    cx = int(width_cm * 360000)
    cy = int(cx * h / w)
    A = "http://schemas.openxmlformats.org/drawingml/2006/main"
    PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
    return E(
        '<w:p><w:pPr><w:keepLines/><w:bidi/><w:spacing w:before="60" w:after="60"/><w:jc w:val="center"/></w:pPr>'
        '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="%d" name="Chart %d"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="%s" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="%s"><a:graphicData uri="%s"><pic:pic xmlns:pic="%s">'
        '<pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
        '</wp:inline></w:drawing></w:r></w:p>'
        % (cx, cy, 9000 + n, n, A, A, PIC, PIC, 9000 + n, name, rid, cx, cy))


# ------------------------------------------------------------------ 4. added blocks
def heading(text, num=None):
    runs = []
    if num:
        runs.append(dsl.run(num + "  ", b=True, sz=22, color="C08A00"))
    runs.append(dsl.run(text, b=True, sz=24, color="1F3864"))
    return E(dsl.para(runs, keep=True, before=140, after=60))


def spacer():
    return E('<w:p><w:pPr><w:bidi/><w:spacing w:before="0" w:after="0" w:line="120" w:lineRule="exact"/>'
             '<w:rPr><w:sz w:val="8"/><w:szCs w:val="8"/></w:rPr></w:pPr></w:p>')


def banner(n, title):
    return E(dsl.para([dsl.run("  جدول و نمودار تکمیلی سؤال %s" % fa(n), b=True, sz=20, color="FFD966"),
                       dsl.run("   |   ", sz=20, color="FFFFFF"),
                       dsl.run(title, b=True, sz=24, color="FFFFFF")],
                      keep=True, before=240, after=60, shd="1F3864", line=300))


def note(text):
    return E(dsl.para([dsl.run(text, sz=20, color="444444")], jc="both", before=60, after=40, line=264))


def fa(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def insert_after(anchor, els):
    for e in els:
        anchor.addnext(e)
        anchor = e
    return anchor


CHARTS = {}
for f in sorted(os.listdir(CHART_DIR)):
    m = re.match(r"q(\d+)_\d+\.png$", f)
    if m:
        CHARTS.setdefault(int(m.group(1)), []).append(os.path.join(CHART_DIR, f))

for n in sorted(Q):
    c = Q[n]
    ans, end = ANS_EL[n], END_EL[n]
    assert ans.getparent() is body and end.getparent() is body, n
    # summary table + chart + source after the explanation
    els = [banner(n, c["title"]), heading("جدول جمع‌بندی", "۱"),
           E(dsl.summary_table(c["sum_head"], c["sum_rows"], c.get("sum_ratio")))]
    if c.get("sum_note"):
        els.append(note(c["sum_note"]))
    els.append(heading("نمودار / فلوچارت", "۲"))
    for png in CHARTS[n]:
        els.append(image_para(png))
    els.append(E(dsl.para([dsl.run("منبع: ", b=True, sz=18, color="555555"),
                           dsl.run(c["src"], sz=18, color="555555")], before=60, after=120)))
    insert_after(end, els)
    # option review right after the answer line
    head = c.get("opts_head", ("گزینه", "ادعای گزینه", "داوری"))
    els = [heading("بررسی گزینه‌ها" if head[0] == "گزینه" else "بررسی موارد"),
           E(dsl.options_table(c["opts"], head))]
    if c.get("count"):
        els.append(E(dsl.para([dsl.run(c["count"], b=True, sz=22, color="2E7D32")], before=60, after=0)))
    els.append(spacer())
    insert_after(ans, els)

tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)
rels.write(rels_path, xml_declaration=True, encoding="UTF-8", standalone=True)

# the chart images are PNG: make sure the package declares that type
ct_path = os.path.join(SRC_DIR, "[Content_Types].xml")
ct = open(ct_path, encoding="utf-8").read()
if not re.search(r'<Default Extension="png"', ct, re.I):
    ct = ct.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1)
    open(ct_path, "w", encoding="utf-8").write(ct)

# ------------------------------------------------------------------ zip
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(SRC_DIR, "[Content_Types].xml"), "[Content_Types].xml")
    for base, _, files in os.walk(SRC_DIR):
        for f in sorted(files):
            full = os.path.join(base, f)
            rel = os.path.relpath(full, SRC_DIR)
            if rel != "[Content_Types].xml":
                z.write(full, rel)
if LOG:
    open(LOG, "w", encoding="utf-8").write("\n".join(log))
print("ok", OUT, "changes:", len(log), "charts:", _img_no[0])
