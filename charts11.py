# Chart section of each question (exam: biology 11, chapter 1 — nervous regulation).
# Every function returns a Fig; build_charts() writes SVG files + a manifest for render_charts.js.
import json, math, os, sys
from svgfig import Fig, Axes, ap, wave, fa, tw, PAL, BLUE, GREEN, RED, GOLD, GRAY, PURPLE

W = 900
CH = {}


def chart(n):
    def deco(fn):
        CH.setdefault(n, []).append(fn)
        return fn
    return deco


def ap_axes(f, x=110, y=None, w=720, h=300, yr=(-125, 50), xr=(0, 4.2)):
    y = f.top + 20 if y is None else y
    a = Axes(f, x, y, w, h, xr, yr)
    a.frame("زمان (هزارم ثانیه)", "پتانسیل درون یاخته (میلی‌ولت)", yticks=(-70, 0, 30))
    return a


# ---------------------------------------------------------------- shared neuron drawing
def neuron(f, x, y, scale=1.0, kind="motor", myelin=True, color=BLUE, labels=True):
    """simple neuron glyph; x,y = centre of cell body; axon runs to the left"""
    s = scale
    if kind == "sensory":
        # one process leaves the body then splits: dendrite to the right, axon to the left
        f.line(x, y + 26 * s, x, y + 60 * s, color, 5 * s)
        f.line(x, y + 60 * s, x + 170 * s, y + 60 * s, color, 5 * s)
        f.line(x, y + 60 * s, x - 170 * s, y + 60 * s, color, 5 * s)
        for k in (-1, 1):
            f.line(x + 170 * s, y + 60 * s, x + 200 * s, y + (60 + 18 * k) * s, color, 3 * s)
            f.line(x - 170 * s, y + 60 * s, x - 198 * s, y + (60 + 16 * k) * s, color, 3 * s)
        f.circle(x, y, 26 * s, "#E8EEF8", color, 3 * s)
        f.circle(x, y, 9 * s, color, color, 1)
        return
    for ang in (35, 80, 125, 160, 200, 250, 300):
        if 160 < ang < 200:
            continue
        a = math.radians(ang)
        x2, y2 = x + math.cos(a) * 62 * s, y - math.sin(a) * 62 * s
        f.line(x + math.cos(a) * 24 * s, y - math.sin(a) * 24 * s, x2, y2, color, 4 * s)
        for d in (-25, 25):
            b = a + math.radians(d)
            f.line(x2, y2, x2 + math.cos(b) * 22 * s, y2 - math.sin(b) * 22 * s, color, 2.5 * s)
    f.line(x - 26 * s, y, x - 230 * s, y, color, 5 * s)
    if myelin:
        for i in range(4):
            x0 = x - (50 + i * 46) * s
            f.rect(x0 - 36 * s, y - 9 * s, 36 * s, 18 * s, "#FFE9A8", GOLD, 6, 1.5)
    for d in (-18, 0, 18):
        f.line(x - 230 * s, y, x - 256 * s, y + d * s, color, 3 * s)
        f.circle(x - 258 * s, y + d * s, 4 * s, color, color, 1)
    f.circle(x, y, 26 * s, "#E8EEF8", color, 3 * s)
    f.circle(x, y, 9 * s, color, color, 1)


# =================================================================== Q1
@chart(1)
def q1():
    f = Fig(W, 520, "نوار مغز: از علت تا تغییر امواج (طرح‌واره)")
    rows = [
        ("طبیعی", "امواج غیرهم‌شکل (حتی در حالت طبیعی)", "g", [(9, 2.1, 0), (5, 3.7, 1), (3, 6.3, 2)], 1.0),
        ("مصرف الکل", "کاهش فعالیت نورون‌ها ← امواج کندتر\n(فاصلهٔ امواج بیشتر)", "y", [(9, 1.0, 0), (5, 1.8, 1), (3, 3.1, 2)], 1.0),
        ("بیماری MS", "تخریب میلین‌سازها در CNS ← اختلال گسترده", "p", [(9, 2.1, 0), (5, 3.7, 1), (3, 6.3, 2)], 0.0),
    ]
    y = f.top + 20
    for i, (lab, note, k, comps, reg) in enumerate(rows):
        yc = y + i * 150 + 55
        f.box(W - 190, yc - 40, 170, 80, lab, k, 19)
        x0, x1 = 300, W - 215
        f.line(x0, yc, x1, yc, "#E0E0E0", 1, "4 4")
        pts = []
        for j in range(401):
            t = j / 400 * 4
            v = wave(t, comps)
            if reg == 0.0:
                v = v * (0.35 + 0.9 * abs(math.sin(7.3 * t) * math.cos(2.1 * t))) + 6 * math.sin(13 * t)
            pts.append((x1 - (x1 - x0) * j / 400, yc - v * 2.1))
        f.poly(pts, PAL[k][1], 2.4)
        f.text(150, yc, note, 15, color="#333")
    f.text(W / 2, f.h - 22, "نوار مغزی = جریان الکتریکی ثبت‌شدهٔ نورون‌های مغز؛ هر اختلالی که کار نورون‌ها را تغییر دهد، در نوار دیده می‌شود.",
           14, color="#555")
    return f


