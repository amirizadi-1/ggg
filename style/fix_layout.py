# Keeps pictures on the pages of their own question: no page may hold only pictures.
#  1) two consecutive picture paragraphs are placed side by side (borderless two-column table), and
#     pictures left after a question's source line are moved up to the end of its explanation;
#  2) then, repeatedly: render to PDF, find picture-only pages, shrink the pictures on them (×0.82),
#     until none is left (or a picture reaches 40 % of its size).
# usage: python3 fix_layout.py <in.docx> <out.docx> [work dir]
import copy, io, os, re, shutil, subprocess, sys, tempfile, zipfile
from lxml import etree
from PIL import Image

SRC, OUT = sys.argv[1:3]
WORK = sys.argv[3] if len(sys.argv) > 3 else tempfile.mkdtemp()
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
q = lambda t: "{%s}%s" % (W, t)
BG = (1786, 2526)
EMU_CM = 360000

zin = zipfile.ZipFile(SRC)
files = {n: zin.read(n) for n in zin.namelist()}
infos = {i.filename: i for i in zin.infolist()}
doc = etree.fromstring(files["word/document.xml"])
body = doc.find(q("body"))
rels = {r.get("Id"): r.get("Target") for r in etree.fromstring(files["word/_rels/document.xml.rels"])}


def pix(inline):
    blip = inline.find(".//{%s}blip" % A)
    return Image.open(io.BytesIO(files["word/" + rels[blip.get("{%s}embed" % R)]])).size


def is_chart(inline):
    return (inline.find("{%s}docPr" % WP).get("name") or "").startswith("Chart")


def scale(inline, f):
    ext = inline.find("{%s}extent" % WP)
    cx, cy = int(int(ext.get("cx")) * f), int(int(ext.get("cy")) * f)
    ext.set("cx", str(cx)); ext.set("cy", str(cy))
    for x in inline.iter("{%s}ext" % A):
        if x.getparent().tag == "{%s}xfrm" % A:
            x.set("cx", str(cx)); x.set("cy", str(cy))


def txt(e):
    return "".join(t.text or "" for t in e.iter(q("t"))).strip()


def picture_only(p):
    return p.tag == q("p") and not txt(p) and p.find(".//{%s}inline" % WP) is not None


# ---- 1) side-by-side pairs of question pictures
pairs = 0
els = list(body)
i = 0
while i < len(els) - 1:
    a, b = els[i], els[i + 1]
    if picture_only(a) and picture_only(b) and not any(is_chart(x) for x in a.iter("{%s}inline" % WP)) \
            and not any(is_chart(x) for x in b.iter("{%s}inline" % WP)):
        col = 4760
        cells = []
        for p in (a, b):
            for inl in p.iter("{%s}inline" % WP):
                ext = inl.find("{%s}extent" % WP)
                maxw = (col - 200) * 635                             # dxa → EMU
                f = min(1.0, maxw / int(ext.get("cx")), 8.5 * EMU_CM / int(ext.get("cy")))
                scale(inl, f)
            p2 = copy.deepcopy(p)
            ppr = p2.find(q("pPr"))
            if ppr is not None:
                for sp in ppr.findall(q("spacing")):
                    sp.set(q("before"), "0"); sp.set(q("after"), "0")
            cells.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>%s</w:tc>'
                         % (col, etree.tostring(p2).decode()))
        tbl = etree.fromstring(
            '<w:tbl xmlns:w="%s"><w:tblPr><w:bidiVisual/><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/>'
            '<w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>'
            '<w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders><w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="60" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/>'
            '<w:right w:w="60" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid><w:gridCol w:w="%d"/><w:gridCol w:w="%d"/>'
            '</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>%s</w:tr></w:tbl>' % (W, 2 * col, col, col, "".join(cells)))
        a.addprevious(tbl)
        body.remove(a); body.remove(b)
        pairs += 1
        els = list(body)
        i = els.index(tbl) + 1
        continue
    i += 1
print("side-by-side pairs:", pairs)


# ---- 1b) question pictures left at the very end of a question (after the source line) are moved up to
#          the end of the explanation, before the «جدول و نمودار تکمیلی» banner, so they flow with text
def is_banner(e):
    if e.tag != q("p"):
        return False
    shd = e.find(q("pPr") + "/" + q("shd"))
    return shd is not None and shd.get(q("fill")) == "282360" and "جدول و نمودار تکمیلی" in txt(e)


def is_pic_block(e):
    if picture_only(e):
        return not any(is_chart(x) for x in e.iter("{%s}inline" % WP))
    if e.tag == q("tbl") and not txt(e) and e.find(".//{%s}inline" % WP) is not None:
        return not any(is_chart(x) for x in e.iter("{%s}inline" % WP))
    return False


moved = 0
banner = None
els = list(body)
for idx, e in enumerate(els):
    if is_banner(e):
        banner = e
    elif e.tag == q("p") and txt(e).startswith("منبع"):
        k = idx + 1
        blocks = []
        while k < len(els) and (is_pic_block(els[k]) or (els[k].tag == q("p") and not txt(els[k])
                                                         and els[k].find(".//{%s}drawing" % W) is None)):
            if is_pic_block(els[k]):
                blocks.append(els[k])
            k += 1
        if banner is not None and blocks:
            for blk in blocks:
                banner.addprevious(blk)
                moved += 1
        banner = None
print("pictures moved before the banner:", moved)


# ---- 2) shrink pictures that are alone on a page
def write(path):
    files["word/document.xml"] = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in files.items():
            z.writestr(infos[n], data)


def render(path):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", WORK, path],
                   capture_output=True, timeout=600)
    return os.path.join(WORK, os.path.splitext(os.path.basename(path))[0] + ".pdf")


def bad_pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    n = int(re.search(r"Pages:\s+(\d+)", out).group(1))
    imgs = {}
    for line in subprocess.run(["pdfimages", "-list", pdf], capture_output=True, text=True).stdout.splitlines()[2:]:
        f = line.split()
        p, w, h = int(f[0]), int(f[3]), int(f[4])
        if (w, h) != BG and p > 2:
            imgs.setdefault(p, []).append((w, h))
    bad = {}
    for p in range(3, n + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True).stdout
        if len(re.sub(r"[\s\d۰-۹‌‪-‮]", "", t)) < 5 and p in imgs:
            bad[p] = imgs[p]
    return n, bad


inlines = [x for x in body.iter("{%s}inline" % WP)]
orig = {id(x): int(x.find("{%s}extent" % WP).get("cy")) for x in inlines}
by_size = {}
for x in inlines:
    by_size.setdefault(pix(x), []).append(x)

tmp = os.path.join(WORK, "layout.docx")
for rnd in range(12):
    write(tmp)
    n, bad = bad_pages(render(tmp))
    print("round %d: %d pages, picture-only pages: %s" % (rnd, n, sorted(bad)))
    if not bad:
        break
    changed = 0
    for p, sizes in bad.items():
        for s in sizes:
            for x in by_size.get(s, []):
                cy = int(x.find("{%s}extent" % WP).get("cy"))
                if cy > 0.4 * orig[id(x)]:
                    scale(x, 0.82); changed += 1
    if not changed:
        print("no more shrinking possible")
        break
shutil.copy(tmp, OUT)
print("ok", OUT)
