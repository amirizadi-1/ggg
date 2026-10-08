# Applies text fixes and inserts the three added blocks per question, then writes the .docx.
import copy, difflib, re, sys, zipfile, os
from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsl
from fixes import TXT, Q21_STEM, Q21_OPTS, Q31_ANSWER, DELETE
from content import Q

SRC_DIR, OUT = sys.argv[1], sys.argv[2]
LOG = sys.argv[3] if len(sys.argv) > 3 else None
WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XNS = "http://www.w3.org/XML/1998/namespace"


def q(t):
    return "{%s}%s" % (WNS, t)


doc_path = os.path.join(SRC_DIR, "word", "document.xml")
tree = etree.parse(doc_path)
root = tree.getroot()
body = root.find(q("body"))
orig = list(body)
NSDECL = " ".join('xmlns:%s="%s"' % (k, v) for k, v in root.nsmap.items() if k)

FA = "؀-ۿ"
ZW = "‌"


def E(xml):
    return etree.fromstring("<x %s>%s</x>" % (NSDECL, xml))[0]


def EL(xml):
    return list(etree.fromstring("<x %s>%s</x>" % (NSDECL, xml)))


# ------------------------------------------------------------------ text helpers
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
        # schema order: rtl comes after sz/szCs/u/... and before cs/em/lang
        after = [c for c in rpr if etree.QName(c).localname in ("cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath")]
        if after:
            after[0].addprevious(rtl)
        else:
            rpr.append(rtl)


def retext(p, new):
    items = items_of(p)
    old = "".join(c for c, _ in items)
    if old == new:
        return False
    runs = [r for r in p.iter(q("r"))]
    m = re.match(r"^(Bio[A-Za-z]+)(: .*)$", new, flags=re.S)
    if m and runs:
        # label in an LTR run, the rest in one RTL run (keeps the colon on the correct side)
        base = max(runs, key=lambda r: sum(len(t.text or "") for t in r.findall(q("t"))))
        base_rpr = base.find(q("rPr"))
        for r in runs:
            r.getparent().remove(r)
        r1 = etree.SubElement(p, q("r"))
        r2 = etree.SubElement(p, q("r"))
        if base_rpr is not None:
            a = copy.deepcopy(base_rpr)
            for x in a.findall(q("rtl")):
                a.remove(x)
            r1.append(a)
            r2.append(copy.deepcopy(base_rpr))
        fill_run(r1, m.group(1)); fill_run(r2, m.group(2))
        ensure_rtl(r2)
        return True
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
    order = []
    for c, r in assign:
        if id(r) not in per:
            per[id(r)] = ""
            order.append(r)
        per[id(r)] += c
    for r in runs:
        if id(r) in per:
            fill_run(r, per[id(r)]); ensure_rtl(r)
        else:
            had_text = any(ch.tag in (q("t"), q("tab"), q("br")) for ch in r)
            others = [ch for ch in r if ch.tag not in (q("rPr"), q("t"), q("tab"), q("br"))]
            if had_text and not others:
                r.getparent().remove(r)
            elif had_text:
                fill_run(r, "")
    assert text_of(p) == new, (text_of(p), new)
    return True


