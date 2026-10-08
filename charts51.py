# Chart section of each question of «سند (51)» (biology 12, chapter 1 — informational molecules).
import json, math, os, sys
from svgfig import Fig, Axes, fa, PAL, BLUE, GREEN, RED, GOLD, GRAY, PURPLE

W = 900
CH = {}
OLD, NEW = "#1F3864", "#E8A33D"          # old (template) strand / new strand
BASE = {"A": "#C0504D", "T": "#4F81BD", "G": "#9BBB59", "C": "#F2C14E", "U": "#8064A2"}


def chart(n):
    def deco(fn):
        CH[n] = fn
        return fn
    return deco


def footer(f, s, color="#555", size=14, weight=400, dy=16):
    f.text(W / 2, f.h - dy, s, size, weight=weight, color=color)


def ladder(f, x0, x1, y, gap=56, seq="ATGCGTAC", top=OLD, bot=OLD, labels=True):
    """horizontal double strand: backbone lines + base-pair rungs"""
    n = len(seq)
    step = (x1 - x0) / n
    comp = {"A": "T", "T": "A", "G": "C", "C": "G"}
    for i, b in enumerate(seq):
        cx = x0 + step * (i + 0.5)
        c = comp[b]
        big = b in "AG"
        mid = y + (gap * (0.58 if big else 0.42)) - gap / 2
        f.rect(cx - 9, y - gap / 2 + 6, 18, mid - (y - gap / 2 + 6), BASE[b], "none", 3, 0)
        f.rect(cx - 9, mid, 18, y + gap / 2 - 6 - mid, BASE[c], "none", 3, 0)
        f.line(cx - 9, mid, cx + 9, mid, "#fff", 2, "2 2")
        if labels:
            f.text(cx, y - gap / 2 + 18, b, 12, weight=700, color="#fff", ltr=True)
            f.text(cx, y + gap / 2 - 18, c, 12, weight=700, color="#fff", ltr=True)
    f.line(x0, y - gap / 2, x1, y - gap / 2, top, 7)
    f.line(x0, y + gap / 2, x1, y + gap / 2, bot, 7)


def tube(f, x, y, h, bands, label=None, w=46):
    f.rect(x - w / 2, y, w, h, "#F4F8FC", "#7F7F7F", 18, 2)
    for pos, thick in bands:            # pos: 0 = top (light) … 1 = bottom (heavy)
        yy = y + 14 + pos * (h - 28)
        f.rect(x - w / 2 + 6, yy - thick / 2, w - 12, thick, "#2F5D9B", "none", 3, 0)
    if label:
        f.text(x, y + h + 20, label, 14, color="#333")


# =================================================================== Q1
@chart(1)
def q1():
    f = Fig(W, 600, "آزمایش‌های گریفیت و ایوری در یک نگاه")
    y0 = f.top + 20
    f.text(W - 160, y0, "گریفیت (۱۹۲۸)", 17, weight=700, color="#1F3864")
    rows = [("۱. پوشینه‌دار زنده", "موش مُرد", RED, True, False),
            ("۲. بدون پوشینهٔ زنده", "موش زنده ماند", GREEN, False, False),
            ("۳. پوشینه‌دارِ کشته با گرما", "موش زنده ماند", GREEN, False, False),
            ("۴. پوشینه‌دارِ کشته + بدون پوشینهٔ زنده", "موش مُرد؛ پوشینه‌دارِ زنده در خون", RED, True, True)]
    for i, (a, b, col, cap, trans) in enumerate(rows):
        yy = y0 + 34 + i * 58
        f.box(W - 330, yy, 310, 44, a, "w", 14.5)
        f.arrow(W - 336, yy + 22, W - 396, yy + 22, BLUE, 2.5)
        f.box(W - 640, yy, 240, 44, b, "p" if col == RED else "g", 14.5)
        f.text(W - 700, yy + 22, "پوشینه ✔" if cap else "پوشینه ✘", 13.5, weight=700, color=GREEN if cap else GRAY)
        if trans:
            f.pill(110, yy + 22, "پوشینه‌دار شدن!", "y", 13)
    y1 = y0 + 290
    f.line(30, y1 - 14, W - 30, y1 - 14, "#DDD", 1.5)
    f.text(W - 160, y1 + 8, "ایوری (۱۹۴۴)", 17, weight=700, color="#1F3864")
    exps = [("۱. عصاره + تخریب همهٔ پروتئین‌ها", "انتقال ✔ ← پروتئین مادهٔ وراثتی نیست"),
            ("۲. لایه‌های گریزانه (سانتریفیوژ)", "انتقال فقط با لایهٔ دنا ← دنا مادهٔ وراثتی است"),
            ("۳. چهار ظرف، چهار آنزیم تخریب‌کننده", "انتقال در همه به جز ظرف آنزیم تخریب‌کنندهٔ دنا")]
    for i, (a, b) in enumerate(exps):
        yy = y1 + 36 + i * 58
        f.box(W - 330, yy, 310, 44, a, "b", 14.5)
        f.arrow(W - 336, yy + 22, W - 396, yy + 22, BLUE, 2.5)
        f.box(40, yy, 440, 44, b, "g", 14.5)
    footer(f, "گزینهٔ ۲: تولید پوشینه در مرحله‌های ۱ و ۴ دیده شد، ولی پوشینه‌دار شدنِ بدون پوشینه‌ها فقط در مرحلهٔ ۴.", "#7A2A20", 14, 700)
    return f


