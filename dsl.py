# Builders for the added blocks: option-review table, summary table, table-based diagrams.
from xml.sax.saxutils import escape

W = 9600          # width of data tables (dxa)
DW = 9400         # max width of diagrams
SYM_FONT = "Segoe UI Symbol"
ARROW_FONT = "Arial"

# box palette: fill, border
PAL = {
    "r": ("D6E4F5", "2F5D9B"),   # root / main
    "g": ("E3F1DE", "5B8F4E"),   # green
    "y": ("FFF2CC", "B8962E"),   # yellow
    "p": ("F8DDD9", "B5564A"),   # pink (highlight)
    "w": ("FFFFFF", "7F7F7F"),   # plain
}
HEAD_FILL = "D6E4F5"
ANS_FILL = "E8F4E3"
GRID = "8FA9C9"


def run(text, b=False, sz=22, color=None, font=None, rtl=True):
    rpr = ""
    if font:
        rpr += '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>' % (font, font, font)
    if b:
        rpr += "<w:b/><w:bCs/>"
    if color:
        rpr += '<w:color w:val="%s"/>' % color
    rpr += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz)
    if rtl:
        rpr += "<w:rtl/>"
    return '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, escape(text))


def para(runs, jc=None, style=None, keep=False, before=0, after=0, line=None, shd=None, ind=None):
    ppr = ""
    if style:
        ppr += '<w:pStyle w:val="%s"/>' % style
    if keep:
        ppr += "<w:keepNext/>"
    ppr += "<w:keepLines/>"
    if shd:
        ppr += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shd
    ppr += "<w:bidi/>"
    sp = '<w:spacing w:before="%d" w:after="%d"' % (before, after)
    if line:
        sp += ' w:line="%d" w:lineRule="auto"' % line
    ppr += sp + "/>"
    if ind is not None:
        ppr += '<w:ind w:left="%d" w:right="%d"/>' % (ind, ind)
    if jc:
        ppr += '<w:jc w:val="%s"/>' % jc
    return "<w:p><w:pPr>%s</w:pPr>%s</w:p>" % (ppr, "".join(runs) if isinstance(runs, (list, tuple)) else runs)


def _borders(color, sz=6, sides=("top", "left", "bottom", "right")):
    return "<w:tcBorders>%s</w:tcBorders>" % "".join(
        '<w:%s w:val="single" w:sz="%d" w:space="0" w:color="%s"/>' % (s, sz, color) for s in sides)


NOBORDER = "<w:tcBorders>%s</w:tcBorders>" % "".join(
    '<w:%s w:val="nil"/>' % s for s in ("top", "left", "bottom", "right"))


def cell(paras, w, span=1, fill=None, borders=None):
    pr = '<w:tcW w:w="%d" w:type="dxa"/>' % w
    if span > 1:
        pr += '<w:gridSpan w:val="%d"/>' % span
    if borders:
        pr += borders
    if fill:
        pr += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill
    pr += '<w:vAlign w:val="center"/>'
    return "<w:tc><w:tcPr>%s</w:tcPr>%s</w:tc>" % (pr, "".join(paras))


def row(cells, header=False, height=None):
    pr = "<w:cantSplit/>"
    if height:
        pr += '<w:trHeight w:val="%d"/>' % height
    if header:
        pr += "<w:tblHeader/>"
    return "<w:tr><w:trPr>%s</w:trPr>%s</w:tr>" % (pr, "".join(cells))


