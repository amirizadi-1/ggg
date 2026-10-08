# Restyles an answer key so that every paragraph, table, picture and page element uses the exact formatting
# of the reference «Faraz11_Styled-2.docx» (fonts, sizes, spacing, colours, header/footer).
# Works on «سند (50)» (charts are drawn from its table diagrams) and on keys made by buildkey.py
# (charts already present; pass "-" as charts dir). A cover section before the first question keeps its
# pictures, and its notice box is taken from the reference.
# usage: python3 restyle.py <unzipped source> <unzipped reference> <background.png> <charts dir|-> <out.docx>
import copy, os, re, shutil, struct, sys, zipfile
from lxml import etree

SRC, REF, BG, CHARTS, OUT = sys.argv[1:6]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
q = lambda t: "{%s}%s" % (W, t)
NAVY = "282360"
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

doc_path = os.path.join(SRC, "word", "document.xml")
tree = etree.parse(doc_path)
root = tree.getroot()
body = root.find(q("body"))
NS = " ".join('xmlns:%s="%s"' % (k, v) for k, v in root.nsmap.items() if k)


def X(xml):
    return etree.fromstring("<x %s>%s</x>" % (NS, xml))[0]


def txt(e):
    return "".join(x.text or "" for x in e.iter(q("t")))


def has_drawing(e):
    return e.find(".//" + q("drawing")) is not None or e.find(".//" + q("pict")) is not None


# ------------------------------------------------------------------ paragraph templates (from the reference)
PPR = {
    "stem": '<w:pPr><w:keepNext/><w:keepLines/>{pb}<w:bidi/><w:spacing w:line="223" w:lineRule="auto"/>'
            '<w:ind w:left="567" w:hanging="567"/><w:jc w:val="both"/></w:pPr>',
    "item": '<w:pPr><w:keepNext/><w:keepLines/><w:bidi/><w:spacing w:line="223" w:lineRule="auto"/>'
            '<w:ind w:left="567"/><w:jc w:val="both"/></w:pPr>',
    "option": '<w:pPr>{kn}<w:keepLines/><w:bidi/><w:spacing w:line="223" w:lineRule="auto"/>'
              '<w:ind w:left="837" w:hanging="270"/><w:jc w:val="both"/></w:pPr>',
    "qspacer": '<w:pPr><w:keepLines/><w:bidi/><w:spacing w:line="20" w:lineRule="exact"/></w:pPr>',
    "answer": '<w:pPr><w:pStyle w:val="ab"/><w:keepNext/><w:shd w:val="clear" w:color="auto" w:fill="282360"/>'
              '<w:bidi/><w:spacing w:before="150" w:after="120" w:line="340" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>',
    "heading": '<w:pPr><w:keepNext/><w:keepLines/><w:bidi/><w:spacing w:before="140" w:after="65"/></w:pPr>',
    "count": '<w:pPr><w:keepLines/><w:bidi/><w:spacing w:before="60" w:after="65"/></w:pPr>',
    "spacer": '<w:pPr><w:bidi/><w:spacing w:before="0" w:after="20" w:line="20" w:lineRule="exact"/>'
              '<w:rPr><w:sz w:val="8"/><w:szCs w:val="8"/></w:rPr></w:pPr>',
    "text": '<w:pPr><w:pStyle w:val="ab"/>{kn}{num}<w:bidi/><w:spacing w:after="65"/><w:jc w:val="both"/></w:pPr>',
    "banner": '<w:pPr><w:keepNext/><w:keepLines/><w:shd w:val="clear" w:color="auto" w:fill="282360"/><w:bidi/>'
              '<w:spacing w:before="200" w:after="120" w:line="370" w:lineRule="auto"/></w:pPr>',
    "note": '<w:pPr><w:keepLines/><w:bidi/><w:spacing w:before="60" w:after="65" w:line="264" w:lineRule="auto"/>'
            '<w:jc w:val="both"/></w:pPr>',
    "chart": '<w:pPr><w:keepLines/><w:bidi/><w:spacing w:before="60" w:after="65"/><w:jc w:val="center"/></w:pPr>',
    "source": '<w:pPr><w:keepLines/><w:bidi/><w:spacing w:before="60" w:after="65"/></w:pPr>',
    "picture": '<w:pPr><w:spacing w:before="100" w:after="100" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>',
}


