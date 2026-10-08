# SVG versions of the table-based diagram builders in dsl.py (VF, HF, TR, MG, PAR, STK), so the
# diagrams of content.py can be drawn as chart images in the same style as charts11.py.
import math
from svgfig import Fig, tw, PAL, BLUE, GRAY

W = 900
KIND = {"r": "b", "g": "g", "y": "y", "p": "p", "w": "w"}
SZ = 15


def wrap(s, width, size=SZ):
    """break each line of s into lines that fit `width` px"""
    maxc = max(6, int((width - 22) / (size * 0.52)))
    out = []
    for ln in str(s).split("\n"):
        cur = ""
        for w in ln.split(" "):
            if cur and len(cur) + 1 + len(w) > maxc:
                out.append(cur); cur = w
            else:
                cur = (cur + " " + w) if cur else w
        out.append(cur)
    return "\n".join(out)


def _tk(s):
    return (s, "w") if isinstance(s, str) else s


def lines(s):
    return str(s).split("\n")


def box_h(s, size=SZ):
    return len(lines(s)) * size * 1.42 + 22


def box_w(s, size=SZ, pad=34):
    return tw(s, size) + pad


def draw_box(f, cx, y, w, s, kind, size=SZ, h=None):
    s = wrap(s, w, size)
    h = h or box_h(s, size)
    f.box(cx - w / 2, y, w, h, s, KIND.get(kind, kind), size)
    return h


def note(f, cx, y, s, size=13):
    n = len(lines(s))
    f.text(cx, y + n * size * 0.7, s, size, color="#555")
    return n * size * 1.4 + 6


class D:
    """a diagram description; rendered later with a title and a footnote"""

    def __init__(self, draw, height):
        self.draw, self.height = draw, height

    def fig(self, title=None, foot=None):
        top = 46 if title else 12
        fh = (len(lines(foot)) * 20 + 16) if foot else 0
        f = Fig(W, int(self.height + top + fh + 14), title)
        self.draw(f, top + 4)
        if foot:
            f.text(W / 2, f.h - fh / 2 - 6, foot, 14, color="#555")
        return f


# ---------------------------------------------------------------- vertical flow
def VF(steps, width=6400, notes=None):
    steps = [_tk(s) for s in steps]
    bw = min(max(box_w(t) for t, _ in steps) + 20, 520 if notes else 640)
    hs = [box_h(t) for t, _ in steps]
    gap = 40
    height = sum(hs) + gap * (len(steps) - 1)
    cx = 600 if notes else W / 2

    def draw(f, y0):
        y = y0
        for i, ((t, k), h) in enumerate(zip(steps, hs)):
            if i:
                f.arrow(cx, y - gap + 4, cx, y - 4, BLUE, 2.5)
            draw_box(f, cx, y, bw, t, k)
            if notes and notes[i]:
                f.line(cx - bw / 2 - 8, y + h / 2, cx - bw / 2 - 30, y + h / 2, "#BBB", 1.5)
                f.text(cx - bw / 2 - 36, y + h / 2, notes[i], 13.5, anchor="start", color="#444")
            y += h + gap
    return D(draw, height)


# ---------------------------------------------------------------- horizontal flow (right to left)
def HF(steps, notes=None, sym="←", width=None):
    steps = [_tk(s) for s in steps]
    n = len(steps)
    aw = 34
    bw = (W - 40 - aw * (n - 1)) / n
    size = SZ if bw > 150 else 13.5
    h = max(box_h(wrap(t, bw, size), size) for t, _ in steps)
    nh = max((len(lines(x)) * 13 * 1.4 + 8 for x in (notes or []) if x), default=0)
    height = h + (nh + 10 if nh else 0)

    def draw(f, y0):
        for i, (t, k) in enumerate(steps):
            cx = W - 20 - bw / 2 - i * (bw + aw)
            draw_box(f, cx, y0, bw, t, k, size, h)
            if i:
                x1 = cx + bw / 2 + aw - 4
                if sym in ("←", "→"):
                    f.arrow(x1, y0 + h / 2, cx + bw / 2 + 4, y0 + h / 2, BLUE, 2.5)
                else:
                    f.text(cx + bw / 2 + aw / 2, y0 + h / 2, sym, 18, weight=700, color=BLUE)
            if notes and notes[i]:
                f.text(cx, y0 + h + 8 + len(lines(notes[i])) * 13 * 0.7, notes[i], 13, color="#555")
    return D(draw, height)


# ---------------------------------------------------------------- tree
def _leaves(node):
    ch = node[2] if len(node) > 2 else []
    return 1 if not ch else sum(_leaves(c) for c in ch)


