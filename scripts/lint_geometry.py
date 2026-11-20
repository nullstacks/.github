
"""Geometry linter: measures every <text> run with real fonts and fails on
clipping or collision, at the card's authored scale."""
import glob, os, sys
from xml.etree import ElementTree as ET
from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = {"sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"}
# fall back to any TTF we have; metrics only need to be close
CAND = ["/tmp/nsf/Geist-Regular.ttf", F["sans"]]
for c in CAND:
    if os.path.exists(c):
        FONT = c
        break
FONTS = {"sans": FONT, "mono": FONT, "bold": FONT}
_cache = {}

def measure(s, size, kind):
    key = (kind, round(size,1))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONTS[kind], max(1, int(size*8)))
    return _cache[key].getlength(s)/8.0

def check(path):
    root = ET.fromstring(open(path, encoding="utf-8").read())
    W = float(root.get("width")); H = float(root.get("height"))
    probs = []; runs = []
    for t in root.iter("{http://www.w3.org/2000/svg}text"):
        if t.get("data-cu"):
            continue   # timed count-up frames: only one is ever visible
        s = "".join(t.itertext())
        if not s.strip():
            continue
        size = float(t.get("font-size", 12))
        x = float(t.get("x", 0)); y = float(t.get("y", 0))
        anchor = t.get("text-anchor", "start")
        cls = t.get("class") or ""
        kind = "mono" if "mono" in cls else "sans"
        w = measure(s, size, kind)
        x1 = x - w/2 if anchor == "middle" else (x - w if anchor == "end" else x)
        runs.append((s, x1, x1+w, y-size*0.74, y+size*0.24, size))
        if x1 < -0.5 or x1+w > W+0.5:
            probs.append("CLIP-H %-34r x=[%.0f,%.0f] W=%.0f" % (s[:34], x1, x1+w, W))
        if y - size > H or y > H:
            probs.append("CLIP-V %-34r y=%.0f H=%.0f" % (s[:34], y, H))
    for i in range(len(runs)):
        for j in range(i+1, len(runs)):
            a, b = runs[i], runs[j]
            ox = min(a[2], b[2]) - max(a[1], b[1])
            oy = min(a[4], b[4]) - max(a[3], b[3])
            if ox > 1.5 and oy > 1.5:
                probs.append("OVERLAP %r <-> %r (%.0fx%.0f)" % (a[0][:22], b[0][:22], ox, oy))
    return probs

def main():
    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "profile", "cards", "*.svg"))):
        p = check(f)
        if p:
            total += len(p)
            print("==", os.path.basename(f))
            for x in p: print("   ", x)
    print("\n%d problem(s)" % total)
    return 1 if total else 0

if __name__ == "__main__":
    sys.exit(main())
