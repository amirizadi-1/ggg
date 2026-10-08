# Draws the diagrams of content.py (questions 21–45 of «سند ۵۰») as chart images.
# usage: python3 style/diag50.py <out dir>   → q21_1.svg … + manifest.json (render with render_charts.js)
import importlib, json, os, sys, types
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import dsl as real_dsl
import svgfig
import svgdiag

svgfig.BG = "#E7F2FE"           # same chart background as Faraz11_Styled-2

fake = types.ModuleType("dsl")
fake.R = real_dsl.R
for name in ("VF", "HF", "TR", "MG", "PAR", "STK"):
    setattr(fake, name, getattr(svgdiag, name))
sys.modules["dsl"] = fake
content = importlib.import_module("content")

out = sys.argv[1] if len(sys.argv) > 1 else "charts50"
os.makedirs(out, exist_ok=True)
man = []
for n in sorted(content.Q):
    for i, (cap, d, foot) in enumerate(content.Q[n]["diag"], 1):
        base = os.path.join(out, "q%02d_%d" % (n, i))
        open(base + ".svg", "w", encoding="utf-8").write(d.fig(cap, foot).svg())
        man.append({"svg": base + ".svg", "png": base + ".png"})
json.dump(man, open(os.path.join(out, "manifest.json"), "w"))
print(len(man), "diagrams")