def TR(root, gapw=180, width=None):
    L = _leaves(root)
    gap = 14
    lw = (W - 40 - gap * (L - 1)) / L
    levels = []

    def walk(node, d, start):
        while len(levels) <= d:
            levels.append([])
        levels[d].append((start, _leaves(node), node))
        s = start
        for c in (node[2] if len(node) > 2 else []):
            walk(c, d + 1, s)
            s += _leaves(c)
    walk(root, 0, 0)
    size = SZ if lw > 140 else 13.5

    def bwid(start, n, nd):
        sw = n * lw + (n - 1) * gap
        return min(sw - 6, max(box_w(nd[0], size), 120))
    rowh = [max(box_h(wrap(nd[0], bwid(st, n, nd), size), size) for st, n, nd in lev) for lev in levels]
    eg = 52
    height = sum(rowh) + eg * (len(levels) - 1)

    def span_x(start, n):
        x_right = W - 20 - start * (lw + gap)
        x_left = x_right - (n * lw + (n - 1) * gap)
        return (x_left + x_right) / 2, (x_right - x_left)

    def draw(f, y0):
        ys, y = [], y0
        for h in rowh:
            ys.append(y)
            y += h + eg
        centers = {}
        for d, lev in enumerate(levels):
            for start, n, nd in lev:
                cx, sw = span_x(start, n)
                bw = bwid(start, n, nd)
                draw_box(f, cx, ys[d], bw, nd[0], nd[1], size, rowh[d])
                centers[id(nd)] = (cx, ys[d], rowh[d])
        for d, lev in enumerate(levels):
            for start, n, nd in lev:
                px, py, ph = centers[id(nd)]
                for c in (nd[2] if len(nd) > 2 else []):
                    cx, cy, _ = centers[id(c)]
                    f.arrow(px, py + ph + 3, cx, cy - 4, BLUE, 2.2)
                    if len(c) > 3 and c[3]:
                        f.text((px + cx) / 2 + (8 if cx < px else -8), (py + ph + cy) / 2, c[3], 12.5,
                               anchor="end" if cx < px else "start", weight=700, color=BLUE)
    return D(draw, height)


# ---------------------------------------------------------------- merge
def MG(sources, target, tail=(), gapw=180, width=None):
    sources = [_tk(s) for s in sources]
    n = len(sources)
    gap = 16
    bw = (W - 40 - gap * (n - 1)) / n
    size = SZ if bw > 140 else 13.5
    sh = max(box_h(wrap(t, bw, size), size) for t, _ in sources)
    tt, tk = _tk(target)
    tail = [_tk(s) for s in tail]
    tbw = min(max([box_w(tt)] + [box_w(t) for t, _ in tail]) + 30, 700)
    th = box_h(tt)
    tails = [box_h(t) for t, _ in tail]
    height = sh + 56 + th + sum(h + 40 for h in tails)

    def draw(f, y0):
        for i, (t, k) in enumerate(sources):
            cx = W - 20 - bw / 2 - i * (bw + gap)
            draw_box(f, cx, y0, bw, t, k, size, sh)
            f.arrow(cx, y0 + sh + 3, W / 2 + (cx - W / 2) * 0.35, y0 + sh + 52, BLUE, 2.2)
        y = y0 + sh + 56
        draw_box(f, W / 2, y, tbw, tt, tk)
        y += th
        for (t, k), h in zip(tail, tails):
            f.arrow(W / 2, y + 4, W / 2, y + 36, BLUE, 2.5)
            y += 40
            draw_box(f, W / 2, y, tbw, t, k)
            y += h
    return D(draw, height)


# ---------------------------------------------------------------- parallel flows
def PAR(cols, gapw=300, width=None):
    n = len(cols)
    gap = 40
    bw = (W - 40 - gap * (n - 1)) / n
    depth = max(len(c[1]) for c in cols)
    th = max(box_h(c[0]) for c in cols)
    rh = [max(box_h(wrap(_tk(c[1][d])[0], bw - 20)) if d < len(c[1]) else 0 for c in cols) for d in range(depth)]
    height = th + sum(h + 40 for h in rh)

    def draw(f, y0):
        for i, (title, steps) in enumerate(cols):
            cx = W - 20 - bw / 2 - i * (bw + gap)
            draw_box(f, cx, y0, bw, title, "r", SZ, th)
            y = y0 + th
            for d, s in enumerate(steps):
                t, k = _tk(s)
                f.arrow(cx, y + 4, cx, y + 36, BLUE, 2.5)
                y += 40
                draw_box(f, cx, y, bw - 20, t, k, SZ, rh[d])
                y += rh[d]
    return D(draw, height)


# ---------------------------------------------------------------- stacked bands
def STK(layers, labelw=2300, width=None):
    hs = [box_h(t) - 4 for _, t, _ in layers]
    height = sum(hs) + 6 * (len(layers) - 1)

    def draw(f, y0):
        y = y0
        x_right = W - 230
        for (lab, t, k), h in zip(layers, hs):
            fill, stroke, tc = PAL[KIND.get(k, k)]
            f.rect(60, y, x_right - 60, h, fill, stroke, 6, 1.8)
            f.text((60 + x_right) / 2, y + h / 2, t, SZ, weight=700, color=tc)
            if lab:
                f.text(W - 30, y + h / 2, lab, 13.5, anchor="start", color="#444")
            y += h + 6
    return D(draw, height)