def table(widths, rows, grid=True, mar=(50, 100)):
    b = ""
    if grid:
        b = "<w:tblBorders>%s</w:tblBorders>" % "".join(
            '<w:%s w:val="single" w:sz="4" w:space="0" w:color="%s"/>' % (s, GRID)
            for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    pr = ('<w:bidiVisual/><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/>%s'
          '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="%d" w:type="dxa"/>'
          '<w:left w:w="%d" w:type="dxa"/><w:bottom w:w="%d" w:type="dxa"/>'
          '<w:right w:w="%d" w:type="dxa"/></w:tblCellMar>'
          '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" '
          'w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>') % (sum(widths), b, mar[0], mar[1], mar[0], mar[1])
    g = "".join('<w:gridCol w:w="%d"/>' % w for w in widths)
    return "<w:tbl><w:tblPr>%s</w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>" % (pr, g, "".join(rows))


def textcell(text, w, b=False, jc=None, fill=None, sz=22, keep=False):
    ps = [para([run(t, b=b, sz=sz)], jc=jc, keep=keep, line=264) for t in text.split("\n")]
    return cell(ps, w, fill=fill)


# ---------------------------------------------------------------- option-review table
def R(label, claim, mark, reason, ans=False, vt=None):
    return dict(label=label, claim=claim, mark=mark, reason=reason, ans=ans, vt=vt)


def options_table(rows, head=("گزینه", "ادعای گزینه", "داوری")):
    ws = [800, 3700, 5100]
    out = [row([textcell(h, w, b=True, jc="center", fill=HEAD_FILL, keep=True)
                for h, w in zip(head, ws)], header=True)]
    for r in rows:
        ok = r["mark"] == "v"
        vt = r["vt"] or ("درست" if ok else "نادرست")
        if r["ans"]:
            vt += " ← پاسخ"
        col = "2E7D32" if ok else "C62828"
        verdict = para([run("✔ " if ok else "✘ ", b=True, color=col, font=SYM_FONT, rtl=False),
                        run(vt, b=True, color=col), run(" — " + r["reason"])], line=264)
        fill = ANS_FILL if r["ans"] else None
        out.append(row([textcell(r["label"], ws[0], b=True, jc="center", fill=fill),
                        textcell(r["claim"], ws[1], fill=fill),
                        cell([verdict], ws[2], fill=fill)]))
    return table(ws, out)


# ---------------------------------------------------------------- summary table
def summary_table(head, rows, ratio=None):
    n = len(head)
    ratio = ratio or [1] * n
    ws = [int(W * r / sum(ratio)) for r in ratio]
    out = [row([textcell(h, w, b=True, jc="center", fill=HEAD_FILL, keep=True)
                for h, w in zip(head, ws)], header=True)]
    for r in rows:
        cs = []
        for i, (t, w) in enumerate(zip(r, ws)):
            cs.append(textcell(t, w, b=(i == 0), jc=None if (i == 0 or len(t) > 28) else "center",
                               fill="F3F7FC" if i == 0 else None))
        out.append(row(cs))
    return table(ws, out)


# ---------------------------------------------------------------- diagrams
def _box(text, w, kind="w", span=1, sz=20):
    fill, bd = PAL[kind]
    lines = text.split("\n")
    ps = []
    for i, t in enumerate(lines):
        bold = (i == 0 and len(lines) > 1) or (len(lines) == 1 and kind == "r")
        ps.append(para([run(t, b=bold, sz=sz if i == 0 else sz - 2)], jc="center", keep=True, line=252))
    return cell(ps, w, span=span, fill=fill, borders=_borders(bd, 8))


def _arrow(sym, w, span=1, label=None):
    runs = []
    if label:
        runs.append(run(label + " ", sz=18, color="2F5D9B", b=True))
    runs.append(run(sym, b=True, sz=30, color="2F5D9B", font=ARROW_FONT, rtl=False))
    return cell([para(runs, jc="center", keep=True, line=220)], w, span=span, borders=NOBORDER)


def _gap(w, span=1):
    return cell([para([run("", sz=8)], keep=True, line=200)], w, span=span, borders=NOBORDER)


def _note(text, w, span=1, sz=18):
    ps = [para([run(t, sz=sz, color="555555")], jc="center", keep=True, line=240) for t in text.split("\n")]
    return cell(ps, w, span=span, borders=NOBORDER)


def _tk(s):
    return (s, "w") if isinstance(s, str) else s


def diagram(widths, rows):
    """rows: list of lists of ('box', text, kind, span) | ('arr', sym, span, label) | ('gap', span) | ('note', text, span)"""
    out = []
    for r in rows:
        cs, col = [], 0
        for c in r:
            t = c[0]
            span = {"box": lambda: c[3], "arr": lambda: c[2], "gap": lambda: c[1], "note": lambda: c[2]}[t]()
            w = sum(widths[col:col + span])
            if t == "box":
                cs.append(_box(c[1], w, c[2], span))
            elif t == "arr":
                cs.append(_arrow(c[1], w, span, c[3] if len(c) > 3 else None))
            elif t == "gap":
                cs.append(_gap(w, span))
            else:
                cs.append(_note(c[1], w, span))
            col += span
        assert col == len(widths), (col, len(widths), r)
        out.append(row(cs))
    return table(widths, out, grid=False, mar=(40, 70))


def VF(steps, width=6400, notes=None):
    """vertical flow; notes: optional side notes aligned with steps"""
    steps = [_tk(s) for s in steps]
    if notes:
        ws = [width, DW - width]
        rows = []
        for i, (t, k) in enumerate(steps):
            if i:
                rows.append([("arr", "↓", 1), ("gap", 1)])
            rows.append([("box", t, k, 1), ("note", notes[i], 1) if notes[i] else ("gap", 1)])
        return diagram(ws, rows)
    rows = []
    for i, (t, k) in enumerate(steps):
        if i:
            rows.append([("arr", "↓", 1)])
        rows.append([("box", t, k, 1)])
    return diagram([width], rows)


def HF(steps, notes=None, sym="←", width=DW):
    """horizontal flow, right to left"""
    steps = [_tk(s) for s in steps]
    n = len(steps)
    aw = 340
    bw = (width - aw * (n - 1)) // n
    ws = []
    for i in range(n):
        if i:
            ws.append(aw)
        ws.append(bw)
    r1 = []
    for i, (t, k) in enumerate(steps):
        if i:
            r1.append(("arr", sym, 1))
        r1.append(("box", t, k, 1))
    rows = [r1]
    if notes:
        r2 = []
        for i in range(n):
            if i:
                r2.append(("gap", 1))
            r2.append(("note", notes[i], 1) if notes[i] else ("gap", 1))
        rows.append(r2)
    return diagram(ws, rows)


def _leaves(node):
    ch = node[2] if len(node) > 2 else []
    return 1 if not ch else sum(_leaves(c) for c in ch)


def _depth(node):
    ch = node[2] if len(node) > 2 else []
    return 1 if not ch else 1 + max(_depth(c) for c in ch)


def TR(root, gapw=180, width=DW):
    """tree: node = (text, kind, [children], edge_label?)"""
    L = _leaves(root)
    lw = (width - gapw * (L - 1)) // L
    ws = []
    for i in range(L):
        if i:
            ws.append(gapw)
        ws.append(lw)
    D = _depth(root)
    levels = [[] for _ in range(D)]   # (first_leaf, last_leaf, node)

    def walk(node, d, start):
        n = _leaves(node)
        levels[d].append((start, start + n - 1, node))
        s = start
        for c in (node[2] if len(node) > 2 else []):
            walk(c, d + 1, s)
            s += _leaves(c)
    walk(root, 0, 0)

    def line(items, maker):
        cells, col = [], 0
        for a, b, node in items:
            c0, c1 = 2 * a, 2 * b
            if c0 > col:
                cells.append(("gap", c0 - col))
            cells.append(maker(node, c1 - c0 + 1))
            col = c1 + 1
        if col < len(ws):
            cells.append(("gap", len(ws) - col))
        return cells

    rows = []
    for d in range(D):
        if d:
            rows.append(line(levels[d], lambda nd, sp: ("arr", "↓", sp, nd[3] if len(nd) > 3 else None)))
        rows.append(line(levels[d], lambda nd, sp: ("box", nd[0], nd[1], sp)))
    return diagram(ws, rows)


def MG(sources, target, tail=(), gapw=180, width=DW):
    """several boxes merging into one, then an optional vertical tail"""
    sources = [_tk(s) for s in sources]
    n = len(sources)
    lw = (width - gapw * (n - 1)) // n
    ws = []
    for i in range(n):
        if i:
            ws.append(gapw)
        ws.append(lw)
    N = len(ws)
    r1, r2 = [], []
    for i, (t, k) in enumerate(sources):
        if i:
            r1.append(("gap", 1)); r2.append(("gap", 1))
        r1.append(("box", t, k, 1)); r2.append(("arr", "↓", 1))
    t, k = _tk(target)
    rows = [r1, r2, [("box", t, k, N)]]
    for s in tail:
        t, k = _tk(s)
        rows.append([("arr", "↓", N)])
        rows.append([("box", t, k, N)])
    return diagram(ws, rows)


def PAR(cols, gapw=300, width=DW):
    """parallel vertical flows: cols = [(title, [steps])]"""
    n = len(cols)
    lw = (width - gapw * (n - 1)) // n
    ws = []
    for i in range(n):
        if i:
            ws.append(gapw)
        ws.append(lw)
    depth = max(len(c[1]) for c in cols)
    rows = []
    r = []
    for i, c in enumerate(cols):
        if i:
            r.append(("gap", 1))
        r.append(("box", c[0], "r", 1))
    rows.append(r)
    for d in range(depth):
        ra, rb = [], []
        for i, c in enumerate(cols):
            if i:
                ra.append(("gap", 1)); rb.append(("gap", 1))
            if d < len(c[1]):
                t, k = _tk(c[1][d])
                ra.append(("arr", "↓", 1)); rb.append(("box", t, k, 1))
            else:
                ra.append(("gap", 1)); rb.append(("gap", 1))
        rows += [ra, rb]
    return diagram(ws, rows)


def STK(layers, labelw=2300, width=8600):
    """stacked bands (no arrows): layers = [(side_label, text, kind)]"""
    ws = [labelw, width - labelw]
    rows = [[("note", lab, 1) if lab else ("gap", 1), ("box", t, k, 1)] for lab, t, k in layers]
    return diagram(ws, rows)