# =================================================================== Q2
@chart(2)
def q2():
    f = Fig(W, 410, "فاصله از جسم یاخته‌ای در یک نورون میلین‌دار")
    y = f.top + 125
    cx = 660
    f.line(cx + 30, y, cx + 200, y, BLUE, 6)
    for d in (-20, 20):
        f.line(cx + 200, y, cx + 228, y + d, BLUE, 3)
    f.circle(cx, y, 34, "#E8EEF8", BLUE, 3)
    f.circle(cx, y, 11, BLUE, BLUE, 1)
    f.line(cx - 34, y, 72, y, BLUE, 6)
    segs = []
    x = cx - 70
    for i in range(4):
        segs.append((x - 110, x))
        x -= 110 + 18
    for a, b in segs:
        f.rect(a, y - 15, b - a, 30, "#FFE9A8", GOLD, 8, 2)
    for d in (-20, 0, 20):
        f.line(72, y, 48, y + d, BLUE, 3)
        f.circle(46, y + d, 5, BLUE, BLUE, 1)

    def pin(x, lab, k, up=True, num=None, bw=136, off=0):
        yy = y - 78 if up else y + 78
        bx = min(max(x + off, bw / 2 + 8), W - bw / 2 - 22)
        f.line(x, y + (-18 if up else 18), x, yy + (22 if up else -22), PAL[k][1], 2, "3 3")
        f.box(bx - bw / 2, yy - 22, bw, 44, lab, k, 14.5)
        if num:
            f.badge(bx + bw / 2 - 2, yy - 22, num, PAL[k][1], 13, 14)
    pin(cx - 52, "ابتدای آسه\n(بدون میلین)", "w", True, bw=118, off=40)
    pin(segs[0][0] - 9, "اولین گرهٔ رانویه", "y", True, fa(1))
    pin((segs[0][0] + segs[0][1]) / 2, "اولین غلاف میلین", "g", False, fa(3))
    pin(46, "پایانهٔ آسه", "p", False, fa(4))
    pin(cx + 214, "انتهای دارینه", "p", True, fa(2))
    ya = f.h - 58
    f.arrow(cx, ya, 40, ya, GRAY, 2)
    f.arrow(cx, ya, cx + 225, ya, GRAY, 2)
    f.circle(cx, ya, 6, BLUE, BLUE)
    f.text(cx, ya + 24, "جسم یاخته‌ای (فاصلهٔ صفر)", 14, color="#333")
    f.text(330, ya - 16, "دورتر شدن در طول آسه ←", 14, color="#555")
    f.text(cx + 115, ya - 16, "→ دورتر در دارینه", 14, color="#555")
    f.text(W / 2, f.h - 12, "ترتیب نزدیکی به جسم یاخته‌ای در آسه: ابتدای بدون میلین ← اولین غلاف (۳) ← اولین گره (۱) ← … ← پایانه (۴)", 13.5, weight=700, color="#1F3864")
    return f


# =================================================================== Q3
@chart(3)
def q3():
    f = Fig(W, 495, "سه بخش نورون و توانایی‌های آن‌ها")
    parts = [("دارینه (دندریت)", W - 170), ("جسم یاخته‌ای", W / 2), ("آسه (آکسون)", 170)]
    y = f.top + 30
    for name, x in parts:
        f.box(x - 125, y, 250, 56, name, "b", 19)
    f.arrow(W - 300, y + 28, W / 2 + 130, y + 28, BLUE, 3)
    f.arrow(W / 2 - 130, y + 28, 300, y + 28, BLUE, 3)
    f.text(W / 2, y + 80, "مسیر پیام در نورون", 14, color=BLUE)
    feats = [
        ("الف) تشکیل همایه", (True, True, True)),
        ("ب) تحریک‌پذیری (تولید پیام)", (True, True, True)),
        ("ج) دریافت پیام", (True, True, False)),
        ("د) هدایت پیام به انتهای خود", (False, None, True)),
    ]
    y0 = y + 140
    for i, (lab, oks) in enumerate(feats):
        yy = y0 + i * 62
        both = all(o is True for o in oks)
        f.rect(20, yy - 26, W - 40, 52, "#F4F9F1" if both else "#FDF3F2", "#DDD", 8, 1)
        f.text(W / 2, yy - 12, lab, 15, weight=700, color="#2E5A24" if both else "#7A2A20")
        for (name, x), ok in zip(parts, oks):
            if ok is None:
                f.text(x, yy + 12, "—", 18, color=GRAY)
            else:
                f.tick(x, yy + 12, ok, 20)
    f.text(W / 2, f.h - 20, "مورد «د»: دارینه پیام را از انتها به ابتدای خود (به سوی جسم یاخته‌ای) هدایت می‌کند، نه به انتهای خود.", 14, color="#555")
    return f