WORDS = {
    "سوال": "سؤال", "تاثیر": "تأثیر", "موثر": "مؤثر", "آنها": "آن‌ها",
    "سنگفرشی": "سنگ‌فرشی", "چند لایه": "چندلایه", "تک لایه": "تک‌لایه", "بنابر این": "بنابراین",
    "کوچکتر": "کوچک‌تر", "بزرگتر": "بزرگ‌تر", "پایینتر": "پایین‌تر", "پایین تر": "پایین‌تر",
    "فراوانتر": "فراوان‌تر", "باقیمانده": "باقی‌مانده", "بوم سازگان": "بوم‌سازگان",
    "زیست بوم": "زیست‌بوم", "غیر زنده": "غیرزنده", "تشکیل دهند": "تشکیل‌دهند",
    "ترشح کنند": "ترشح‌کنند", "تجزیه کنند": "تجزیه‌کنند", "مخلوط کنند": "مخلوط‌کنند",
    "بین رشته": "بین‌رشته", "شگفت انگیز": "شگفت‌انگیز", "کم تعداد": "کم‌تعداد",
    "تولید مثل": "تولیدمثل", "ای شکل": "ای‌شکل", "نارنجی رنگ": "نارنجی‌رنگ", "برعهده": "بر عهده", "غیر یکسان": "غیریکسان", " ـ ": " – ", " - ": " – ", "مکعبی شکل": "مکعبی‌شکل", "بین یاخته‌ای": "بین‌یاخته‌ای", "موادمغذی": "مواد مغذی", "دوکی شکل": "دوکی‌شکل",
    "انگشتری شکل": "انگشتری‌شکل", "چین خورده": "چین‌خورده", "آسیب دیده": "آسیب‌دیده",
    "اتصال دهند": "اتصال‌دهند",
}
MI = "کن|شو|گیر|توان|گوی|ده|خوا|دانیم|دانید|داند|بین|رس|ریز|آی|گه|شه|مان|ساز|پوش|باش|رو|گرد|پیوند|پیما|گذ|بر|آور|خور|یاب"


def norm(s):
    s = s.replace("ي", "ی").replace("ك", "ک").replace("ۀ", "هٔ").replace("ة", "هٔ")
    s = s.replace(" ", " ")
    for a, b in WORDS.items():
        s = s.replace(a, b)
    s = re.sub(r"(?<!وی)تامین", "تأمین", s)
    s = re.sub(r"دوبار(?![%s])" % FA, "دو بار", s)
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


# ------------------------------------------------------------------ addressing
def cell_paras(tbl_idx):
    tc = orig[tbl_idx].findall(".//" + q("tc"))[0]
    return tc, tc.findall(q("p"))


TP = {}
for ti in (288, 341):
    TP[ti] = cell_paras(ti)


def get(key):
    if key.startswith("T"):
        t, k = key[1:].split(":")
        return TP[int(t)][1][int(k)]
    return orig[int(key)]


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
    p.getparent().remove(p)

# Q21: rebuild stem + options with the layout of Q22
stem21 = copy.deepcopy(orig[12]); retext(stem21, Q21_STEM)
orig[0].addprevious(stem21)
for t in Q21_OPTS:
    o = copy.deepcopy(orig[14]); retext(o, t)
    orig[0].addprevious(o)
for i in (0, 1, 2):
    body.remove(orig[i])
explicit.add(id(stem21))

# Q31: missing answer line
ans31 = copy.deepcopy(orig[211]); retext(ans31, Q31_ANSWER)
orig[188].addprevious(ans31)

# global rules on every paragraph
for p in body.iter(q("p")):
    old = text_of(p)
    new = norm(old)
    if new != old:
        retext(p, new)
        if id(p) not in explicit:
            log.append("[auto]\n  - %s\n  + %s" % (old, new))
    for r in p.iter(q("r")):
        ensure_rtl(r)


def is_empty(p):
    if text_of(p).strip(" ‌"):
        return False
    for tag in ("drawing", "pict", "object", "sectPr"):
        if p.find(".//" + q(tag)) is not None:
            return False
    return True


# Q37 / Q41: move the answer paragraphs out of the question table
moved = {}
for ti in (288, 341):
    tc, ps = TP[ti]
    anchor = orig[ti]
    moved[ti] = []
    for p in ps[4:]:
        tc.remove(p)
        if is_empty(p):
            continue
        anchor.addnext(p)
        anchor = p
        moved[ti].append(p)

# drop empty body-level paragraphs
for p in list(body):
    if p.tag == q("p") and is_empty(p):
        body.remove(p)

