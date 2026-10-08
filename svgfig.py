# Small SVG toolkit for the chart section (rendered to PNG by render_charts.js).
import math
from xml.sax.saxutils import escape

FONT = "Vazirmatn"
BG = "#fff"                     # chart background (the styled answer keys use the page colour #E7F2FE)
FA_DIGITS = str.maketrans("0123456789-", "۰۱۲۳۴۵۶۷۸۹−")

# fill, stroke, text
PAL = {
    "b": ("#D6E4F5", "#2F5D9B", "#1F3864"),
    "g": ("#E3F1DE", "#5B8F4E", "#2E5A24"),
    "y": ("#FFF2CC", "#B8962E", "#6B5410"),
    "p": ("#F8DDD9", "#B5564A", "#7A2A20"),
    "w": ("#FFFFFF", "#7F7F7F", "#222222"),
    "v": ("#E9E1F5", "#6A4C9C", "#3E2A63"),
}
BLUE, GREEN, RED, GOLD, GRAY, PURPLE = "#2F5D9B", "#3E8E41", "#C62828", "#C08A00", "#8A8A8A", "#6A4C9C"


def fa(x):
    return str(x).translate(FA_DIGITS)


class Fig:
    def __init__(self, w, h, title=None):
        self.w, self.h = w, h
        self.els = []
        self.markers = {}
        self.top = 0
        if title:
            self.text(w / 2, 26, title, size=21, weight=700, color="#1F3864")
            self.top = 46

    # ---------------------------------------------------------------- primitives
    def raw(self, s):
        self.els.append(s)

    def rect(self, x, y, w, h, fill="#fff", stroke="#7F7F7F", rx=10, sw=2, dash=None, op=1):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.raw('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="%s" fill-opacity="%s" '
                 'stroke="%s" stroke-width="%s"%s/>' % (x, y, w, h, rx, fill, op, stroke, sw, d))

    def circle(self, cx, cy, r, fill="#fff", stroke="#7F7F7F", sw=2, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.raw('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="%s"%s/>'
                 % (cx, cy, r, fill, stroke, sw, d))

    def ellipse(self, cx, cy, rx, ry, fill="#fff", stroke="#7F7F7F", sw=2):
        self.raw('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%s"/>'
                 % (cx, cy, rx, ry, fill, stroke, sw))

    def line(self, x1, y1, x2, y2, color="#555", sw=2, dash=None, cap="round"):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.raw('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s" '
                 'stroke-linecap="%s"%s/>' % (x1, y1, x2, y2, color, sw, cap, d))

    def path(self, d, color="#555", sw=2, fill="none", dash=None, op=1, join="round"):
        ds = ' stroke-dasharray="%s"' % dash if dash else ""
        self.raw('<path d="%s" stroke="%s" stroke-width="%s" fill="%s" fill-opacity="%s" '
                 'stroke-linejoin="%s" stroke-linecap="round"%s/>' % (d, color, sw, fill, op, join, ds))

    def poly(self, pts, color="#555", sw=2, fill="none", dash=None, op=1):
        d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
        self.path(d, color, sw, fill, dash, op)

    def _marker(self, color):
        if color not in self.markers:
            mid = "m%d" % len(self.markers)
            self.markers[color] = mid
        return self.markers[color]

    def arrow(self, x1, y1, x2, y2, color=BLUE, sw=2.5, dash=None, both=False):
        m = self._marker(color)
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        start = ' marker-start="url(#%s_s)"' % m if both else ""
        self.raw('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s" '
                 'marker-end="url(#%s)"%s%s/>' % (x1, y1, x2, y2, color, sw, m, start, d))

    def carrow(self, d, color=BLUE, sw=2.5, dash=None):
        m = self._marker(color)
        ds = ' stroke-dasharray="%s"' % dash if dash else ""
        self.raw('<path d="%s" stroke="%s" stroke-width="%s" fill="none" marker-end="url(#%s)"%s/>'
                 % (d, color, sw, m, ds))

    def text(self, x, y, s, size=17, anchor="middle", weight=400, color="#222", lh=1.4, rot=None, italic=False,
             ltr=False):
        """y = vertical centre of the whole block; '\n' separates lines.
        anchor: middle | start (= right edge for RTL text) | end (= left edge for RTL text)"""
        lines = str(s).split("\n")
        first = y - (len(lines) - 1) * size * lh / 2 + size * 0.36
        tr = ' transform="rotate(%d %.1f %.1f)"' % (rot, x, y) if rot else ""
        st = ' font-style="italic"' if italic else ""
        out = ['<text x="%.1f" y="%.1f" font-size="%s" text-anchor="%s" font-weight="%d" fill="%s" '
               'direction="%s" unicode-bidi="plaintext"%s%s>' % (x, first, size, anchor, weight, color,
                                                                 "ltr" if ltr else "rtl", tr, st)]
        for i, t in enumerate(lines):
            out.append('<tspan x="%.1f" dy="%s">%s</tspan>' % (x, "0" if i == 0 else "%.1f" % (size * lh), escape(t)))
        out.append("</text>")
        self.raw("".join(out))

    # ---------------------------------------------------------------- composites
    def box(self, x, y, w, h, s, kind="w", size=17, weight=None, rx=12, sw=2, dash=None):
        fill, stroke, tc = PAL[kind]
        self.rect(x, y, w, h, fill, stroke, rx, sw, dash)
        lines = str(s).split("\n")
        if weight is None:
            weight = 700 if len(lines) == 1 else 400
        if len(lines) > 1 and weight == 400:
            # bold first line, regular rest
            lh = size * 1.4
            top = y + h / 2 - (len(lines) - 1) * lh / 2
            self.text(x + w / 2, top, lines[0], size, weight=700, color=tc)
            for i, t in enumerate(lines[1:], 1):
                self.text(x + w / 2, top + i * lh, t, size - 2, color="#333")
        else:
            self.text(x + w / 2, y + h / 2, s, size, weight=weight, color=tc)

    def pill(self, x, y, s, kind="b", size=15, pad=12, anchor="middle"):
        fill, stroke, tc = PAL[kind]
        w = tw(s, size) + 2 * pad
        h = size * 1.75
        x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        self.rect(x0, y - h / 2, w, h, fill, stroke, rx=int(h / 2), sw=1.5)
        self.text(x0 + w / 2, y, s, size, weight=700, color=tc)
        return w

    def badge(self, cx, cy, s, color=BLUE, r=14, size=15):
        self.circle(cx, cy, r, color, color, 1)
        self.text(cx, cy, s, size, weight=700, color="#fff")

    def tick(self, cx, cy, ok, size=22):
        self.text(cx, cy, "✔" if ok else "✘", size, weight=700, color=GREEN if ok else RED)

    def svg(self):
        defs = []
        for color, mid in self.markers.items():
            defs.append('<marker id="%s" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
                        'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>' % (mid, color))
            defs.append('<marker id="%s_s" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
                        'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>' % (mid, color))
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
                'font-family="%s"><rect width="100%%" height="100%%" fill="%s"/><defs>%s</defs>%s</svg>'
                % (self.w, self.h, self.w, self.h, FONT, BG, "".join(defs), "".join(self.els)))