# =================================================================== Q4
@chart(4)
def q4():
    f = Fig(W, 430, "تعداد محل خروج رشته‌ها از جسم یاخته‌ای")
    y = f.top + 20
    f.box(W / 2 - 200, y, 400, 50, "رشته‌های عصبی از چند محل جسم یاخته‌ای خارج می‌شوند؟", "b", 16)
    f.carrow("M%d,%d C%d,%d %d,%d %d,%d" % (W / 2 + 120, y + 50, W / 2 + 160, y + 90, 680, y + 70, 680, y + 110), GREEN)
    f.carrow("M%d,%d C%d,%d %d,%d %d,%d" % (W / 2 - 120, y + 50, W / 2 - 160, y + 90, 220, y + 70, 220, y + 110), PURPLE)
    f.box(560, y + 112, 240, 46, "یک محل ← نورون حسی", "g", 17)
    f.box(100, y + 112, 240, 46, "چند محل ← حرکتی و رابط", "v", 17)
    neuron(f, 680, y + 200, 0.55, "sensory", color="#3E7B34")
    neuron(f, 270, y + 210, 0.55, "motor", color=PURPLE)
    f.text(680, y + 290, "یک رشته خارج و سپس دو شاخه می‌شود:\nیک دارینه + یک آسه", 15, color="#2E5A24")
    f.text(220, y + 290, "چند دارینه + یک آسه\n(آسه از هر دارینه بلندتر)", 15, color="#3E2A63")
    f.text(W / 2, f.h - 18, "«چند» در زیست‌شناسی یعنی بیش از دو؛ میلین‌دار بودن ویژگی هیچ نوع خاصی نیست (هر سه نوع می‌توانند میلین‌دار یا بدون میلین باشند).", 13.5, color="#555")
    return f


# =================================================================== Q5
@chart(5)
def q5():
    f = Fig(W, 420, "نقطهٔ اول نورون با چه چیزی تحریک می‌شود؟")
    y = f.top + 16
    f.box(W / 2 - 150, y, 300, 50, "تحریک نقطهٔ اول نورون", "b", 18)
    f.arrow(W / 2 + 60, y + 50, 680, y + 100, GREEN, 3)
    f.arrow(W / 2 - 60, y + 50, 220, y + 100, GOLD, 3)
    f.box(560, y + 104, 240, 54, "محرک\n(دارینه = گیرندهٔ حسی)", "g", 17)
    f.box(100, y + 104, 240, 54, "ناقل عصبی\n(در محل همایه)", "y", 17)
    f.arrow(680, y + 158, 680, y + 196, GREEN, 3)
    f.arrow(220, y + 158, 220, y + 196, GOLD, 3)
    f.box(560, y + 200, 240, 50, "فقط برخی نورون‌های حسی", "g", 16)
    f.box(70, y + 200, 300, 50, "حسی (برخی)، حرکتی و رابط", "y", 16)
    f.arrow(680, y + 250, 680, y + 288, GREEN, 3)
    f.box(520, y + 292, 320, 58, "به‌طور حتم پیام را به سوی\nدستگاه عصبی مرکزی می‌آورد  ✔", "g", 16)
    f.text(220, y + 318, "هر سه نوع ← درباره‌شان «حتم» نمی‌توان گفت\n(میلین، طول رشته‌ها و … متغیرند)", 15, color="#6B5410")
    return f


# =================================================================== Q6
@chart(6)
def q6():
    f = Fig(W, 330, "مراحل مشترک کار همهٔ نورون‌ها")
    y = f.top + 40
    steps = [("۱. تولید پیام", "با محرک یا با ناقل عصبی", "b"), ("۲. هدایت پیام", "نقطه به نقطه در طول یاخته", "b"),
             ("۳. انتقال پیام", "همیشه به یاختهٔ دیگر (پاسخ)", "g")]
    xs = [W - 160, W / 2, 160]
    for (t, s, k), x in zip(steps, xs):
        f.box(x - 125, y, 250, 76, t + "\n" + s, k, 18)
    f.arrow(W - 290, y + 38, W / 2 + 130, y + 38, BLUE, 3)
    f.arrow(W / 2 - 130, y + 38, 290, y + 38, BLUE, 3)
    ex = [("گزینهٔ ۱ ✘", "اگر پیام در جسم یاخته‌ای دریافت شود،\nحرکتی به سمت جسم یاخته‌ای ندارد", W - 160),
          ("گزینهٔ ۲ ✘", "نقطهٔ اول با محرک یا ناقل تحریک\nمی‌شود، نه با نقطهٔ قبلی", W / 2),
          ("گزینهٔ ۳ ✘", "دارینهٔ گیرندهٔ حسی\nدر همایه شرکت نمی‌کند", 160)]
    for lab, s, x in ex:
        f.line(x, y + 76, x, y + 118, RED, 2, "4 4")
        f.rect(x - 140, y + 120, 280, 92, "#FDF3F2", RED, 10, 1.5, "5 4")
        f.text(x, y + 142, lab, 16, weight=700, color=RED)
        f.text(x, y + 180, s, 14, color="#333")
    return f


# =================================================================== Q7
@chart(7)
def q7():
    f = Fig(W, 470, "بسته شدن کانال‌های دریچه‌دار در پتانسیل عمل")
    a = ap_axes(f)
    a.band(1.0, 1.55, BLUE, 0.10, "بالارو\nدریچهٔ سدیمی باز", 13, a.Y(-100))
    a.band(1.55, 2.45, GOLD, 0.12, "پایین‌رو\nدریچهٔ پتاسیمی باز", 13, a.Y(-100), "#8A6A00")
    a.band(2.45, 3.4, GREEN, 0.12, "بیشترین فعالیت\nپمپ سدیم ـ پتاسیم", 13, a.Y(-100), "#2E5A24")
    a.curve(ap, 0, 4.2)
    a.dot(1.55, 30, "بسته شدن دریچهٔ سدیمی (مثبت ۳۰)", RED, dy=-22, dx=-20)
    a.dot(2.45, -70, "بسته شدن دریچهٔ پتاسیمی (منفی ۷۰)", PURPLE, dy=-26, dx=130)
    f.text(W / 2, f.h - 18, "بلافاصله پس از بسته شدن دریچهٔ پتاسیمی، فعالیت پمپ بیشینه است؛ کانال‌های نشتی همیشه باز و پتاسیم همیشه در حال خروج است.", 13.5, color="#555")
    return f