# =================================================================== Q2
@chart(2)
def q2():
    f = Fig(W, 450, "نردبان مارپیچ دنا: سه بخش تصویر")
    y = f.top + 190
    ladder(f, 80, 640, y, 110, "ATGCCGTA")
    # callouts
    f.line(250, y + 2, 250, y - 120, "#999", 1.5, "4 4")
    f.box(170, y - 160, 160, 40, "۱: پیوند هیدروژنی", "p", 15)
    f.line(430, y - 30, 470, y - 120, "#999", 1.5, "4 4")
    f.box(390, y - 160, 170, 40, "۲: باز آلی (پله)", "y", 15)
    f.line(600, y + 55, 690, y + 100, "#999", 1.5, "4 4")
    f.box(680, y + 80, 190, 40, "۳: ستون قند ـ فسفات", "b", 15)
    # legend of H-bonds
    f.text(760, y - 120, "تعداد پیوند هیدروژنی", 15, weight=700, color="#1F3864")
    for i, (pair, n) in enumerate((("A – T", 2), ("G – C", 3))):
        yy = y - 80 + i * 44
        f.text(820, yy, pair, 15, weight=700, ltr=True)
        for k in range(3):
            f.rect(700 + k * 22, yy - 10, 16, 20, "#C0504D" if k < n else "#EEE", "none", 3, 0)
    footer(f, "پیوندهای هیدروژنی اختصاصی‌اند و دو رشته را مقابل هم نگه می‌دارند؛ برابری پورین و پیریمیدین فقط در کل مولکول دورشته‌ای است.")
    return f


# =================================================================== Q3
@chart(3)
def q3():
    f = Fig(W, 400, "مهم‌ترین عوامل مؤثر در همانندسازی (طبق کتاب)")
    y = f.top + 30
    src = [("دنا\n(الگو)", "b"), ("نوکلئوتیدهای آزاد\nسه‌فسفاته", "g"), ("آنزیم‌ها\n(هلیکاز، دنابسپاراز …)", "y")]
    xs = [W - 190, W / 2, 190]
    for (s, k), x in zip(src, xs):
        f.box(x - 130, y, 260, 70, s, k, 17)
        f.arrow(x, y + 72, W / 2 + (x - W / 2) * 0.25, y + 150, BLUE, 3)
    f.box(W / 2 - 170, y + 154, 340, 56, "همانندسازی دنا", "b", 20)
    f.rect(40, y + 240, 300, 70, "#FDF3F2", RED, 10, 2, "6 4")
    f.text(190, y + 262, "ATP (گزینهٔ ۳)", 17, weight=700, color=RED, ltr=False)
    f.text(190, y + 290, "در فهرست مهم‌ترین عوامل نیامده", 14, color="#7A2A20")
    f.text(620, y + 275, "انرژی تشکیل فسفودی‌استر ← جدا شدن دو فسفاتِ\nنوکلئوتید سه‌فسفاته", 14.5, color="#2E5A24")
    return f


# =================================================================== Q4
@chart(4)
def q4():
    f = Fig(W, 470, "ترتیب رویدادها در همانندسازی دنای یوکاریوتی")
    y = f.top + 20
    steps = [("قبل از همانندسازی", "باز شدن پیچ‌وتاب فامینه\nو جدا شدن هیستون‌ها", "w"),
             ("در دوراهی", "هلیکاز: شکستن پیوند هیدروژنی\nو جدا شدن دو رشته", "y"),
             ("پشت دوراهی", "دنابسپاراز: جفت کردن نوکلئوتید مکمل،\nشکستن پیوند بین فسفات‌ها،\nتشکیل فسفودی‌استر", "g")]
    xs = [W - 150, W / 2, 150]
    for (t, s, k), x in zip(steps, xs):
        f.text(x, y + 6, t, 15, weight=700, color="#1F3864")
        f.box(x - 135, y + 24, 270, 92, s, k, 15, weight=400)
    f.arrow(W - 288, y + 70, W / 2 + 140, y + 70, BLUE, 3)
    f.arrow(W / 2 - 140, y + 70, 288, y + 70, BLUE, 3)
    # replication bubble
    yb = y + 260
    x0, x1 = 60, W - 60
    f.line(x0, yb - 14, 260, yb - 14, OLD, 6)
    f.line(x0, yb + 14, 260, yb + 14, OLD, 6)
    f.line(640, yb - 14, x1, yb - 14, OLD, 6)
    f.line(640, yb + 14, x1, yb + 14, OLD, 6)
    f.path("M260,%d C330,%d 570,%d 640,%d" % (yb - 14, yb - 90, yb - 90, yb - 14), OLD, 6)
    f.path("M260,%d C330,%d 570,%d 640,%d" % (yb + 14, yb + 90, yb + 90, yb + 14), OLD, 6)
    f.path("M290,%d C350,%d 550,%d 610,%d" % (yb - 30, yb - 70, yb - 70, yb - 30), NEW, 5, dash="10 5")
    f.path("M290,%d C350,%d 550,%d 610,%d" % (yb + 30, yb + 70, yb + 70, yb + 30), NEW, 5, dash="10 5")
    for x in (262, 638):
        f.circle(x, yb, 12, "#FFF2CC", GOLD, 2)
        f.text(x, yb + 120 - 10, "دوراهی:\nشکستن پیوند هیدروژنی", 13, color="#6B5410")
    f.text(W / 2, yb, "بین دوراهی‌ها: تشکیل فسفودی‌استر", 14, weight=700, color="#2E5A24")
    f.text(W / 2, yb - 112, "حباب همانندسازی (یک جایگاه آغاز، دو دوراهی)", 14, color="#555")
    return f