def tw(s, size):
    """rough text width estimate for Vazirmatn"""
    return max(len(t) for t in str(s).split("\n")) * size * 0.52


# -------------------------------------------------------------------- plotting
class Axes:
    def __init__(self, fig, x, y, w, h, xr, yr):
        self.f, self.x, self.y, self.w, self.h = fig, x, y, w, h
        self.xr, self.yr = xr, yr

    def X(self, t):
        return self.x + (t - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def frame(self, xlabel, ylabel, yticks=(), xticks=(), grid=True):
        f = self.f
        for v in yticks:
            if grid:
                f.line(self.x, self.Y(v), self.x + self.w, self.Y(v), "#E3E3E3", 1.2, None)
            f.line(self.x - 6, self.Y(v), self.x, self.Y(v), "#444", 1.5)
            f.text(self.x - 12, self.Y(v), fa("+%d" % v if v > 0 else v), 15, anchor="end", color="#333", ltr=True)
        for t, lab in xticks:
            f.line(self.X(t), self.y + self.h, self.X(t), self.y + self.h + 6, "#444", 1.5)
            f.text(self.X(t), self.y + self.h + 20, lab, 14, color="#333")
        f.arrow(self.x, self.y + self.h, self.x + self.w + 22, self.y + self.h, "#444", 1.8)
        f.arrow(self.x, self.y + self.h, self.x, self.y - 18, "#444", 1.8)
        f.text(self.x + self.w / 2, self.y + self.h + 44, xlabel, 15, color="#444")
        f.text(self.x - 58, self.y + self.h / 2, ylabel, 15, color="#444", rot=-90)

    def curve(self, fn, t0, t1, color=BLUE, sw=3.5, dash=None, n=300):
        pts = [(self.X(t0 + (t1 - t0) * i / n), self.Y(fn(t0 + (t1 - t0) * i / n))) for i in range(n + 1)]
        self.f.poly(pts, color, sw, dash=dash)

    def band(self, t0, t1, color, op=0.16, label=None, size=14, ly=None, lcolor=None):
        self.f.rect(self.X(t0), self.y, self.X(t1) - self.X(t0), self.h, color, "none", 0, 0, op=op)
        if label:
            self.f.text((self.X(t0) + self.X(t1)) / 2, ly if ly is not None else self.y + 14, label, size,
                        weight=700, color=lcolor or color)

    def dot(self, t, v, label=None, color=RED, r=7, dx=0, dy=-22, size=15):
        self.f.circle(self.X(t), self.Y(v), r, color, "#fff", 2)
        if label:
            self.f.text(self.X(t) + dx, self.Y(v) + dy, label, size, weight=700, color=color)


def ap(t, t0=1.0, rise=0.55, fall=0.9, peak=30.0, rest=-70.0, rest2=None):
    """smooth action-potential curve (no undershoot, as in the textbook figure)"""
    rest2 = rest if rest2 is None else rest2
    if t < t0:
        return rest
    if t < t0 + rise:
        u = (t - t0) / rise
        return rest + (peak - rest) * (1 - math.cos(math.pi * u)) / 2
    if t < t0 + rise + fall:
        u = (t - t0 - rise) / fall
        return peak + (rest2 - peak) * (1 - math.cos(math.pi * u)) / 2
    return rest2


def wave(t, comps):
    return sum(a * math.sin(2 * math.pi * f * t + p) for a, f, p in comps)