# =================================================================== Q8
@chart(8)
def q8():
    f = Fig(W, 500, "اثر مهار پمپ سدیم ـ پتاسیم (طرح‌واره)")
    a = ap_axes(f, w=520)
    a.curve(lambda t: ap(t, t0=0.6, rise=0.5, fall=0.8), 0, 4.2, BLUE, 3.2)
    a.curve(lambda t: ap(t, t0=0.6, rise=0.5, fall=0.8, peak=30, rest2=-62) if t < 2.3 else
            ap(t, t0=2.6, rise=0.5, fall=0.8, peak=18, rest=-62, rest2=-57), 0, 4.2, RED, 3.2, "9 6")
    f.line(170, a.y + a.h + 66, 210, a.y + a.h + 66, BLUE, 3.2)
    f.text(255, a.y + a.h + 66, "طبیعی", 14)
    f.line(310, a.y + a.h + 66, 350, a.y + a.h + 66, RED, 3.2, "9 6")
    f.text(410, a.y + a.h + 66, "پمپ مهارشده", 14)
    a.dot(3.15, 18, "ج) قلهٔ کمتر", RED, dy=-20)
    a.dot(3.95, -57, "د) اختلاف پتانسیل\nآرامش کمتر", RED, dy=42, dx=-30)
    # bars on the right
    bx = 680
    f.text(bx + 95, f.top + 20, "پیامدهای دیگر", 16, weight=700, color="#1F3864")
    items = [("الف) مصرف ATP", 0.3, "کاهش"), ("ب) یون‌های مثبت درون یاخته", 0.9, "افزایش"),
             ("ب) جذب آب و حجم یاخته", 0.85, "تورم")]
    for i, (lab, v, s) in enumerate(items):
        yy = f.top + 62 + i * 122
        f.text(bx + 95, yy - 18, lab, 14, weight=700, color="#333")
        f.rect(bx + 190 - 190 * 0.6, yy, 190 * 0.6, 24, "#B9CBE6", "none", 5, 0)
        f.text(bx + 190 - 190 * 0.3, yy + 12, "طبیعی", 12, color="#1F3864")
        f.rect(bx + 190 - 190 * v, yy + 30, 190 * v, 24, "#F2B8B0", "none", 5, 0)
        f.text(bx + 190 - 190 * v / 2, yy + 42, "مهارشده", 12, color="#7A2A20")
        f.text(bx + 95, yy + 72, s + (" ↓" if v < 0.6 else " ↑"), 14, weight=700, color=RED)
    return f


# =================================================================== Q9
@chart(9)
def q9():
    f = Fig(W, 470, "ترتیب زمانی رویدادهای گزینه‌ها پس از تحریک")
    a = ap_axes(f)
    a.curve(ap, 0, 4.2)
    a.band(1.55, 2.45, GOLD, 0.10)
    a.dot(1.55, 30, "۱) قله: کانال‌های دریچه‌دار بسته", GREEN, dy=-20, dx=-30)
    a.dot(1.95, -20, "۴) بیشترین نفوذپذیری به پتاسیم", GOLD, dx=150, dy=0)
    a.dot(2.45, -70, "۲ و ۳) پایان پتانسیل عمل:\nبیشترین سدیم و کمترین پتاسیم درون یاخته", RED, dx=150, dy=-46)
    f.text(W / 2, f.h - 18, "ترتیب وقوع: ۱ ← ۴ ← (۲ و ۳)؛ پس گزینهٔ ۱ زودتر از بقیه رخ می‌دهد.", 15, weight=700, color="#1F3864")
    return f


# =================================================================== Q10
@chart(10)
def q10():
    f = Fig(W, 490, "چه زمانی عبور سدیم از غشا بیشتر می‌شود؟")
    a = ap_axes(f)
    a.band(1.0, 1.55, BLUE, 0.16, "حالت ۱) بالارو:\nکانال دریچه‌دار سدیمی", 13, a.Y(-100))
    a.band(2.45, 3.4, GREEN, 0.16, "حالت ۲) پس از پتانسیل عمل:\nفعالیت بیشتر پمپ", 13, a.Y(-100), "#2E5A24")
    a.curve(ap, 0, 4.2)
    f.text(W / 2, f.h - 40, "در همهٔ لحظه‌ها مقدار یون سدیم بیرون یاخته بیشتر از درون آن است ← گزینهٔ ۴", 15, weight=700, color="#6B5410")
    f.text(W / 2, f.h - 14, "چون افزایش عبور سدیم در دو حالت رخ می‌دهد، گزینه‌های ۱ تا ۳ «حتمی» نیستند.", 14, color="#555")
    return f