# =================================================================== Q5
@chart(5)
def q5():
    f = Fig(W, 440, "مولکول‌های نوکلئوتیدی مارپیچ در یاختهٔ یوکاریوتی")
    y = f.top + 10
    f.box(W / 2 - 200, y, 400, 46, "مولکول نوکلئوتیدی (بسپار نوکلئوتیدهای سه‌بخشی)", "b", 16)
    f.arrow(W / 2 + 100, y + 46, 680, y + 92, BLUE, 3)
    f.arrow(W / 2 - 100, y + 46, 220, y + 92, BLUE, 3)
    f.box(560, y + 96, 240, 42, "هسته", "g", 17)
    f.box(100, y + 96, 240, 42, "سیتوپلاسم", "y", 17)
    leaves = [(620, "دنای خطی\n(دورشته؛ دو سر یکسان)", "g"), (760, "رنا\n(تک‌رشته؛ دو سر متفاوت)", "g"),
              (80, "دنای حلقوی\n(راکیزه، دیسه)", "y"), (220, "دنای خطیِ\nدر حال همانندسازی\n(دورشته)", "y"), (360, "رنا\n(تک‌رشته)", "y")]
    for x, s, k in leaves:
        px = 680 if k == "g" else 220
        f.arrow(px, y + 138, x, y + 182, GREEN if k == "g" else GOLD, 2.5)
        f.box(x - 66, y + 186, 132, 78, s, k, 14, weight=400)
    f.rect(40, y + 290, W - 80, 64, "#F7F7F7", "#DDD", 8, 1)
    f.text(W / 2, y + 310, "ویژگی مشترک همه: از واحدهای سه‌بخشی (قند، باز آلی، فسفات) ساخته شده‌اند ← گزینهٔ ۲", 15, weight=700, color="#2E5A24")
    f.text(W / 2, y + 336, "در مولکول خطی، قند ـ فسفاتِ نوکلئوتید ابتدایی جزو فسفودی‌استر نیست (رد گزینهٔ ۳).", 13.5, color="#555")
    return f


# =================================================================== Q6
@chart(6)
def q6():
    f = Fig(W, 400, "انواع رنا × ویژگی‌ها (نمودار نقطه‌ای)")
    types = ["رنای پیک", "رنای ناقل", "رنای رناتنی", "رناهای کوچک"]
    feats = [("۱) مجاورت با پروتئین‌ها", (1, 1, 1, 1)), ("۲) عبور از منفذ هسته", (1, 1, 1, 1)),
             ("۳) حمل آمینواسید به رناتن", (0, 1, 0, 0)), ("۴) نقش آنزیمی", (0, 0, 1, 1))]
    cw = 120
    y0 = f.top + 40
    cols = [W - 300 - cw * j for j in range(4)]
    for j, t in enumerate(types):
        f.text(cols[j], y0, t, 15, weight=700, color="#1F3864")
    for i, (lab, vals) in enumerate(feats):
        yy = y0 + 50 + i * 66
        only = sum(vals) == 1
        f.rect(20, yy - 26, W - 40, 52, "#E8F4E3" if only else ("#F7F7F7" if i % 2 else "#FFFFFF"), "#E2E2E2", 6, 1)
        f.text(W - 30, yy, lab, 15, anchor="start", weight=700 if only else 400, color="#2E5A24" if only else "#333")
        for j, v in enumerate(vals):
            f.circle(cols[j], yy, 15 if v else 7, GREEN if v else "#DDD", "#fff" if v else "#DDD", 2)
        f.text(70, yy, "فقط یک نوع ✔" if only else "چند نوع", 13.5, weight=700, color=GREEN if only else GRAY)
    footer(f, "فقط مورد ۳ (رنای ناقل) ویژگی یک نوع رناست ← گزینهٔ ۳", "#2E5A24", 15, 700)
    return f


# =================================================================== Q7
@chart(7)
def q7():
    f = Fig(W, 460, "تعداد جایگاه‌های آغاز و سهم هر دنابسپاراز (طرح‌واره)")
    a = Axes(f, 120, f.top + 30, 330, 250, (0, 10), (0, 10))
    f.arrow(a.x, a.y + a.h, a.x + a.w + 16, a.y + a.h, "#444", 1.8)
    f.arrow(a.x, a.y + a.h, a.x, a.y - 14, "#444", 1.8)
    f.text(a.x + a.w / 2, a.y + a.h + 28, "تعداد جایگاه‌های آغاز", 14, color="#444")
    f.text(a.x - 40, a.y + a.h / 2, "طول رشتهٔ هر دنابسپاراز", 14, color="#444", rot=-90)
    a.curve(lambda t: 9 / (0.25 + 0.9 * t) if t > 0.05 else 9.5, 0.4, 10, GREEN, 3.5)
    a.dot(1.2, 9 / (0.25 + 1.08), "مثلاً بعد از تشکیل اندام‌ها", BLUE, dx=70, dy=-12, size=13)
    a.dot(7.5, 9 / (0.25 + 6.75), "مورولا و بلاستولا", RED, dx=0, dy=-22, size=13)
    # bars: relative chromosome length
    bx, by = 560, f.top + 30
    f.text(bx + 140, by, "طول نسبی دنای اصلی (طرح‌واره)", 15, weight=700, color="#1F3864")
    bars = [("فام‌تن پروکاریوت (حلقوی)", 0.18, "y"), ("هر فام‌تن یوکاریوت (خطی)", 0.95, "b")]
    for i, (lab, v, k) in enumerate(bars):
        yy = by + 50 + i * 80
        f.text(bx + 280, yy - 8, lab, 14, anchor="start", color="#333")
        f.rect(bx + 280 - 280 * v, yy + 6, 280 * v, 30, PAL[k][1], "none", 5, 0, op=0.85)
    f.text(bx + 140, by + 225, "فسفودی‌استر بیشتر در فام‌تن یوکاریوتی\n← گزینهٔ ۱ نامناسب", 15, weight=700, color="#7A2A20")
    footer(f, "هرچه جایگاه‌های آغاز بیشتر باشد، هر دنابسپاراز بخش کوتاه‌تری از رشته را می‌سازد (گزینهٔ ۲ مناسب).")
    return f