def run_xml(text, b=False, color=None, sz=None, hint=True):
    rpr = '<w:rFonts w:hint="cs"/>' if hint else ""
    if b:
        rpr += "<w:b/><w:bCs/>"
    if color:
        rpr += '<w:color w:val="%s"/>' % color
    if sz:
        rpr += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz)
    rpr += "<w:rtl/>"
    return '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (
        rpr, text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def new_p(kind, runs="", **fmt):
    f = {"pb": "", "kn": "", "num": ""}
    f.update(fmt)
    return X("<w:p>%s%s</w:p>" % (PPR[kind].format(**f), runs))


def set_ppr(p, kind, **fmt):
    old = p.find(q("pPr"))
    f = {"pb": "", "kn": "", "num": ""}
    f.update(fmt)
    new = X("<w:p>%s</w:p>" % PPR[kind].format(**f))[0]
    if old is not None:
        p.replace(old, new)
    else:
        p.insert(0, new)


RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow",
             "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern",
             "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign", "rtl", "cs",
             "em", "lang", "eastAsianLayout", "specVanish", "oMath"]


def restyle_runs(p, bold=None, color=NAVY, sz=None, keep_colors=(), keep_sym=True):
    """normalise run formatting: drop size/highlight/latin font overrides, set bold/colour/size like the reference"""
    for r in p.iter(q("r")):
        rpr = r.find(q("rPr"))
        if rpr is None:
            rpr = etree.Element(q("rPr")); r.insert(0, rpr)
        fonts = rpr.find(q("rFonts"))
        sym = fonts is not None and "Segoe" in (fonts.get(q("ascii")) or "")
        old_color = rpr.find(q("color"))
        oc = old_color.get(q("val")) if old_color is not None else None
        was_b = rpr.find(q("b")) is not None
        was_u = copy.deepcopy(rpr.find(q("u")))
        is_rtl = rpr.find(q("rtl")) is not None or bool(re.search("[؀-ۿ]", "".join(t.text or "" for t in r.iter(q("t")))))
        for c in list(rpr):
            rpr.remove(c)
        if sym and keep_sym:
            rpr.append(copy.deepcopy(fonts))
        elif fonts is not None and fonts.get(q("hint")) == "cs":
            e = etree.SubElement(rpr, q("rFonts")); e.set(q("hint"), "cs")
        if (was_b if bold is None else bold):
            etree.SubElement(rpr, q("b")); etree.SubElement(rpr, q("bCs"))
        col = oc if oc in keep_colors else color
        if col:
            etree.SubElement(rpr, q("color")).set(q("val"), col)
        if sz:
            etree.SubElement(rpr, q("sz")).set(q("val"), str(sz))
            etree.SubElement(rpr, q("szCs")).set(q("val"), str(sz))
        if was_u is not None:
            rpr.append(was_u)
        if is_rtl and not sym:
            etree.SubElement(rpr, q("rtl"))
        for t in r.findall(q("lastRenderedPageBreak")):
            r.remove(t)


# ------------------------------------------------------------------ tables
TBLPR_DATA = ('<w:tblPr><w:bidiVisual/><w:tblW w:w="{w}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>'
              + "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="F0C45F"/>' % s
                        for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
              + '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="85" w:type="dxa"/>'
              '<w:left w:w="100" w:type="dxa"/><w:bottom w:w="85" w:type="dxa"/><w:right w:w="100" w:type="dxa"/>'
              '</w:tblCellMar><w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" '
              'w:noHBand="0" w:noVBand="1"/></w:tblPr>')


def is_data_table(tbl):
    b = tbl.find(q("tblPr") + "/" + q("tblBorders"))
    return b is not None and any(c.get(q("color")) == "8FA9C9" for c in b)


def is_diagram_table(tbl):
    return tbl.find(q("tblPr") + "/" + q("tblBorders")) is None and tbl.find(".//" + q("tcBorders")) is not None