# =================================================================== Q11
@chart(11)
def q11():
    f = Fig(W, 450, "مقایسهٔ نفوذپذیری غشا به Na⁺ و K⁺ در مراحل مختلف (کیفی)")
    x0, y0, h = 120, f.top + 30, 260
    f.arrow(x0, y0 + h, W - 40, y0 + h, "#444", 1.8)
    f.arrow(x0, y0 + h, x0, y0 - 10, "#444", 1.8)
    f.text(x0 - 50, y0 + h / 2, "نفوذپذیری نسبی", 15, color="#444", rot=-90)
    phases = [("آرامش", 0.45, 0.12, "K⁺ > Na⁺"), ("بالارو", 0.40, 0.9, "Na⁺ > K⁺"),
              ("پایین‌رو", 0.95, 0.10, "K⁺ ≫ Na⁺"), ("قله / پایان", 0.45, 0.12, "K⁺ > Na⁺")]
    gw = (W - 40 - x0) / len(phases)
    for i, (lab, k, na, s) in enumerate(phases):
        cx = W - 40 - gw * (i + 0.5)
        for j, (v, col, nm) in enumerate(((k, GOLD, "K⁺"), (na, BLUE, "Na⁺"))):
            bx = cx + (6 if j == 0 else -54)
            f.rect(bx, y0 + h - v * h, 48, v * h, col, col, 4, 1, op=0.85)
            f.text(bx + 24, y0 + h - v * h - 12, nm, 13, weight=700, color=col)
        f.text(cx, y0 + h + 22, lab, 16, weight=700, color="#333")
        f.text(cx, y0 + h + 48, s, 14, color=RED if "Na⁺ >" in s else "#555")
    f.text(W / 2, f.h - 16, "نفوذپذیری به سدیم فقط در بالارو بیشتر است؛ در این مرحله دریچهٔ کانال سدیمی (به سمت خارج) باز است ← گزینهٔ ۳", 14, color="#1F3864")
    return f


# =================================================================== Q12
@chart(12)
def q12():
    f = Fig(W, 450, "پتانسیل غشا پس از تحریک: طبیعی در برابر کانال سدیمیِ ازکارافتاده")
    a = ap_axes(f, h=280)
    a.curve(ap, 0, 4.2, "#9DB4D6", 3, "8 6")
    a.curve(lambda t: -70, 0, 4.2, RED, 4)
    f.arrow(a.X(1.0), a.Y(-70) + 60, a.X(1.0), a.Y(-70) + 8, GREEN, 3)
    f.text(a.X(1.0), a.Y(-70) + 74, "تحریک", 14, weight=700, color=GREEN)
    f.text(a.X(2.2), a.Y(45), "خط‌چین: پتانسیل عمل طبیعی", 14, color="#2F5D9B")
    f.text(a.X(3.2), a.Y(-70) - 18, "بدون کانال سدیمی: ثابت در منفی ۷۰ (گزینهٔ ۲)", 15, weight=700, color=RED)
    f.text(W / 2, f.h - 16, "سدیم وارد نمی‌شود ← درون یاخته مثبت‌تر نمی‌شود ← کانال دریچه‌دار پتاسیمی هم باز نمی‌شود.", 14, color="#555")
    return f


# =================================================================== Q13
@chart(13)
def q13():
    f = Fig(W, 470, "تصویر لحظه‌ای پتانسیل در طول یک رشتهٔ بدون میلین")
    a = Axes(f, 110, f.top + 20, 720, 250, (0, 10), (-100, 50))
    a.frame("مکان در طول رشته", "پتانسیل (میلی‌ولت)", yticks=(-70, 0, 30))

    def prof(x):  # wave travelling to the right (towards point 1)
        return ap(10.5 - x, t0=3.0, rise=1.4, fall=2.6)
    a.curve(prof, 0, 10)
    pts = {"۴": 2.0, "۳": 4.9, "۲": 7.0, "۱": 9.2}
    for k, x in pts.items():
        v = prof(x)
        a.dot(x, v, k, RED, r=8, dy=-24, size=18)
    f.text(a.X(2.0), a.Y(-70) - 62, "پس از پتانسیل عمل\n(بیشترین فعالیت پمپ)", 13, color="#2E5A24")
    f.text(a.X(4.9) - 70, a.Y(prof(4.9)), "پایین‌رو", 13, color="#6B5410")
    f.text(a.X(7.0) + 52, a.Y(prof(7.0)), "بالارو", 13, color=BLUE)
    f.text(a.X(9.2), a.Y(-70) - 52, "هنوز در آرامش", 13, color="#555")
    ya = a.y + a.h + 70
    f.arrow(a.X(3.0), ya, a.X(9.4), ya, GREEN, 4)
    f.text(a.X(6.2), ya + 22, "جهت هدایت: از ۳ به ۲ (به سوی ۱)", 15, weight=700, color=GREEN)
    f.text(W / 2, f.h - 14, "اگر نقطهٔ ۱ به جسم یاخته‌ای نزدیک‌تر باشد، پیام به سوی جسم یاخته‌ای می‌رود ← رشته، دارینه است (گزینهٔ ۱).", 14, color="#1F3864")
    return f