# =================================================================== Q8
@chart(8)
def q8():
    f = Fig(W, 510, "دو حباب همانندسازی روی یک فام‌تن")
    yb = f.top + 90
    f.line(40, yb - 10, W - 40, yb - 10, OLD, 6)
    f.line(40, yb + 10, W - 40, yb + 10, OLD, 6)

    def bubble(c, r, lab):
        f.ellipse(c, yb, r, 52 if r > 150 else 34, "#FFFFFF", OLD, 6)
        f.path("M%d,%d Q%d,%d %d,%d" % (c - r + 20, yb - 6, c, yb - (40 if r > 150 else 24), c + r - 20, yb - 6), NEW, 4, dash="8 4")
        f.path("M%d,%d Q%d,%d %d,%d" % (c - r + 20, yb + 6, c, yb + (40 if r > 150 else 24), c + r - 20, yb + 6), NEW, 4, dash="8 4")
        f.badge(c, yb, lab, BLUE, 16, 16)
    bubble(620, 190, "۱")
    bubble(200, 90, "۲")
    # comparison bars
    rows = [("الف) نوکلئوتیدهای جایگاه فعال", 0.9, 0.45), ("ب) احتمال دیدن نوکلئوتید یوراسیل‌دار", 0.85, 0.5),
            ("ج) فراوانی سیتوزین (طبق پاسخ‌نامه)", 0.45, 0.85), ("د) احتمال اشتباه دنابسپاراز", 0.45, 0.85)]
    y0 = yb + 100
    f.rect(W - 330, y0 - 30, 14, 14, BLUE, "none", 3, 0)
    f.text(W - 340, y0 - 23, "حباب ۱", 13, anchor="start")
    f.rect(W - 220, y0 - 30, 14, 14, GOLD, "none", 3, 0)
    f.text(W - 230, y0 - 23, "حباب ۲", 13, anchor="start")
    for i, (lab, v1, v2) in enumerate(rows):
        yy = y0 + i * 62
        more2 = v2 > v1
        f.text(W - 40, yy + 14, lab, 14.5, anchor="start", weight=700 if more2 else 400, color="#2E5A24" if more2 else "#333")
        f.rect(80, yy, 380 * v1, 16, BLUE, "none", 4, 0, op=0.85)
        f.rect(80, yy + 20, 380 * v2, 16, GOLD, "none", 4, 0, op=0.85)
        f.text(40, yy + 18, "✔" if more2 else "✘", 18, weight=700, color=GREEN if more2 else RED)
    footer(f, "در بخش ۲ بیشتر است: موارد «ج» و «د» ← ۲ مورد (مقادیر طرح‌واره‌اند)", "#2E5A24", 14.5, 700)
    return f


# =================================================================== Q9
@chart(9)
def q9():
    f = Fig(W, 360, "خط زمانی کشف مادهٔ وراثتی و ساختار دنا")
    y = f.top + 120
    events = [(1869, "میشر", "کشف نوکلئیک اسید"), (1928, "گریفیت", "انتقال «مادهٔ وراثتی»\n(نه دنا) ← گزینهٔ ۱"),
              (1944, "ایوری", "دنا مادهٔ وراثتی است"), (1950, "چارگاف", "A=T و G=C"),
              (1952, "ویلکینز و فرانکلین", "مارپیچ، بیش از یک رشته"), (1953, "واتسون و کریک", "مدل مارپیچ دورشته‌ای")]
    x1, x0 = W - 60, 60
    f.line(x0, y, x1, y, "#888", 4)
    for i, (yr, who, what) in enumerate(events):
        x = x1 - (x1 - x0) * i / (len(events) - 1)
        hl = yr == 1928
        f.circle(x, y, 11, RED if hl else BLUE, "#fff", 3)
        f.text(x, y + 28, fa(yr), 15, weight=700, color=RED if hl else "#1F3864", ltr=True)
        up = i % 2 == 0
        f.text(x, y - 40 if up else y + 70, who, 15, weight=700, color="#333")
        f.text(x, y - 82 if up else y + 112, what, 13.5, color=RED if hl else "#555")
    footer(f, "گریفیت ماهیت مادهٔ وراثتی را مشخص نکرد؛ ایوری حدود ۱۶ سال بعد نشان داد این ماده دناست.")
    return f


