# Text helpers for editing paragraphs of a .docx (WordprocessingML) in place, keeping run formatting.
# Same machinery as build.py, packaged for reuse.
import copy, difflib, re
from lxml import etree

WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XNS = "http://www.w3.org/XML/1998/namespace"
FA = "؀-ۿ"
ZW = "‌"


def q(t):
    return "{%s}%s" % (WNS, t)


def items_of(p):
    out = []
    for r in p.iter(q("r")):
        for ch in r:
            if ch.tag == q("t"):
                out += [(c, r) for c in (ch.text or "")]
            elif ch.tag == q("tab"):
                out.append(("\t", r))
            elif ch.tag == q("br"):
                out.append(("⏎", r))
    return out


def text_of(p):
    return "".join(c for c, _ in items_of(p))


def fill_run(r, s):
    for ch in list(r):
        if ch.tag in (q("t"), q("tab"), q("br")):
            r.remove(ch)
    buf = ""

    def flush():
        nonlocal buf
        if buf:
            t = etree.SubElement(r, q("t"))
            t.text = buf
            t.set("{%s}space" % XNS, "preserve")
            buf = ""
    for c in s:
        if c == "\t":
            flush(); etree.SubElement(r, q("tab"))
        elif c == "⏎":
            flush(); etree.SubElement(r, q("br"))
        else:
            buf += c
    flush()


def ensure_rtl(r):
    s = "".join((t.text or "") for t in r.findall(q("t")))
    if not s or re.search("[A-Za-z]", s) and not re.search("[%s]" % FA, s):
        return
    rpr = r.find(q("rPr"))
    if rpr is None:
        rpr = etree.Element(q("rPr"))
        r.insert(0, rpr)
    if rpr.find(q("rtl")) is None:
        rtl = etree.Element(q("rtl"))
        after = [c for c in rpr if etree.QName(c).localname in ("cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath")]
        if after:
            after[0].addprevious(rtl)
        else:
            rpr.append(rtl)


def retext(p, new):
    """replace the text of paragraph p with `new`, mapping characters onto the existing runs"""
    items = items_of(p)
    old = "".join(c for c, _ in items)
    if old == new:
        return False
    runs = [r for r in p.iter(q("r"))]
    if not items:
        r = runs[0] if runs else etree.SubElement(p, q("r"))
        fill_run(r, new); ensure_rtl(r)
        return True
    assign = []
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            assign += [(new[j], items[i1 + j - j1][1]) for j in range(j1, j2)]
        elif tag == "replace":
            assign += [(new[j], items[i1][1]) for j in range(j1, j2)]
        elif tag == "insert":
            r = items[i1 - 1][1] if i1 > 0 else items[i1][1]
            assign += [(new[j], r) for j in range(j1, j2)]
    per = {}
    for c, r in assign:
        per[id(r)] = per.get(id(r), "") + c
    for r in runs:
        if id(r) in per:
            fill_run(r, per[id(r)]); ensure_rtl(r)
        else:
            had_text = any(ch.tag in (q("t"), q("tab"), q("br")) for ch in r)
            others = [ch for ch in r if ch.tag not in (q("rPr"), q("t"), q("tab"), q("br"), q("lastRenderedPageBreak"))]
            if had_text and not others:
                r.getparent().remove(r)
            elif had_text:
                fill_run(r, "")
    assert text_of(p) == new, (text_of(p), new)
    return True


WORDS = {
    "سوال": "سؤال", "تاثیر": "تأثیر", "موثر": "مؤثر", "آنها": "آن‌ها", "مننز": "مننژ",
    "چند لایه": "چندلایه", "تک لایه": "تک‌لایه", "بنابر این": "بنابراین",
    "کوچکتر": "کوچک‌تر", "بزرگتر": "بزرگ‌تر", "نزدیکتر": "نزدیک‌تر", "پایینتر": "پایین‌تر", "پایین تر": "پایین‌تر",
    "باقیمانده": "باقی‌مانده", "غیر زنده": "غیرزنده", "تشکیل دهند": "تشکیل‌دهند",
    "تولید مثل": "تولیدمثل", "غیر یکسان": "غیریکسان", "بین یاخته‌ای": "بین‌یاخته‌ای",
    "دریچه دار": "دریچه‌دار", "دریچهدار": "دریچه‌دار", "میلین دار": "میلین‌دار", "نفوذ پذیری": "نفوذپذیری",
    "پیش سیناپسی": "پیش‌سیناپسی", "پس سیناپسی": "پس‌سیناپسی",
    "به طور": "به‌طور", "به‌طورحتم": "به‌طور حتم", "سدیم-پتاسیم": "سدیم ـ پتاسیم",
    "زیست شناسی": "زیست‌شناسی", "هم ایستایی": "هم‌ایستایی", "عایق بندی": "عایق‌بندی",
    "پایین رو": "پایین‌رو", "بالا رو": "بالارو", "پروتیین": "پروتئین",
}
MI = "کن|شو|گیر|توان|گوی|ده|خوا|دانیم|دانید|داند|بین|رس|ریز|آی|گه|شه|مان|ساز|پوش|باش|رو|گرد|پیوند|پیما|گذ|بر|آور|خور|یاب"