# =================================================================== Q14
@chart(14)
def q14():
    f = Fig(W, 560, "مراحل انتقال پیام عصبی و نیاز به ATP")
    steps = [
        ("ساخت ناقل در یاختهٔ عصبی و ذخیره در ریزکیسه", True, ""),
        ("حرکت ریزکیسه‌ها تا پایانهٔ آسه", None, ""),
        ("ترشح ناقل با برون‌رانی", True, "الف"),
        ("حرکت (انتشار) ناقل در فضای همایه‌ای", False, "ج"),
        ("اتصال به گیرنده و باز شدن کانال ← تغییر نفوذپذیری", False, "د"),
        ("ورود یون‌ها و تغییر پتانسیل یاختهٔ پس‌همایه‌ای", False, ""),
        ("تخلیهٔ ناقل: جذب دوباره به یاختهٔ پیش‌همایه‌ای / تجزیه", True, "ب"),
    ]
    y = f.top + 8
    for i, (s, atp, it) in enumerate(steps):
        yy = y + i * 68
        k = "w" if atp is None else ("p" if atp else "g")
        f.box(170, yy, 560, 50, s, k, 16)
        f.badge(W - 140, yy + 25, fa(i + 1), BLUE, 16, 16)
        if it:
            f.pill(W - 70, yy + 25, "مورد " + it, "y", 14)
        lab = "بدون مصرف ATP" if atp is False else ("با مصرف ATP" if atp else "—")
        f.text(90, yy + 25, lab, 14, weight=700, color=GREEN if atp is False else (RED if atp else GRAY))
        if i:
            f.arrow(450, yy - 18, 450, yy - 2, BLUE, 2.5)
    f.text(W / 2, f.h - 16, "دو مورد (ج و د) بدون مصرف ATP انجام می‌شوند.", 16, weight=700, color="#2E5A24")
    return f


# =================================================================== Q15
@chart(15)
def q15():
    f = Fig(W, 500, "پروتئین‌هایی که جایگاه ویژهٔ ناقل عصبی دارند")
    ct, cb, ce = 560, 390, 160      # columns: excitatory receptor, inhibitory receptor, enzyme
    y = f.top + 8
    f.box(250, y, 380, 48, "پروتئین دارای جایگاه اتصال به ناقل", "b", 17)
    f.arrow(500, y + 48, (ct + cb) / 2, y + 92, BLUE, 3)
    f.arrow(380, y + 48, ce, y + 92, BLUE, 3)
    f.box((ct + cb) / 2 - 150, y + 96, 300, 54, "گیرندهٔ ناقل (کانال)\nدر غشای یاختهٔ پس‌همایه‌ای", "g", 15.5)
    f.box(ce - 120, y + 96, 240, 54, "آنزیم تجزیه‌کنندهٔ ناقل\nدر فضای همایه‌ای", "y", 15.5)
    f.arrow((ct + cb) / 2 + 40, y + 150, ct, y + 186, GREEN, 2.5)
    f.arrow((ct + cb) / 2 - 40, y + 150, cb, y + 186, GREEN, 2.5)
    f.box(ct - 70, y + 190, 140, 40, "تحریکی", "g", 15)
    f.box(cb - 70, y + 190, 140, 40, "بازدارنده", "g", 15)
    f.line(ce, y + 150, ce, y + 230, GOLD, 2, "4 4")
    f.text(W - 125, y + 210, "ویژگی", 16, weight=700, color="#1F3864")
    rows = [("الف) همواره به دو ناقل متصل", (True, True, False)),
            ("ب) تغییر برهم‌کنش‌ها (تغییر شکل)", (True, True, True)),
            ("ج) افزایش نفوذپذیری به سدیم", (True, False, False)),
            ("د) تغییر اختلاف پتانسیل غشا", (True, True, False))]
    y0 = y + 262
    for i, (lab, oks) in enumerate(rows):
        yy = y0 + i * 44
        allok = all(oks)
        f.rect(20, yy - 19, W - 40, 38, "#E8F4E3" if allok else ("#F7F7F7" if i % 2 else "#FFFFFF"), "#E2E2E2", 5, 1)
        f.text(W - 30, yy, lab, 14.5, anchor="start", weight=700 if allok else 400, color="#2E5A24" if allok else "#333")
        for x, ok in zip((ct, cb, ce), oks):
            f.tick(x, yy, ok, 19)
    f.text(W / 2, f.h - 14, "فقط مورد «ب» دربارهٔ همهٔ این پروتئین‌ها درست است ← ۱ مورد", 15, weight=700, color="#2E5A24")
    return f


# =================================================================== Q16
@chart(16)
def q16():
    f = Fig(W, 430, "یاختهٔ عصبی (x) در برابر یاختهٔ پشتیبانِ میلین‌ساز (y)")
    hdr_y = f.top + 20
    cx_x, cx_y = 310, 120
    f.box(cx_x - 80, hdr_y, 160, 44, "x: نورون", "b", 17)
    f.box(cx_y - 80, hdr_y, 160, 44, "y: میلین‌ساز", "y", 17)
    rows = [("۱) شبکهٔ آندوپلاسمی صاف گسترده", False, True),
            ("۲) نقش در هم‌ایستایی مایع اطراف", True, True),
            ("۳) رشته‌ها در ابتدا ضخیم‌ترند", True, False),
            ("۴) ضخامت متفاوت محل هسته", True, True)]
    for i, (lab, a, b) in enumerate(rows):
        yy = hdr_y + 86 + i * 62
        diff = a != b and a
        f.rect(20, yy - 24, W - 40, 48, "#E8F4E3" if diff else ("#FFFFFF" if i % 2 else "#F7F7F7"), "#DDD", 6, 1)
        f.text(W - 40, yy, lab, 16, anchor="start", weight=700 if diff else 400, color="#2E5A24" if diff else "#333")
        f.tick(cx_x, yy, a, 22)
        f.tick(cx_y, yy, b, 22)
        if diff:
            f.text(cx_x + 110, yy, "← وجه تمایز", 14, weight=700, color=GREEN)
    f.text(W / 2, f.h - 16, "تعداد یاخته‌های پشتیبان چند برابر نورون‌هاست؛ نورون‌ها سه عملکرد اصلی دارند: تولید، هدایت و انتقال پیام.", 14, color="#555")
    return f