# ------------------------------------------------------------------ added blocks
def heading(text):
    return E('<w:p><w:pPr><w:pStyle w:val="a6"/><w:keepNext/><w:spacing w:before="120" w:after="60"/></w:pPr>'
             '<w:r><w:rPr><w:rtl/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % text)


def spacer(h=120):
    return E('<w:p><w:pPr><w:bidi/><w:spacing w:before="0" w:after="0" w:line="%d" w:lineRule="exact"/>'
             '<w:rPr><w:sz w:val="8"/><w:szCs w:val="8"/></w:rPr></w:pPr></w:p>' % h)


def blank():
    return E('<w:p><w:pPr><w:bidi/><w:spacing w:before="0" w:after="0"/></w:pPr></w:p>')


def banner(title):
    return E(dsl.para([dsl.run("جدول و نمودار تکمیلی", b=True, sz=20, color="FFD966"),
                       dsl.run("   |   ", sz=20, color="FFFFFF"),
                       dsl.run(title, b=True, sz=24, color="FFFFFF")],
                      keep=True, before=240, after=60, shd="1F3864", line=300))


def note(text, center=False, before=60):
    return E(dsl.para([dsl.run(text, sz=20, color="444444")], jc="center" if center else "both",
                      before=before, after=40, line=264))


def insert_after(anchor, els):
    for e in els:
        anchor.addnext(e)
        anchor = e
    return anchor


ANCH = {
    21: ("3", "8"), 22: ("18", "25"), 23: ("36", "46"), 24: ("53", "61"), 25: ("69", "76"),
    26: ("84", "95"), 27: ("102", "113"), 28: ("119", "127"), 29: ("146", "167"), 30: ("176", "182"),
    31: (None, "198"), 32: ("211", "219"), 33: ("225", "234"), 34: ("242", "251"), 35: ("259", "266"),
    36: ("273", "284"), 37: ("T288:4", "T288:16"), 38: ("295", "303"), 39: ("310", "320"),
    40: ("329", "337"), 41: ("T341:4", "T341:14"), 42: ("348", "357"), 43: ("366", "377"),
    44: ("383", "392"), 45: ("398", "408"),
}
STEMS = [12, 28, 48, 64, 79, 97, 114, 129, 171, 183, 205, 220, 236, 254, 268, 287, 290, 305, 324, 340,
         343, 359, 378, 393]

for n, (a, e) in ANCH.items():
    c = Q[n]
    ans = ans31 if a is None else get(a)
    end = get(e)
    assert ans.getparent() is body and end.getparent() is body, n
    # block at the end of the answer
    els = [banner(c["title"]), heading("جدول جمع‌بندی"),
           E(dsl.summary_table(c["sum_head"], c["sum_rows"], c.get("sum_ratio")))]
    if c.get("sum_note"):
        els.append(note(c["sum_note"]))
    els.append(heading("نمودار / فلوچارت"))
    for cap, xml, nt in c["diag"]:
        if cap:
            els.append(E(dsl.para([dsl.run(cap, b=True, sz=20, color="2F5D9B")], jc="center",
                                  keep=True, before=80, after=50)))
        els.append(E(xml))
        els.append(note(nt, center=True, before=40) if nt else spacer())
    els.append(E(dsl.para([dsl.run("منبع: ", b=True, sz=18, color="555555"),
                           dsl.run(c["src"], sz=18, color="555555")], before=80, after=0)))
    insert_after(end, els)
    # option review right after the answer line
    els = [heading("بررسی گزینه‌ها" if "opts_head" not in c or c["opts_head"][0] == "گزینه" else "بررسی موارد"),
           E(dsl.options_table(c["opts"], c.get("opts_head", ("گزینه", "ادعای گزینه", "داوری"))))]
    if c.get("count"):
        els.append(E(dsl.para([dsl.run(c["count"], b=True, sz=22, color="2E7D32")], before=60, after=0)))
    els.append(spacer(160))
    insert_after(ans, els)

# one blank line before every question stem (except the first)
for i in STEMS:
    orig[i].addprevious(blank())

tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)

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
print("ok", OUT, "changes:", len(log))