def norm(s):
    s = s.replace("ي", "ی").replace("ك", "ک").replace("ۀ", "هٔ").replace("ة", "هٔ")
    s = s.replace(" ", " ")
    for a, b in WORDS.items():
        s = s.replace(a, b)
    s = re.sub(r"(?<!وی)تامین", "تأمین", s)
    s = re.sub(r"(?<![%s%s])(ن?می)(?=(%s))" % (FA, ZW, MI), r"\1" + ZW, s)
    s = re.sub(r"(?<![%s%s])(ن?می) (?=[%s])" % (FA, ZW, FA), r"\1" + ZW, s)
    s = re.sub(r"(?<=[ادذرزژو]) (ها|های|هایی)(?![%s%s])" % (FA, ZW), r"\1", s)
    s = re.sub(r"(?<=[%s]) (ها|های|هایی)(?![%s%s])" % (FA, FA, ZW), ZW + r"\1", s)
    s = re.sub(r"(?<=[%s]) اند(?![%s%s])" % (FA, FA, ZW), ZW + "اند", s)
    s = re.sub(r"(?<=ه) ای(?![%s%s])" % (FA, ZW), ZW + "ای", s)
    s = re.sub(r" {2,}", " ", s)
    s = re.sub(r" *\t *", "\t", s)
    s = re.sub(r"(?<=[%s%s»\)A-Za-z0-9]) +(?=[،؛؟:!])" % (FA, ZW), "", s)
    s = re.sub(r"(?<=[%s%s»\)A-Za-z0-9]) +\.(?!\.)" % (FA, ZW), ".", s)
    s = re.sub(r"([،؛])(?=[%sA-Za-z«])" % FA, r"\1 ", s)
    s = re.sub(r":(?=[%sA-Za-z«])" % FA, ": ", s)
    s = re.sub(r"\( +", "(", s)
    s = re.sub(r" +\)", ")", s)
    s = re.sub(ZW + "{2,}", ZW, s)
    s = re.sub(r"%s(?=[ \t،؛:.؟!»\)]|$)" % ZW, "", s)
    s = re.sub(r"(?<=[ \t«\(])%s" % ZW, "", s)
    s = re.sub(r"^%s" % ZW, "", s)
    return s.strip(" ")


# ------------------------------------------------------------------ paragraph direction
PPR_AFTER_BIDI = ("adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
                  "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl",
                  "divId", "cnfStyle", "rPr", "sectPr", "pPrChange")
PPR_BEFORE_JC = PPR_AFTER_BIDI[PPR_AFTER_BIDI.index("jc") + 1:]


def _insert_ppr(ppr, el, before_names):
    nxt = [c for c in ppr if etree.QName(c).localname in before_names]
    if nxt:
        nxt[0].addprevious(el)
    else:
        ppr.append(el)


def make_rtl(p, justify=False):
    """give a Persian paragraph RTL direction (w:bidi); optionally justify it"""
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = etree.Element(q("pPr"))
        p.insert(0, ppr)
    changed = False
    if ppr.find(q("bidi")) is None:
        _insert_ppr(ppr, etree.Element(q("bidi")), PPR_AFTER_BIDI)
        changed = True
        jc = ppr.find(q("jc"))
        # in an RTL paragraph "right" means "end" (= visually left); the text was meant to start at the right
        if jc is not None and jc.get(q("val")) == "right":
            jc.set(q("val"), "both" if justify else "left")
    if justify:
        jc = ppr.find(q("jc"))
        if jc is None:
            jc = etree.Element(q("jc"))
            _insert_ppr(ppr, jc, PPR_BEFORE_JC)
        if jc.get(q("val")) in (None, "right", "left", "start"):
            jc.set(q("val"), "both")
    return changed