# =================================================================== Q17
@chart(17)
def q17():
    f = Fig(W, 430, "ساخت غلاف میلین و پیامد آن")
    cx, cy = 230, f.top + 170
    # spiral wrapping (cross-section)
    f.circle(cx, cy, 38, "#E8EEF8", BLUE, 3)
    f.text(cx, cy, "آسه", 15, weight=700, color=BLUE)
    d = []
    for i in range(0, 4 * 360 + 1, 6):
        t = math.radians(i)
        r = 46 + i / 360 * 18
        d.append("%s%.1f,%.1f" % ("M" if i == 0 else "L", cx + r * math.cos(t), cy + r * math.sin(t)))
    f.path(" ".join(d), GOLD, 7)
    f.carrow("M%.1f,%.1f A125,125 0 0,1 %.1f,%.1f" % (cx + 125, cy, cx, cy + 125), RED, 3.5)
    f.text(cx + 120, cy + 110, "جهت پیچش", 15, weight=700, color=RED)
    f.text(cx, cy - 138, "برش عرضی: لایه‌های پیچیده‌شدهٔ یاختهٔ پشتیبان", 14, color="#555")
    # longitudinal view
    x0, x1, yl = 450, W - 40, f.top + 110
    f.line(x0, yl, x1, yl, BLUE, 8)
    segs = [(x0 + 20, x0 + 120), (x0 + 140, x0 + 240), (x0 + 260, x0 + 360)]
    for a, b in segs:
        f.rect(a, yl - 18, b - a, 36, "#FFE9A8", GOLD, 10, 2)
    for gx in (x0 + 130, x0 + 250):
        f.line(gx, yl - 42, gx, yl - 22, RED, 2)
        f.text(gx, yl - 54, "گره", 13, color=RED)
    f.text((x0 + x1) / 2, yl + 44, "غلاف میلین پیوسته نیست (گره‌های رانویه)", 14, color="#333")
    # speed chart along the fibre
    ys = yl + 150
    f.text((x0 + x1) / 2, ys - 52, "سرعت هدایت در طول رشته (طرح‌واره)", 14, weight=700, color="#1F3864")
    f.line(x0, ys, x1, ys, "#CCC", 1)
    pts = []
    for j in range(200):
        x = x0 + (x1 - x0) * j / 199
        inside = any(a <= x <= b for a, b in segs)
        pts.append((x, ys - (34 if inside else 8)))
    f.poly(pts, GREEN, 3)
    f.text((x0 + x1) / 2, ys + 26, "سرعت در طول رشته یکسان نیست ← گزینهٔ ۴", 15, weight=700, color=GREEN)
    f.text(W / 2, f.h - 14, "لایهٔ آخر غلاف ضخیم‌تر است و ضخامت آسه از غلاف میلین کمتر است.", 14, color="#555")
    return f


# =================================================================== Q18
@chart(18)
def q18():
    f = Fig(W, 470, "مادهٔ سفید و مادهٔ خاکستری در مغز و نخاع")
    y = f.top + 120
    # brain section: grey cortex outside, white inside
    f.ellipse(220, y, 150, 100, "#9E9E9E", "#666", 2)
    f.ellipse(220, y + 8, 122, 76, "#FAFAFA", "#BBB", 1.5)
    f.ellipse(220, y + 24, 34, 18, "#9E9E9E", "#777", 1)
    f.text(220, y - 118, "مغز (مخ): قشر خاکستری، داخل سفید و خاکستری", 14, weight=700, color="#333")
    # spinal cord: white outside, grey H inside
    cx = 650
    f.circle(cx, y, 95, "#FAFAFA", "#666", 2)
    f.path("M%d,%d C%d,%d %d,%d %d,%d C%d,%d %d,%d %d,%d C%d,%d %d,%d %d,%d C%d,%d %d,%d %d,%d z" % (
        cx - 12, y - 10, cx - 70, y - 90, cx - 75, y - 20, cx - 40, y,
        cx - 75, y + 20, cx - 70, y + 85, cx - 12, y + 10,
        cx + 70, y + 85, cx + 75, y + 20, cx + 40, y,
        cx + 75, y - 20, cx + 70, y - 90, cx - 12, y - 10), "#666", 1.5, "#9E9E9E")
    f.text(cx, y - 118, "نخاع: بخش خارجی سفید، داخل خاکستری", 14, weight=700, color="#333")
    rows = [("الف) نبودِ هسته", "✘ هستهٔ یاخته‌های پشتیبان در مادهٔ سفید هست"),
            ("ب) هدایت جهشی", "✔ فقط در رشته‌های میلین‌دار ← فقط مادهٔ سفید"),
            ("ج) نبودِ دارینهٔ کوتاه", "✘ در هیچ‌کدام از دو تعریف نیامده است"),
            ("د) بخش داخلی مغز", "✘ داخل مغز هر دو ماده دیده می‌شود")]
    y0 = y + 130
    for i, (a, b) in enumerate(rows):
        yy = y0 + i * 34
        ok = b.startswith("✔")
        f.text(W - 40, yy, a, 15, anchor="start", weight=700, color="#2E5A24" if ok else "#7A2A20")
        f.text(W - 250, yy, b, 14, anchor="start", color="#333")
    return f