def restyle_data_table(tbl):
    pr = tbl.find(q("tblPr"))
    w = pr.find(q("tblW")).get(q("w"))
    tbl.replace(pr, X(TBLPR_DATA.format(w=w)))
    for i, tr in enumerate(tbl.findall(q("tr"))):
        trpr = tr.find(q("trPr"))
        if trpr is not None:
            for j in trpr.findall(q("jc")):
                trpr.remove(j)
        fill = "FFE08A" if i == 0 else ("FCEFC5" if i % 2 else "FFF8E7")
        for tc in tr.findall(q("tc")):
            tcpr = tc.find(q("tcPr"))
            width = tcpr.find(q("tcW"))
            span = tcpr.find(q("gridSpan"))
            new = etree.Element(q("tcPr"))
            new.append(copy.deepcopy(width))
            if span is not None:
                new.append(copy.deepcopy(span))
            sh = etree.SubElement(new, q("shd"))
            sh.set(q("val"), "clear"); sh.set(q("color"), "auto"); sh.set(q("fill"), fill)
            etree.SubElement(new, q("vAlign")).set(q("val"), "center")
            tc.replace(tcpr, new)
            for p in tc.findall(q("p")):
                ppr = p.find(q("pPr"))
                jc = ppr.find(q("jc")) if ppr is not None else None
                kn = ppr is not None and ppr.find(q("keepNext")) is not None
                new_ppr = X('<w:p><w:pPr>%s<w:keepLines/><w:bidi/><w:spacing w:before="0" w:after="0" w:line="264" '
                            'w:lineRule="auto"/>%s</w:pPr></w:p>' % ("<w:keepNext/>" if kn else "",
                                                                     '<w:jc w:val="%s"/>' % jc.get(q("val")) if jc is not None else ""))[0]
                if ppr is not None:
                    p.replace(ppr, new_ppr)
                else:
                    p.insert(0, new_ppr)
                restyle_runs(p, sz=22, keep_colors=("2E7D32", "C62828"))


def restyle_question_table(tbl):
    for p in tbl.iter(q("p")):
        ppr = p.find(q("pPr"))
        if ppr is not None and ppr.find(q("bidi")) is None:
            b = etree.Element(q("bidi"))
            after = [c for c in ppr if etree.QName(c).localname in ("spacing", "ind", "jc", "rPr")]
            (after[0].addprevious(b) if after else ppr.append(b))


# ------------------------------------------------------------------ chart images
rels_path = os.path.join(SRC, "word", "_rels", "document.xml.rels")
rels = etree.parse(rels_path)
media = os.path.join(SRC, "word", "media")
_n = [0]


def chart_para(png):
    _n[0] += 1
    n = _n[0]
    name = "chart%02d.png" % n
    shutil.copy(png, os.path.join(media, name))
    rid = "rIdChart%02d" % n
    rel = etree.SubElement(rels.getroot(), "{%s}Relationship" % PKG)
    rel.set("Id", rid); rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel.set("Target", "media/" + name)
    with open(png, "rb") as f:
        w, h = struct.unpack(">II", f.read(24)[16:24])
    cx = 5760000
    cy = int(cx * h / w)
    return new_p("chart", '<w:r><w:rPr><w:color w:val="282360"/></w:rPr><w:drawing><wp:inline distT="0" distB="0" '
                 'distL="0" distR="0"><wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
                 '<wp:docPr id="%d" name="Chart %d"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="%s" '
                 'noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic xmlns:a="%s"><a:graphicData uri="%s">'
                 '<pic:pic xmlns:pic="%s"><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
                 '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr>'
                 '<a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
                 '</a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
                 % (cx, cy, 9000 + n, n, A, A, PIC, PIC, 9000 + n, name, rid, cx, cy))


def to_inline(anchor):
    inline = etree.Element("{%s}inline" % WP)
    for k in ("distT", "distB", "distL", "distR"):
        inline.set(k, "0")
    for tag in ("extent", "effectExtent", "docPr", "cNvGraphicFramePr"):
        el = anchor.find("{%s}%s" % (WP, tag))
        if el is not None:
            inline.append(copy.deepcopy(el))
    inline.append(copy.deepcopy(anchor.find("{%s}graphic" % A)))
    return inline