# =================================================================== Q10
@chart(10)
def q10():
    f = Fig(W, 420, "رنا در برابر دنای هسته‌ای")
    yr, yd = f.top + 70, f.top + 200
    f.text(W - 90, yr, "رنا", 18, weight=700, color="#3E2A63")
    f.line(200, yr, 760, yr, PURPLE, 6)
    for i in range(8):
        x = 225 + i * 70
        f.rect(x - 9, yr + 3, 18, 34, BASE["AUGCAGUC"[i]], "none", 3, 0)
    f.circle(200, yr, 9, "#fff", PURPLE, 3)
    f.text(180, yr - 20, "P", 14, weight=700, color=PURPLE, ltr=True)
    f.text(780, yr - 20, "OH", 14, weight=700, color=PURPLE, ltr=True)
    f.text(W - 90, yd, "دنای هسته‌ای", 18, weight=700, color="#1F3864")
    ladder(f, 200, 760, yd, 70, "ATGCATGC", labels=False)
    f.text(180, yd - 52, "P / OH", 13, weight=700, color=OLD, ltr=True)
    f.text(790, yd - 52, "OH / P", 13, weight=700, color=OLD, ltr=True)
    rows = ["الف) دو سر متفاوت", "ب) بدون محدودیت مکملی", "ج) فسفودی‌استر = نوکلئوتید − ۱", "د) OH روی کربن ۲ قند"]
    for i, s in enumerate(rows):
        x = W - 230 - (i % 2) * 400
        f.pill(x, f.h - 100 + (i // 2) * 36, s + "  ✔", "g", 13)
    footer(f, "هر چهار ویژگی دربارهٔ رنا درست و دربارهٔ دنای هسته‌ای نادرست است ← ۴ مورد", "#2E5A24", 14.5, 700)
    return f


# =================================================================== Q11
@chart(11)
def q11():
    f = Fig(W, 470, "نتایج گریزانه در سه طرح همانندسازی (مزلسون و استال)")
    models = [("حفاظتی", [[(1, 9)], [(0.05, 9), (1, 9)], [(0.05, 16), (1, 9)]]),
              ("نیمه‌حفاظتی (تأییدشده)", [[(1, 9)], [(0.5, 9)], [(0.05, 9), (0.5, 9)]]),
              ("غیرحفاظتی (پراکنده)", [[(1, 9)], [(0.5, 9)], [(0.36, 9)]])]
    times = ["۰ دقیقه", "۲۰ دقیقه", "۴۰ دقیقه"]
    gw = (W - 160) / 3
    for i, (name, tubes) in enumerate(models):
        cx = W - 20 - gw * (i + 0.5)
        hl = i == 2 or i == 1
        f.text(cx, f.top + 20, name, 16, weight=700, color="#1F3864")
        for j, bands in enumerate(tubes):
            x = cx + 72 - j * 72
            tube(f, x, f.top + 46, 270, bands, times[j])
        if i:
            f.rect(cx - gw / 2 + 6, f.top + 30, gw - 12, 330, "none", GREEN, 12, 2, "6 4")
    f.text(55, f.top + 60, "سبک\n(۱۴N)", 13, color="#555")
    f.text(55, f.top + 315, "سنگین\n(۱۵N)", 13, color="#555")
    f.arrow(55, f.top + 90, 55, f.top + 285, GRAY, 2)
    footer(f, "کادر سبز: طرح‌هایی که دنای جدید از «بخشی از» دنای اولیه ساخته می‌شود؛ خط دقیقهٔ ۲۰ پایین‌تر از یک خط دقیقهٔ ۴۰ است ← گزینهٔ ۴", "#2E5A24", 13.5, 700)
    return f


# =================================================================== Q12
@chart(12)
def q12():
    f = Fig(W, 430, "پایان همانندسازی: دنای خطی در برابر دنای حلقوی")
    # circular
    cx, cy = 680, f.top + 150
    f.circle(cx, cy, 95, "none", OLD, 7)
    f.raw('<path d="M%d,%d A95,95 0 0,1 %d,%d" stroke="%s" stroke-width="6" fill="none" stroke-dasharray="10 5"/>'
          % (cx - 95, cy, cx + 95, cy, NEW))
    f.badge(cx - 95, cy, "آ", GREEN, 15, 14)
    f.badge(cx + 95, cy, "پ", RED, 15, 14)
    f.text(cx, cy, "حلقوی\n(پروکاریوت)", 15, weight=700, color="#1F3864")
    steps_c = ["آغاز", "طویل شدن", "پایان", "حلقوی شدن"]
    for i, s in enumerate(steps_c):
        f.pill(cx + 150 - i * 100, cy + 140, s, "y" if i == 3 else "b", 13)
    # linear
    lx0, lx1, ly = 60, 440, f.top + 150
    f.line(lx0, ly, lx1, ly, OLD, 7)
    for i, x in enumerate((120, 250, 380)):
        f.badge(x, ly, "آ", GREEN, 13, 12)
        f.line(x - 45, ly - 18, x + 45, ly - 18, NEW, 5, "10 5")
    f.text((lx0 + lx1) / 2, ly - 60, "خطی (یوکاریوت): چند جایگاه آغاز", 15, weight=700, color="#1F3864")
    for i, s in enumerate(["آغاز", "طویل شدن", "پایان"]):
        f.pill(380 - i * 120, ly + 140, s, "b", 13)
    f.text(250, ly + 60, "پایان = الگو قرار گرفتن همهٔ نوکلئوتیدها", 14, color="#2E5A24")
    footer(f, "«پایان با جفت شدن همهٔ نوکلئوتیدهای الگو» فقط دربارهٔ دنای خطی درست است ← گزینهٔ ۱ (آ: آغاز، پ: پایان)", "#1F3864", 14, 700)
    return f


# =================================================================== Q13
@chart(13)
def q13():
    f = Fig(W, 450, "استرپتوکوکوس نومونیا و پوشینه")
    cx, cy = 230, f.top + 170
    # irregular capsule
    pts = []
    for k in range(48):
        t = 2 * math.pi * k / 48
        r = 120 + 12 * math.sin(5 * t) + 8 * math.cos(9 * t)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    f.poly(pts + [pts[0]], "#B8962E", 2, "#FFF2CC")
    f.circle(cx, cy, 82, "#E3F1DE", "#5B8F4E", 7)
    f.circle(cx, cy, 74, "#F4FAF1", "#2F5D9B", 2)
    f.text(cx, cy, "یاختهٔ کروی", 15, weight=700, color="#2E5A24")
    f.text(cx, cy + 150, "زرد: پوشینه (ضخیم، نامنظم و غیریکنواخت) — سبز: دیواره — آبی: غشا", 13, color="#333")
    f.text(cx, cy + 180, "گزینهٔ ۳ نادرست: پوشینه منظم و یکنواخت نیست", 15, weight=700, color=RED)
    # transformation flow
    x = 520
    steps = [("بدون پوشینهٔ زنده", "w"), ("دریافت مادهٔ وراثتی از\nپوشینه‌دارِ کشته‌شده", "y"), ("پوشینه‌دار شدن\n(تغییر ظاهری)", "g")]
    for i, (s, k) in enumerate(steps):
        f.box(x, f.top + 20 + i * 110, 340, 70, s, k, 15)
        if i:
            f.arrow(x + 170, f.top + 20 + i * 110 - 38, x + 170, f.top + 20 + i * 110 - 4, BLUE, 3)
    return f


# =================================================================== Q14
@chart(14)
def q14():
    f = Fig(W, 480, "نوکلئوتید آدنین‌دار با قند دئوکسی‌ریبوز در وسط رشته")
    cx, cy, R = 330, f.top + 190, 90
    ang = {"O": -90, "1": -18, "2": 54, "3": 126, "4": 198}
    P = {k: (cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for k, a in ang.items()}
    order = ["O", "1", "2", "3", "4", "O"]
    f.poly([P[k] for k in order], "#555", 4, "#F7F7F7")
    near = {"1", "4"}
    for k, (x, y) in P.items():
        if k == "O":
            f.circle(x, y, 20, RED, "#fff", 3)
            f.text(x, y, "O", 16, weight=700, color="#fff", ltr=True)
        else:
            f.circle(x, y, 18, "#E3F1DE" if k in near else "#FFFFFF", GREEN if k in near else "#888", 3)
            f.text(x, y, fa(k), 15, weight=700, color="#333")
    # substituents
    x1, y1 = P["1"]
    f.line(x1 + 18, y1, x1 + 110, y1 - 10, "#555", 3)
    f.box(x1 + 100, y1 - 50, 140, 70, "آدنین (پورین)\nحلقهٔ ۵ و ۶ضلعی", "y", 14)
    x4, y4 = P["4"]
    f.line(x4 - 18, y4, x4 - 80, y4 - 50, "#555", 3)
    f.circle(x4 - 92, y4 - 60, 16, "#FFFFFF", "#888", 3)
    f.text(x4 - 92, y4 - 60, "۵", 14, weight=700)
    f.line(x4 - 108, y4 - 60, x4 - 170, y4 - 60, "#555", 3)
    f.circle(x4 - 190, y4 - 60, 20, "#D6E4F5", BLUE, 3)
    f.text(x4 - 190, y4 - 60, "P", 15, weight=700, color=BLUE, ltr=True)
    x2, y2 = P["2"]
    f.text(x2 + 40, y2 + 30, "H (بدون OH)", 13.5, color="#555")
    x3, y3 = P["3"]
    f.line(x3 - 10, y3 + 16, x3 - 40, y3 + 70, "#555", 3)
    f.circle(x3 - 48, y3 + 88, 20, "#D6E4F5", BLUE, 3)
    f.text(x3 - 48, y3 + 88, "P", 15, weight=700, color=BLUE, ltr=True)
    f.text(x3 - 48, y3 + 122, "فسفودی‌استر با نوکلئوتید بعد", 13, color="#555")
    # distance bars
    bx = 680
    f.text(bx + 100, f.top + 20, "نزدیکی به اکسیژن حلقه", 15, weight=700, color="#1F3864")
    vals = [("کربن ۱ (متصل به باز)", 1.0), ("کربن ۴ (متصل به کربن ۵) ← گزینهٔ ۳", 1.0),
            ("کربن ۳ و ۲", 0.5), ("کربن ۵ (کنار فسفات، خارج حلقه)", 0.3)]
    for i, (s, v) in enumerate(vals):
        yy = f.top + 60 + i * 64
        f.text(bx + 200, yy, s, 12, anchor="start", color="#2E5A24" if "۴" in s else "#333",
               weight=700 if "۴" in s else 400)
        f.rect(bx + 200 - 200 * v, yy + 12, 200 * v, 18, GREEN if v == 1.0 else "#BBB", "none", 4, 0)
    return f


# =================================================================== Q15
@chart(15)
def q15():
    f = Fig(W, 400, "دو دسته نوکلئوتید آمادهٔ اتصال در حباب همانندسازی")
    cols = [(W - 220, "نوکلئوتید آزاد سه‌فسفاته", "g", 3), (220, "نوکلئوتید تک‌فسفاتهٔ رشتهٔ الگو", "b", 1)]
    for x, t, k, nP in cols:
        y = f.top + 30
        f.box(x - 170, y, 340, 44, t, k, 16)
        # glyph: phosphates - sugar pentagon - base
        gy = y + 110
        for i in range(nP):
            f.circle(x - 120 + i * 34, gy, 14, "#D6E4F5", BLUE, 2)
            f.text(x - 120 + i * 34, gy, "P", 12, weight=700, color=BLUE, ltr=True)
        px = x - 120 + nP * 34 + 20
        pent = [(px + 22 * math.cos(math.radians(a)), gy + 22 * math.sin(math.radians(a))) for a in range(-90, 270, 72)]
        f.poly(pent + [pent[0]], "#555", 2.5, "#FFF2CC")
        f.rect(px + 36, gy - 26, 34, 52, "#F2C14E", "#B8962E", 6, 2)
        f.text(px + 53, gy, "باز", 12, weight=700)
    rows = [("۱) دو پیوند بین فسفاتی", True, False), ("۲) قند سبک‌تر از ریبوز", None, True),
            ("۳) پیوند فسفودی‌استر", False, True), ("۴) حلقهٔ ۶ضلعی کنار ۵ضلعی", True, True)]
    y0 = f.top + 200
    for i, (lab, a, b) in enumerate(rows):
        yy = y0 + i * 40
        both = a is True and b is True
        f.rect(20, yy - 17, W - 40, 34, "#E8F4E3" if both else "#FFFFFF", "#E5E5E5", 5, 1)
        f.text(W / 2, yy, lab, 14.5, weight=700 if both else 400, color="#2E5A24" if both else "#333")
        if a is None:
            f.text(W - 220, yy, "نه همیشه", 13, color=GRAY)
        else:
            f.tick(W - 220, yy, a, 18)
        f.tick(220, yy, b, 18)
    return f


# =================================================================== Q16
@chart(16)
def q16():
    f = Fig(W, 380, "بخش‌های A، B و C در نردبان مارپیچ")
    y = f.top + 120
    ladder(f, 120, 620, y, 130, "AGTCGA")
    f.box(650, y - 100, 220, 46, "A: پورین (دوحلقه‌ای)", "p", 15)
    f.box(650, y - 30, 220, 46, "B: پیریمیدین (تک‌حلقه‌ای)", "b", 15)
    f.box(650, y + 40, 220, 46, "C: ستون قند ـ فسفات", "w", 15)
    f.rect(30, y + 110, W - 60, 76, "#FDF3F2", RED, 10, 1.5, "6 4")
    f.text(W / 2, y + 132, "گزینهٔ ۲ نادرست: نوکلئوتیدهای درون دنا تک‌فسفاته‌اند و پیوند بین فسفاتی ندارند", 15, weight=700, color=RED)
    f.text(W / 2, y + 162, "پیوند فسفودی‌استر ستون پایدار است و شکستن آن زنجیره را می‌گسلد (گزینهٔ ۱ درست)", 13.5, color="#333")
    return f


# =================================================================== Q17
@chart(17)
def q17():
    f = Fig(W, 400, "ساختار نوکلئوتید و ارزیابی موارد")
    y = f.top + 110
    x = 560
    for i in range(3):
        f.circle(x - 160 + i * 46, y, 19, "#D6E4F5", BLUE, 2.5)
        f.text(x - 160 + i * 46, y, "P", 14, weight=700, color=BLUE, ltr=True)
        if i:
            f.line(x - 160 + i * 46 - 27, y, x - 160 + i * 46 - 19, y, RED, 4)
    pent = [(x + 30 * math.cos(math.radians(a)), y + 30 * math.sin(math.radians(a))) for a in range(-90, 270, 72)]
    f.poly(pent + [pent[0]], "#555", 3, "#FFF2CC")
    f.text(x, y, "قند", 13, weight=700)
    f.rect(x + 60, y - 40, 70, 80, "#F8DDD9", "#B5564A", 8, 2.5)
    f.text(x + 95, y, "باز آلی", 13, weight=700, color="#7A2A20")
    f.line(x + 28, y - 8, x + 60, y - 8, "#555", 3)
    f.text(x - 114, y - 46, "پیوندهای پرانرژی بین فسفات‌ها (مورد ب)", 13, color=RED)
    f.text(x + 50, y + 62, "قند–نیتروژن نزدیک قند–فسفات (مورد ج)", 13, color="#2E5A24")
    rows = [("الف", "هر یک برای فعالیت به اتصال به هم‌نوع نیاز دارد", False), ("ب", "هر نوع سه‌فسفاته می‌تواند منبع انرژی باشد", True),
            ("ج", "پیوند قند–نیتروژن نزدیک توالی قند–فسفات", True), ("د", "همهٔ انواع در نوکلئیک اسید باکتری به دو فسفات متصل‌اند", False)]
    y0 = y + 110
    for i, (k, s, ok) in enumerate(rows):
        yy = y0 + i * 38
        f.text(W - 40, yy, k + ") " + s, 14.5, anchor="start", color="#2E5A24" if ok else "#7A2A20", weight=700 if ok else 400)
        f.tick(60, yy, ok, 18)
    return f


# =================================================================== Q18
@chart(18)
def q18():
    f = Fig(W, 440, "دنای حاصل از دور اول در سه طرح (تیره: قدیم، روشن: جدید)")

    def strand(x0, y, segs):
        x = x0
        for L, old in segs:
            f.line(x, y, x + L, y, OLD if old else NEW, 9, cap="butt")
            x += L

    models = [("حفاظتی", [[(220, True)], [(220, True)]], [[(220, False)], [(220, False)]]),
              ("نیمه‌حفاظتی", [[(220, True)], [(220, False)]], [[(220, True)], [(220, False)]]),
              ("غیرحفاظتی", [[(70, True), (80, False), (70, True)], [(70, False), (80, True), (70, False)]],
               [[(70, False), (80, True), (70, False)], [(70, True), (80, False), (70, True)]])]
    for i, (name, d1, d2) in enumerate(models):
        y = f.top + 40 + i * 100
        f.text(W - 80, y + 20, name, 16, weight=700, color="#1F3864")
        for j, d in enumerate((d1, d2)):
            x0 = 420 - j * 300
            strand(x0, y, d[0])
            strand(x0, y + 34, d[1])
            for k in range(6):
                f.line(x0 + 20 + k * 36, y + 6, x0 + 20 + k * 36, y + 28, "#BBB", 2)
    f.text(W / 2, f.top + 330, "پیوند هیدروژنی قدیم–جدید: حفاظتی ✘ — غیرحفاظتی ✔ ← وجه تمایز است، نه تشابه (گزینهٔ ۳ نادرست)", 14.5, weight=700, color=RED)
    footer(f, "فسفودی‌استر قدیم–جدید و شکستن فسفودی‌استر دنای اولیه فقط در طرح غیرحفاظتی دیده می‌شود.")
    return f


# =================================================================== Q19
@chart(19)
def q19():
    f = Fig(W, 400, "سه طرح همانندسازی × ویژگی‌ها")
    cols = ["حفاظتی", "نیمه‌حفاظتی", "غیرحفاظتی"]
    xs = [420, 270, 120]
    y0 = f.top + 30
    for x, c in zip(xs, cols):
        f.text(x, y0, c, 15, weight=700, color="#1F3864")
    rows = [("ترتیب بازها مانند دنای اولیه", (1, 1, 1)), ("سازگار با مشاهدات چارگاف", (1, 1, 1)),
            ("نوکلئازی در دنای اولیه", (0, 0, 1)), ("هر دو دنا بخش جدید دارند", (0, 1, 1)),
            ("چگالی یکسان دو دنا در دور اول", (0, 1, 1)), ("تأیید در آزمایش مزلسون و استال", (0, 1, 0))]
    for i, (lab, v) in enumerate(rows):
        yy = y0 + 42 + i * 42
        f.rect(20, yy - 18, W - 40, 36, "#F7F7F7" if i % 2 else "#FFFFFF", "#E5E5E5", 5, 1)
        f.text(W - 40, yy, lab, 14.5, anchor="start", color="#333")
        for x, ok in zip(xs, v):
            f.tick(x, yy, bool(ok), 18)
    footer(f, "در طرح غیرحفاظتی، غالب پیوندهای فسفودی‌استر بین نوکلئوتیدهای هم‌نسل است ← گزینهٔ ۲ نادرست", "#7A2A20", 14.5, 700)
    return f


# =================================================================== Q20
@chart(20)
def q20():
    f = Fig(W, 400, "کدام بخش نوکلئوتید در یک مولکول دنا تغییر می‌کند؟")
    parts = [("قند", "ثابت: دئوکسی‌ریبوز", 0.15, "y"), ("گروه فسفات", "ثابت: یک فسفات", 0.15, "b"),
             ("باز آلی", "متغیر: A، T، G، C ← اطلاعات وراثتی", 1.0, "p")]
    y0 = f.top + 40
    for i, (name, s, v, k) in enumerate(parts):
        yy = y0 + i * 80
        f.text(W - 40, yy + 16, name, 17, anchor="start", weight=700, color=PAL[k][2])
        f.rect(W - 180 - 520 * v, yy, 520 * v, 32, PAL[k][1], "none", 6, 0, op=0.85)
        if v < 1:
            f.text(W - 195 - 520 * v, yy + 16, s, 14, anchor="start", weight=700, color="#333")
        else:
            f.text(W - 180 - 260, yy + 16, s, 14, weight=700, color="#fff")
    f.text(W / 2, y0 + 250, "در پله‌های نردبان، بازهای مکمل با پیوند هیدروژنی و به صورت اختصاصی جفت می‌شوند (A–T و G–C) ← گزینهٔ ۳", 14.5, weight=700, color="#2E5A24")
    footer(f, "نمودار: میزان تنوع هر بخش در نوکلئوتیدهای یک مولکول دنا (طرح‌واره)")
    return f


# =================================================================== build
def build_charts(outdir):
    os.makedirs(outdir, exist_ok=True)
    man = []
    for n in sorted(CH):
        base = os.path.join(outdir, "q%02d_1" % n)
        open(base + ".svg", "w", encoding="utf-8").write(CH[n]().svg())
        man.append({"svg": base + ".svg", "png": base + ".png"})
    json.dump(man, open(os.path.join(outdir, "manifest.json"), "w"))


if __name__ == "__main__":
    build_charts(sys.argv[1] if len(sys.argv) > 1 else "charts")