# =================================================================== Q19
@chart(19)
def q19():
    f = Fig(W, 430, "مرکزی یا محیطی؟ (نمودار ون)")
    y = f.top + 170
    f.circle(560, y, 175, PAL["b"][0], BLUE, 2.5)
    f.circle(340, y, 175, PAL["y"][0], GOLD, 2.5)
    f.raw('<circle cx="560" cy="%d" r="175" fill="none" stroke="%s" stroke-width="2.5"/>' % (y, BLUE))
    f.text(640, y - 140, "دستگاه عصبی مرکزی", 18, weight=700, color="#1F3864")
    f.text(260, y - 140, "دستگاه عصبی محیطی", 18, weight=700, color="#6B5410")
    f.text(650, y - 60, "• مادهٔ سفید و خاکستری", 15)
    f.text(650, y - 20, "• تفسیر اطلاعات", 15)
    f.text(650, y + 20, "• پرده‌های مننژ", 15)
    f.text(650, y + 60, "• جمجمه (مغز)", 15)
    f.text(250, y - 20, "• ۱۲ جفت عصب مغزی", 15)
    f.text(250, y + 20, "• ۳۱ جفت عصب نخاعی", 15)
    f.text(450, y - 30, "حفاظت با", 15, weight=700, color=RED)
    f.text(450, y, "ستون مهره‌ها", 15, weight=700, color=RED)
    f.text(450, y + 40, "(نخاع + بخش‌هایی\nاز اعصاب نخاعی)", 13, color="#333")
    f.text(W / 2, f.h - 14, "نخاع فقط تا دومین مهرهٔ کمری ادامه دارد؛ پایین‌تر، اعصاب نخاعی درون ستون مهره‌ها هستند ← گزینهٔ ۱ نمی‌تواند تمایز ایجاد کند.", 13.5, color="#555")
    return f


# =================================================================== Q20
@chart(20)
def q20():
    f = Fig(W, 540, "لایه‌های حفاظتی مغز و نخاع (از خارج به داخل)")
    layers = [
        ("استخوان جمجمه / ستون مهره", "#D9D2C5", "#8C7B5A", ""),
        ("پردهٔ خارجی (ضخیم‌تر)", "#C9DAF0", BLUE, "فقط در شیارهای عمیق؛\nیک سطح آن با مایع در تماس"),
        ("مایع مغزی ـ نخاعی", "#E6F4FB", "#7FB3D5", "ضربه‌گیر؛ فقط بین پرده‌ها"),
        ("پردهٔ میانی (دارای زوائد)", "#F2D7A6", GOLD, "هر دو سطح با مایع در تماس؛\nفقط در شیارهای عمیق؛ با رگ‌ها در تماس"),
        ("مایع مغزی ـ نخاعی", "#E6F4FB", "#7FB3D5", ""),
        ("پردهٔ داخلی", "#F3C9C2", "#B5564A", "در همهٔ شیارها؛ با رگ‌ها در تماس؛\nتنها پرده در تماس با قشر مغز و نخاع"),
        ("قشر مخ (خاکستری) / بخش خارجی نخاع (سفید)", "#ECECEC", "#777", ""),
    ]
    y = f.top + 10
    x0, x1 = 420, W - 30
    hs = [50, 58, 44, 58, 44, 58, 56]
    later = []
    for (lab, fill, st, note), h in zip(layers, hs):
        f.rect(x0, y, x1 - x0, h - 4, fill, st, 8, 1.8)
        if "میانی" in lab:
            later.append(y + h - 4)
        f.text((x0 + x1) / 2, y + h / 2 - 2, lab, 16, weight=700, color="#222")
        if note:
            f.line(x0 - 6, y + h / 2 - 2, x0 - 22, y + h / 2 - 2, "#999", 1.5)
            f.text(x0 - 28, y + h / 2 - 2, note, 13.5, anchor="start", color="#333")
        y += h
    for yb in later:
        for xx in (x0 + 25, x0 + 70, x0 + 115, x1 - 115, x1 - 70, x1 - 25):
            f.path("M%d,%d C%d,%d %d,%d %d,%d" % (xx, yb, xx - 7, yb + 14, xx + 7, yb + 28, xx, yb + 42), GOLD, 3.5)
    f.text((x0 + x1) / 2, y + 22, "زوائد پردهٔ میانی از فضای مایع به سمت پردهٔ داخلی کشیده شده‌اند.", 13.5, color="#555")
    f.text(W / 2, f.h - 14, "فقط پردهٔ داخلی با مادهٔ سفید نخاع تماس دارد؛ پس گزینهٔ ۴ دربارهٔ پردهٔ میانی نادرست است.", 14.5, weight=700, color="#7A2A20")
    return f


# =================================================================== build
def build_charts(outdir):
    os.makedirs(outdir, exist_ok=True)
    man, out = [], {}
    for n in sorted(CH):
        for i, fn in enumerate(CH[n]):
            fig = fn()
            base = os.path.join(outdir, "q%02d_%d" % (n, i + 1))
            open(base + ".svg", "w", encoding="utf-8").write(fig.svg())
            man.append({"svg": base + ".svg", "png": base + ".png"})
            out.setdefault(n, []).append(base + ".png")
    json.dump(man, open(os.path.join(outdir, "manifest.json"), "w"))
    return out


if __name__ == "__main__":
    print(build_charts(sys.argv[1] if len(sys.argv) > 1 else "charts"))