# ------------------------------------------------------------------ walk the body
STEM = re.compile(r"^([۰-۹0-9]+)\s*-")
STEM_RE = STEM
OPTION = re.compile(r"^[۰-۹0-9]\s*\)")
HEADINGS = ("بررسی گزینه‌ها", "بررسی موارد")
EXPL_HEADS = re.compile(r"^(بررسی (موارد|سایر|همهٔ|گزینهٔ)[^:]*:)\s*$")
LABEL = re.compile(r"^((صورت )?سؤال چی می‌گه؟|بررسی گزینهٔ (پاسخ|صحیح|درست|جواب)\s*:)")

elements = list(body)
qnum, state, first_stem = None, None, True
HAS_ANSWERS = any(e.tag == q("p") and txt(e).strip().startswith("پاسخ") for e in body)
ref_body = list(etree.parse(os.path.join(REF, "word", "document.xml")).getroot().find(q("body")))
ref_front = []
for e in ref_body:
    if e.tag == q("p") and STEM_RE.match(txt(e).strip()):
        break
    if not has_drawing(e):
        ref_front.append(copy.deepcopy(e))
front_done = False


def is_chart(p):
    return any((d.get("name") or "").startswith("Chart") for d in p.iter("{%s}docPr" % WP))
i = 0
pending_charts = None
out = []                                # (element) in final order
while i < len(elements):
    el = elements[i]
    i += 1
    if el.tag == q("sectPr"):
        out.append(el); continue
    if el.tag == q("tbl") and state is None:
        if not front_done:
            out.extend(ref_front); front_done = True
        continue
    if el.tag == q("tbl"):
        if is_diagram_table(el):
            continue                                          # replaced by chart images
        if is_data_table(el):
            restyle_data_table(el)
        else:
            restyle_question_table(el)
        out.append(el); continue
    p, t = el, txt(el).strip()
    if state is None and not STEM.match(t):                             # cover section before the first question
        if has_drawing(p):
            out.append(p)
        elif not front_done:
            out.extend(ref_front); front_done = True
        continue
    ppr = p.find(q("pPr"))
    fill = ppr.find(q("shd")).get(q("fill")) if ppr is not None and ppr.find(q("shd")) is not None else None
    jc = ppr.find(q("jc")).get(q("val")) if ppr is not None and ppr.find(q("jc")) is not None else None
    m = STEM.match(t)
    # pictures (anchored or inline, alone in their paragraph)
    if has_drawing(p) and state == "a" and is_chart(p) and not t:
        runs = [r for r in p.findall(q("r")) if r.find(q("drawing")) is not None]
        cp = new_p("chart")
        for r in runs:
            rpr = r.find(q("rPr"))
            if rpr is not None:
                r.remove(rpr)
            r.insert(0, X('<w:r><w:rPr><w:color w:val="282360"/></w:rPr></w:r>')[0])
            cp.append(r)
        out.append(cp)
        continue
    if has_drawing(p) and state == "a":
        for a in list(p.iter("{%s}anchor" % WP)):
            if a.get("behindDoc") != "1":
                a.getparent().replace(a, to_inline(a))
        runs = [r for r in p.findall(q("r")) if r.find(q("drawing")) is not None]
        pic = new_p("picture")
        for r in runs:
            p.remove(r); pic.append(r)
        out.append(pic)
        if not t:
            continue
    if m and not (state == "q" and not first_stem and False):
        qnum = int(m.group(1).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")))
        set_ppr(p, "stem", pb="" if first_stem or not HAS_ANSWERS else "<w:pageBreakBefore/>")
        restyle_runs(p, bold=True, color=None)
        first_stem, state = False, "q"
        out.append(p); continue
    if state == "q":
        if t.startswith("پاسخ"):
            state = "a"
        elif not t:
            if has_drawing(p):
                out.append(p); continue
            set_ppr(p, "qspacer"); out.append(p); continue
        elif OPTION.match(t):
            nxt = elements[i] if i < len(elements) else None
            last = nxt is None or not (nxt.tag == q("p") and OPTION.match(txt(nxt).strip()))
            set_ppr(p, "option", kn="" if last else "<w:keepNext/>")
            restyle_runs(p, bold=False, color=None, sz=26)
            out.append(p); continue
        else:
            set_ppr(p, "item")
            restyle_runs(p, bold=True, color=None)
            out.append(p); continue
    if t.startswith("پاسخ") and len(t) < 40:
        set_ppr(p, "answer")
        restyle_runs(p, bold=True, color="FFFFFF")
        out.append(p); continue
    if fill == "1F3864":                                                  # banner
        title = t.split("|", 1)[1].strip() if "|" in t else t
        out.append(new_p("banner",
                         '<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="FFD966"/><w:sz w:val="20"/><w:szCs w:val="20"/><w:rtl/></w:rPr>'
                         '<w:t xml:space="preserve">  جدول و نمودار تکمیلی سؤال %s</w:t></w:r>'
                         '<w:r><w:rPr><w:color w:val="FFFFFF"/><w:sz w:val="20"/><w:szCs w:val="20"/><w:rtl/></w:rPr>'
                         '<w:t xml:space="preserve">   |   </w:t></w:r>'
                         '<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="FFFFFF"/><w:sz w:val="24"/><w:szCs w:val="24"/><w:rtl/></w:rPr>'
                         '<w:t xml:space="preserve">%s</w:t></w:r>' % (str(qnum).translate(FA_DIGITS), title)))
        continue
    if t in HEADINGS:
        out.append(new_p("heading", '<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="282360"/><w:sz w:val="24"/>'
                                    '<w:szCs w:val="24"/><w:rtl/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % t))
        continue
    t_head = re.sub(r"^[۱۲]\s+", "", t)
    if t_head in ("جدول جمع‌بندی", "نمودار / فلوچارت"):
        t = t_head
        num = "۱" if t.startswith("جدول") else "۲"
        out.append(new_p("heading", '<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="C08A00"/><w:sz w:val="22"/>'
                                    '<w:szCs w:val="22"/><w:rtl/></w:rPr><w:t xml:space="preserve">%s  </w:t></w:r>'
                                    '<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="282360"/><w:sz w:val="24"/>'
                                    '<w:szCs w:val="24"/><w:rtl/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (num, t)))
        if num == "۲" and CHARTS != "-":                                   # charts + skip the drawn diagram
            k = 1
            while os.path.exists(os.path.join(CHARTS, "q%02d_%d.png" % (qnum, k))):
                out.append(chart_para(os.path.join(CHARTS, "q%02d_%d.png" % (qnum, k))))
                k += 1
            while i < len(elements):
                nx = elements[i]
                if nx.tag == q("p") and txt(nx).strip().startswith("منبع"):
                    break
                if nx.tag == q("p") and has_drawing(nx):
                    break
                i += 1
        continue
    if t.startswith("تعداد موارد") or t.startswith("تعداد مورد"):
        out.append(new_p("count", run_xml(t, b=True, color="2E7D32", sz=22, hint=False)))
        continue
    if t.startswith("منبع"):
        body_txt = t.split(":", 1)[1].strip() if ":" in t else t
        out.append(new_p("source", run_xml("منبع: ", b=True, color=NAVY, sz=18, hint=False)
                         + run_xml(body_txt, color=NAVY, sz=18, hint=False)))
        out.append(new_p("spacer"))
        continue
    if not t:
        out.append(new_p("spacer")); continue
    # summary note under a table (centred/justified small paragraph right after a data table)
    prev = out[-1] if out else None
    if prev is not None and prev.tag == q("tbl") and ppr is not None and ppr.find(q("spacing")) is not None \
            and ppr.find(q("spacing")).get(q("line")) == "264":
        out.append(new_p("note", run_xml(t, color=NAVY, sz=20, hint=False)))
        continue
    # explanation text
    num = ppr.find(q("numPr")) if ppr is not None else None
    numxml = etree.tostring(num).decode() if num is not None else ""
    numxml = re.sub(r' xmlns:\w+="[^"]+"', "", numxml)
    kn = "<w:keepNext/>" if EXPL_HEADS.match(t) or t.startswith("بررسی گزینهٔ") else ""
    set_ppr(p, "text", kn=kn, num=numxml)
    if EXPL_HEADS.match(t):
        restyle_runs(p, bold=True)
    else:
        restyle_runs(p)
        lm = LABEL.match(t)
        if lm and t.startswith(("سؤال", "صورت")):                           # bold the «سؤال چی می‌گه؟» label
            acc = 0
            for r in p.iter(q("r")):
                s = "".join(x.text or "" for x in r.findall(q("t")))
                if acc < len(lm.group(1)):
                    rpr = r.find(q("rPr"))
                    if rpr.find(q("b")) is None:
                        fonts = rpr.find(q("rFonts"))
                        b = etree.Element(q("b")); bcs = etree.Element(q("bCs"))
                        (fonts.addnext(b) if fonts is not None else rpr.insert(0, b)); b.addnext(bcs)
                acc += len(s)
    out.append(p)

for el in list(body):
    body.remove(el)
for el in out:
    body.append(el)

# ------------------------------------------------------------------ package: styles, fonts, theme, header, footer
for part in ("styles.xml", "fontTable.xml", "theme/theme1.xml"):
    shutil.copy(os.path.join(REF, "word", part), os.path.join(SRC, "word", part))
if os.path.isdir(os.path.join(SRC, "word", "fonts")):
    shutil.rmtree(os.path.join(SRC, "word", "fonts"))
shutil.copytree(os.path.join(REF, "word", "fonts"), os.path.join(SRC, "word", "fonts"))
shutil.copy(os.path.join(REF, "word", "_rels", "fontTable.xml.rels"), os.path.join(SRC, "word", "_rels", "fontTable.xml.rels"))
st = open(os.path.join(SRC, "word", "settings.xml"), encoding="utf-8").read()
if "embedTrueTypeFonts" not in st:
    st = re.sub(r"(<w:settings[^>]*>)", r'\1<w:embedTrueTypeFonts/>', st, count=1)
    open(os.path.join(SRC, "word", "settings.xml"), "w", encoding="utf-8").write(st)

hdr_target = None
for rel in list(rels.getroot()):
    if rel.get("Type").endswith("/header"):
        hdr_target = rel.get("Target")
    if rel.get("Type").endswith("/footer"):
        rels.getroot().remove(rel)
shutil.copy(os.path.join(REF, "word", "header1.xml"), os.path.join(SRC, "word", hdr_target))
shutil.copy(os.path.join(REF, "word", "_rels", "header1.xml.rels"),
            os.path.join(SRC, "word", "_rels", os.path.basename(hdr_target) + ".rels"))
shutil.copy(BG, os.path.join(media, "page_design.png"))
shutil.copy(os.path.join(REF, "word", "footer1.xml"), os.path.join(SRC, "word", "footer_design.xml"))
fr = etree.SubElement(rels.getroot(), "{%s}Relationship" % PKG)
fr.set("Id", "rIdFooterDesign"); fr.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer")
fr.set("Target", "footer_design.xml")
rels.write(rels_path, xml_declaration=True, encoding="UTF-8", standalone=True)

sect = body.find(q("sectPr"))
ref_sect = etree.parse(os.path.join(REF, "word", "document.xml")).getroot().find(q("body")).find(q("sectPr"))
new_sect = copy.deepcopy(ref_sect)
new_sect.find(q("headerReference")).set("{%s}id" % R, sect.find(q("headerReference")).get("{%s}id" % R))
if not front_done:                       # no cover pages: number from 1 (with covers keep the reference's «3»)
    new_sect.find(q("pgNumType")).set(q("start"), "1")
body.replace(sect, new_sect)

ct_path = os.path.join(SRC, "[Content_Types].xml")
ct = open(ct_path, encoding="utf-8").read()
if "footer_design.xml" not in ct:
    ct = ct.replace("</Types>", '<Override PartName="/word/footer_design.xml" ContentType="application/'
                    'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
for ext, typ in (("png", "image/png"), ("odttf", "application/vnd.openxmlformats-officedocument.obfuscatedFont")):
    if not re.search(r'Extension="%s"' % ext, ct, re.I):
        ct = ct.replace("<Default ", '<Default Extension="%s" ContentType="%s"/><Default ' % (ext, typ), 1)
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
print("ok", OUT, "charts:", _n[0])
