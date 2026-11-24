#!/usr/bin/env python3
"""Render the pixel-themed animated SVG cards for the nullstacks org profile README.

Run from the repo root:    python scripts/render_cards.py
Writes:                    profile/cards/*.svg  and  profile/README.md
STATIC=1 python ...        renders final frames (no animation) for screenshots.

RESPONSIVE LAYOUT (why this file is built the way it is)
  GitHub gives a README no media queries and no CSS, only HTML. Two things make it adapt anyway:

  1. NO width attribute on any <img>. Each image renders at its SVG's own size, clamped to the
     column by GitHub's max-width:100% (height stays proportional). So:
        wide cards  (hero, category banners, headings, divider)  880 wide -> scale down smoothly
        repo cards  200 wide (192 drawn + 8px gutter)            -> four fit a ~830px column and
                    the row simply re-flows to 3 / 2 per line as the column narrows.
     (Percent widths, used before, shrink the text with the column: ~4px type on a phone.)

  2. <picture><source media="(max-width: 600px)" srcset="NAME-m.svg"> swaps in a variant that is
     REDRAWN for phones at MW = 320px wide (about the width of a phone README column), so type
     renders ~1:1. Repo cards become full-width list rows, banners/hero/headings are re-laid out.

Everything works inside <img> on GitHub: inline <style>, CSS keyframes, prefers-color-scheme and
prefers-reduced-motion. No scripts, no external requests, no web fonts (the pixel lettering is
drawn from rects, so it needs no font file).
"""
import html
import math
import os
import textwrap

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CARDS = os.path.join(ROOT, "profile", "cards")
STATIC = os.environ.get("STATIC") == "1"

WIDE, MW, SHADOW, GUT = 880, 320, 4, 8   # wide card, mobile card, shadow offset, gutter between cards
D_W, D_H = 192, 92                       # desktop repo card as drawn (svg is D_W+GUT x D_H+GUT = 200 x 100)
M_H = 88                                 # mobile repo card as drawn height (svg is MW x M_H+GUT)
RAW = "https://raw.githubusercontent.com/nullstacks/.github/main/profile/cards"

SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"

# ---- content (from the READMEs of the public repos) ---------------------------------
CATS = {
    "gateways": dict(label="MODEL GATEWAYS", color="blue", desc="Free AI models as drop-in, OpenAI-style APIs."),
    "services": dict(label="APIS & SERVICES", color="red", desc="Small hosted APIs and services on Cloudflare Workers."),
    "extensions": dict(label="BROWSER EXTENSIONS", color="amber", desc="Browser extensions for everyday chores."),
    "apps": dict(label="WEB APPS & TOOLS", color="teal", desc="Apps, toolkits and utilities for everyday work."),
}

# slug, category, description (2 lines max at 212px), language, live demo URL or None
#
# The demo URL is the single source of truth for "is this live": a card shows the
# live badge iff it has a URL here, and the "Try them live" list is generated from
# the same field. Keeping a separate live-flag plus a separate URL list is what let
# two dead links drift out of sync with the cards.
REPOS = [
    ("kilo-gateway", "gateways", "Kilo's free models, keyless, as an OpenAI/Anthropic API.", "Python", None),
    ("opencode-gateway", "gateways", "OpenCode models and free tier in any harness. No key.", "Python", None),
    ("cline2api", "gateways", "Cline's free models as an API. Catalog auto-refreshes.", "Python", None),
    ("qoder2api", "gateways", "Qoder (intl) as a self-hosted OpenAI-compatible API.", "Python", None),
    ("mailapi", "services", "Your Gmail as a REST API. One key, many accounts.", "JavaScript",
     "https://mailapi.nullstacks.workers.dev"),
    ("heardlist", "services", "Free proxy-list API. Hourly refresh, JSON/TXT/CSV.", "JavaScript",
     "https://heardlist.nullstacks.workers.dev"),
    ("tack", "services", "Paste a page, get a rendered link and a raw link.", "HTML",
     "https://tack.nullstacks.workers.dev"),
    ("temp-mail-extension", "extensions", "Disposable inbox for Chrome & Brave. Autofill, OTP copy.", "JavaScript", None),
    ("cookie-manager", "extensions", "Cookie editor for Chrome & Brave. JSON/cookies.txt export.", "JavaScript", None),
    ("google-forms-copilot", "extensions", "AI filler for Google Forms. You review every answer.", "JavaScript", None),
    ("papersnap", "apps", "Local PDF and image toolkit. 30 tools, no uploads.", "TypeScript",
     "https://papersnap.nullstacks.workers.dev"),
    ("curl-toolkit", "apps", "cURL to 18 languages plus an in-browser API client.", "TypeScript",
     "https://nullstacks.github.io/curl-toolkit/"),
    ("jee", "apps", "JEE Main 2027: PYQ chapters, rank predictor, JoSAA.", "TypeScript",
     "https://jee.nullstacks.workers.dev"),
    ("mai-image", "apps", "Free image gen via Bing Image Creator. Skill + CLI.", "Python", None),
]

# Display names for the live-links line. The old pushkarsingh4343.workers.dev
# subdomain is NXDOMAIN; every Worker now lives under nullstacks.workers.dev.
LIVE_LABELS = {"curl-toolkit": "cURL Toolkit"}

# ---- 5x7 bitmap font (drawn from rects, so no font file is needed) ------------------
FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000", "-": "00000 00000 00000 11111 00000 00000 00000",
    "_": "00000 00000 00000 00000 00000 00000 11111", "&": "01100 10010 10100 01000 10101 10010 01101",
}

# 8x8 sprites for the category tiles
SPRITES = {
    "gateways": ["00111100", "01000010", "10000001", "10011001", "10011001", "10000001", "10000001", "11111111"],
    "services": ["11111111", "10100001", "11111111", "00011000", "11111111", "10100001", "11111111", "00000000"],
    "extensions": ["00100100", "00100100", "01111110", "01111110", "01111110", "00111100", "00011000", "00011000"],
    "apps": ["11111111", "10101011", "11111111", "10000001", "10111101", "10100101", "10111101", "11111111"],
}

CSS = """
:root{--bg:#fbfaf6;--card:#ffffff;--ink:#17171a;--mute:#6b6b73;--line:#d9d5c8;
--blue:#2f6fed;--red:#e5484d;--amber:#c98100;--teal:#12a37f}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--card:#12171e;--ink:#ecebe6;--mute:#8b949e;--line:#2b323d;
--blue:#6ea0ff;--red:#ff7b7f;--amber:#f5b942;--teal:#3ddbb0}}
path,rect,line{shape-rendering:crispEdges}
text{font-family:%(sans)s;fill:var(--ink)}
.serif{font-family:%(serif)s}.mono{font-family:%(mono)s}.mute{fill:var(--mute)}
.ink{fill:var(--ink)}
.rise{animation:rise .7s cubic-bezier(.2,.8,.2,1) var(--d,0s) backwards}
.pop{transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,1.4,.4,1) var(--d,0s) backwards}
.tick{opacity:0;animation:tick .13s linear var(--d,0s) both}
.final{animation:fade .3s ease-out var(--d,0s) backwards}
.blink{animation:blink 1.1s steps(1) infinite}
.pulse{animation:pulse 2s steps(2) infinite}
.twinkle{animation:twinkle 3s steps(1) var(--d,0s) infinite}
.march{animation:march 1s steps(2) infinite}
.title{animation:flick .7s steps(1) var(--d,0s) backwards,glint 6s linear var(--g,0s) infinite}
.orbit{opacity:.4;transform-box:fill-box;transform-origin:center;animation:orbit 3.6s linear var(--d,0s) infinite}
.zip{opacity:.4;transform-box:fill-box;transform-origin:center;animation:zip 4.2s linear var(--d,0s) infinite}
.wave{opacity:.35;animation:wave 3.2s linear var(--d,0s) infinite}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes fade{from{opacity:0}}
@keyframes tick{0%%,99%%{opacity:1}100%%{opacity:0}}
@keyframes blink{50%%{opacity:0}}
@keyframes pulse{50%%{opacity:.3}}
@keyframes twinkle{0%%,100%%{opacity:.15}50%%{opacity:.9}}
@keyframes march{to{stroke-dashoffset:-8}}
@keyframes flick{0%%{opacity:0}20%%{opacity:1}35%%{opacity:0}55%%{opacity:1}70%%{opacity:0}100%%{opacity:1}}
@keyframes glint{0%%{fill:var(--blue)}9%%{fill:var(--ink)}100%%{fill:var(--ink)}}
@keyframes orbit{0%%{opacity:1;transform:scale(1.18)}22%%{opacity:.4;transform:scale(1)}100%%{opacity:.4}}
@keyframes zip{0%%{opacity:1;transform:scale(1.3)}14%%{opacity:.4;transform:scale(1)}100%%{opacity:.4}}
@keyframes wave{0%%{opacity:1}20%%{opacity:.35}100%%{opacity:.35}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.tick{opacity:0}.orbit,.zip,.wave{opacity:1}}
""" % dict(sans=SANS, serif=SERIF, mono=MONO)

if STATIC:
    CSS += "*{animation:none!important}.tick{opacity:0}.orbit,.zip,.wave{opacity:1}"


# ---- helpers ------------------------------------------------------------------------
def esc(s):
    return html.escape(s, quote=False)


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>'
        f"<style>{CSS}</style>{body}</svg>"
    )


def write(name, content):
    os.makedirs(CARDS, exist_ok=True)
    # newline="\n" so Windows does not write CRLF into the committed SVGs
    with open(os.path.join(CARDS, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print(f"wrote {name:28s} {len(content):6d} bytes")


def pixbox(x, y, w, h, n=4):
    """Rectangle with single-pixel stepped corners (retro 'rounded' look)."""
    return (f"M{x+n} {y}H{x+w-n}V{y+n}H{x+w}V{y+h-n}H{x+w-n}V{y+h}H{x+n}V{y+h-n}H{x}V{y+n}H{x+n}Z")


def frame(w, h, accent):
    """Card body (w-SHADOW x h-SHADOW) with a hard, offset accent shadow."""
    bw, bh = w - SHADOW, h - SHADOW
    return (
        f'<path d="{pixbox(SHADOW, SHADOW, bw, bh)}" style="fill:var(--{accent});opacity:.28"/>'
        f'<path d="{pixbox(1, 1, bw - 2, bh - 2)}" fill="var(--card)" stroke="var(--line)" stroke-width="2"/>'
    )


# Thickening M / N / W by a pixel fills their inner gaps solid (M reads as H), so they get 7-wide shapes.
BOLD = {
    "M": "1100011 1110111 1101011 1101011 1100011 1100011 1100011",
    "N": "1100011 1110011 1101011 1100111 1100011 1100011 1100011",
    "W": "1100011 1100011 1100011 1101011 1101011 1110111 1100011",
}


def glyph_d(ch, x, y, cell, pitch, bold=False):
    rows = (BOLD[ch] if bold and ch in BOLD else FONT[ch]).split()
    lit = set()
    for r, row in enumerate(rows):
        for c, bit in enumerate(row):
            if bit == "1":
                lit.add((r, c))
                if bold and ch not in BOLD:  # thicken every stroke by one pixel to the right
                    lit.add((r, c + 1))
    return "".join(f"M{x + c * pitch} {y + r * pitch}h{cell}v{cell}h-{cell}z" for r, c in sorted(lit))


def text_width(text, cell, gap, bold=False):
    pitch = cell + gap
    cols = 7 if bold else 6  # glyph columns (5, or 6 when bold) plus one spacing column
    return len(text) * cols * pitch - pitch


def pixel_text(text, x, y, cell, gap, attrs="", per_letter=None, bold=False):
    """One <path> per letter. per_letter(i) returns extra attributes for that letter."""
    pitch = cell + gap
    adv = (7 if bold else 6) * pitch
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        extra = per_letter(i) if per_letter else ""
        out.append(f'<path {attrs} {extra} d="{glyph_d(ch, x + i * adv, y, cell, pitch, bold)}"/>')
    return "".join(out)


def sprite(rows, x, y, cell, col, d0):
    d = []
    for r, row in enumerate(rows):
        for c, bit in enumerate(row):
            if bit == "1":
                d.append(f"M{x + c * cell} {y + r * cell}h{cell}v{cell}h-{cell}z")
    return f'<path class="pop" style="--d:{d0:.2f}s;fill:var(--{col})" d="{"".join(d)}"/>'


def chip(x, y, label, size=10):
    w = round(len(label) * 0.6 * size + 14)
    return w, (
        f'<rect x="{x}" y="{y}" width="{w}" height="20" fill="none" stroke="var(--line)" stroke-width="2"/>'
        f'<text class="mono mute" x="{x + 7}" y="{y + 14}" font-size="{size}">{esc(label)}</text>'
    )


def wrap_balanced(text, limit):
    """Wrap to the fewest lines `limit` allows, then even the lines out (no one-word orphans).
    Never breaks a word at its hyphen ("OpenAI-/style")."""
    n = len(textwrap.wrap(text, limit, break_on_hyphens=False))
    w = max(1, -(-len(text) // n))
    while len(textwrap.wrap(text, w, break_on_hyphens=False)) > n:
        w += 1
    lines = textwrap.wrap(text, w, break_on_hyphens=False)
    assert len(lines) <= 2, f"description needs {len(lines)} lines: {text!r}"
    return lines


# ---- small shared pieces --------------------------------------------------------------------
ARROW = ["00111", "00011", "00101", "01000", "10000"]  # north-east arrow, 5x5
MAIL = ["11111111", "11000011", "10100101", "10011001", "10000001", "10000001", "11111111", "00000000"]
BOOK = ["01111110", "01000010", "01011110", "01000010", "01011110", "01000010", "01111110", "00000000"]

STATS = [  # derived from REPOS so the hero can never drift out of sync with the cards
    (f"{len(REPOS)} REPOS", "blue"),
    (f"{sum(1 for r in REPOS if r[4])} LIVE", "teal"),
    (f"{len(CATS)} CATEGORIES", "amber"),
    ("OPEN SOURCE", "red"),
]


def chip2(x, y, label, col, size=10, delay=0.0):
    """Outlined stat chip with a coloured pixel marker."""
    w = round(len(label) * 0.6 * size + 26)
    return w, (
        f'<g class="rise" style="--d:{delay:.2f}s">'
        f'<rect x="{x}" y="{y}" width="{w}" height="20" fill="none" stroke="var(--line)" stroke-width="2"/>'
        f'<rect x="{x + 8}" y="{y + 8}" width="4" height="4" style="fill:var(--{col})"/>'
        f'<text class="mono mute" x="{x + 18}" y="{y + 14}" font-size="{size}">{esc(label)}</text></g>'
    )


def window_chrome(W, path):
    out = []
    for i, col in enumerate(("red", "amber", "teal")):
        out.append(f'<rect x="{16 + i * 12}" y="10" width="7" height="7" fill="var(--{col})"/>')
    out.append(f'<text class="mono mute" x="64" y="17" font-size="10" letter-spacing="1">{path}</text>')
    out.append(f'<line x1="14" y1="24" x2="{W - SHADOW - 14}" y2="24" stroke="var(--line)" stroke-width="2"/>')
    return out


def null_glyph(gx, gy, cols, rows, pitch, cell, lo, hi, slash_half, start=2.1):
    """The 'null' mark (ring + slash) from squares, then a looping comet + zip."""
    cx, cy = (cols - 1) / 2, (rows - 1) / 2
    cells = []
    for r in range(rows):
        for c in range(cols):
            dx, dy = c - cx, r - cy
            d = math.hypot(dx, dy)
            ring = lo <= d <= hi
            slash = abs(dx + dy) < 0.6 and abs(dy) <= slash_half
            if ring or slash:
                f = ((math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
                cells.append((d, c, r, "blue" if ring else "red", f, dy))
    cells.sort()
    out = []
    for i, (d, c, r, col, f, dy) in enumerate(cells):
        if col == "blue":
            loop = f'class="orbit" style="--d:{start + f * 3.6:.2f}s"'
        else:
            loop = f'class="zip" style="--d:{start + (slash_half - dy) * 0.11:.2f}s"'
        out.append(
            f'<g class="pop" style="--d:{0.5 + i * 0.018:.2f}s"><rect {loop} x="{gx + c * pitch}" y="{gy + r * pitch}" '
            f'width="{cell}" height="{cell}" fill="var(--{col})"/></g>')
    return out


HERO_ALT = "Nullstacks: open-source AI tools and utilities. Small, sharp, composable."


# ---- hero ------------------------------------------------------------------------------------
def hero():
    """880 x 224: terminal window, pixel title, stat chips, the animated null glyph."""
    W, H = WIDE, 224
    out = [frame(W, H, "blue")] + window_chrome(W, "~/nullstacks/README.md")
    stars = [(520, 44), (560, 150), (610, 62), (650, 120), (470, 170), (700, 40), (830, 40),
             (846, 190), (440, 52), (600, 196), (690, 190), (500, 100), (780, 196), (420, 120)]
    for i, (sx, sy) in enumerate(stars):
        out.append(f'<rect class="twinkle" style="--d:{i * .4:.1f}s;fill:var(--{("ink", "blue", "teal", "amber")[i % 4]})" '
                   f'x="{sx}" y="{sy}" width="3" height="3"/>')
    out += null_glyph(700, 44, 13, 11, 12, 9, 4.0, 5.45, 5)
    out.append('<text class="mono rise" style="--d:.1s" x="24" y="52" font-size="12"><tspan style="fill:var(--teal)">$</tspan>'
               '<tspan class="mute" dx="8">open github.com/nullstacks</tspan></text>')
    title, tx, ty = "NULLSTACKS", 24, 66  # flickers in letter by letter, then a blue glint travels across forever
    out.append(pixel_text(title, tx, ty, 7, 0, 'class="title" fill="var(--ink)"',
                          lambda i: f'style="--d:{0.15 + i * 0.09:.2f}s;--g:{2.2 + i * 0.1:.2f}s"'))
    out.append(f'<rect class="blink" x="{tx + text_width(title, 7, 0) + 10}" y="{ty + 20}" width="14" height="29" fill="var(--blue)"/>')
    out.append('<text class="rise" style="--d:.6s" x="24" y="148" font-size="15">Open-source AI tools and utilities.</text>'
               '<text class="serif mute rise" style="--d:.8s" x="24" y="169" font-size="15" font-style="italic">Small, sharp, composable.</text>')
    x = 24
    for i, (label, col) in enumerate(STATS):
        w, svgc = chip2(x, 184, label, col, 10, 1.0 + i * 0.1)
        out.append(svgc)
        x += w + 8
    return svg(W, H, "".join(out), HERO_ALT)


def hero_m():
    """320 x 176 phone hero: same window, title at 4px pixels, tagline, chips, a small glyph."""
    W, H = MW, 176
    out = [frame(W, H, "blue")] + window_chrome(W, "~/nullstacks/README.md")
    for i, (sx, sy) in enumerate([(236, 36), (262, 38), (292, 34), (302, 62), (240, 100), (266, 158), (298, 160)]):
        out.append(f'<rect class="twinkle" style="--d:{i * .4:.1f}s;fill:var(--{("ink", "blue", "teal", "amber")[i % 4]})" '
                   f'x="{sx}" y="{sy}" width="3" height="3"/>')
    out += null_glyph(256, 90, 9, 9, 6, 5, 3.0, 4.3, 3.6)
    out.append('<text class="mono rise" style="--d:.1s" x="20" y="48" font-size="11"><tspan style="fill:var(--teal)">$</tspan>'
               '<tspan class="mute" dx="8">open github.com/nullstacks</tspan></text>')
    title, tx, ty = "NULLSTACKS", 20, 58
    out.append(pixel_text(title, tx, ty, 4, 0, 'class="title" fill="var(--ink)"',
                          lambda i: f'style="--d:{0.15 + i * 0.09:.2f}s;--g:{2.2 + i * 0.1:.2f}s"'))
    out.append(f'<rect class="blink" x="{tx + text_width(title, 4, 0) + 8}" y="{ty + 11}" width="8" height="17" fill="var(--blue)"/>')
    out.append('<text class="rise" style="--d:.6s" x="20" y="116" font-size="13">Open-source AI tools and utilities.</text>'
               '<text class="serif mute rise" style="--d:.8s" x="20" y="134" font-size="13" font-style="italic">Small, sharp, composable.</text>')
    x = 20
    for i, (label, col) in enumerate(STATS[:3]):
        w, svgc = chip2(x, 146, label, col, 9, 1.0 + i * 0.1)
        out.append(svgc)
        x += w + 6
    return svg(W, H, "".join(out), HERO_ALT)


# ---- category banners (replace the old summary tiles) ---------------------------------------
def banner(key, delay, mobile=False):
    cat, col = CATS[key], CATS[key]["color"]
    names = [r[0] for r in REPOS if r[1] == key]
    n = len(names)
    W, H = (MW, 68) if mobile else (WIDE, 64)
    out = [f'<g class="rise" style="--d:{delay:.2f}s">', frame(W, H, col)]
    if mobile:
        out.append(sprite(SPRITES[key], 14, 14, 3, col, delay + 0.2))
        out.append(f'<text class="mono" x="48" y="24" font-size="10" font-weight="700" letter-spacing="1.5" style="fill:var(--{col})">{esc(cat["label"])}</text>')
        for i, ln in enumerate(wrap_balanced(cat["desc"], 38)):
            out.append(f'<text class="mute" x="48" y="{40 + i * 13}" font-size="10.5">{esc(ln)}</text>')
        dx, dy, cellp, lx, ly = 268, 14, 4, 268, 56
    else:
        out.append(sprite(SPRITES[key], 20, 15, 4, col, delay + 0.2))
        out.append(f'<text class="mono" x="66" y="29" font-size="11" font-weight="700" letter-spacing="2" style="fill:var(--{col})">{esc(cat["label"])}</text>')
        out.append(f'<text class="mute" x="66" y="47" font-size="12">{esc(cat["desc"])}</text>')
        out.append(f'<line x1="{W - SHADOW - 118}" y1="14" x2="{W - SHADOW - 118}" y2="46" stroke="var(--line)" stroke-width="2" stroke-dasharray="4 4"/>')
        dx, dy, cellp, lx, ly = W - SHADOW - 96, 15, 4, W - SHADOW - 96 + 34, 38
    # count-up in pixel digits: 0 .. n-1 flash by, then the final number stays
    for i in range(n):
        out.append(pixel_text(str(i), dx, dy, cellp, 0, f'class="tick" style="--d:{delay + .45 + i * .13:.2f}s;fill:var(--{col})"', bold=True))
    out.append(pixel_text(str(n), dx, dy, cellp, 0, f'class="final" style="--d:{delay + .45 + n * .13:.2f}s;fill:var(--{col})"', bold=True))
    out.append(f'<text class="mono mute" x="{lx}" y="{ly}" font-size="10">repos</text>')
    out.append("</g>")
    return svg(W, H, "".join(out), f'{cat["label"].title()}: {", ".join(names)}')


# ---- repo cards -----------------------------------------------------------------------------
def live_pill(x, y):
    return (f'<rect x="{x}" y="{y}" width="42" height="14" fill="none" stroke="var(--teal)" stroke-width="2"/>'
            f'<rect class="pulse" x="{x + 7}" y="{y + 5}" width="4" height="4" style="fill:var(--teal)"/>'
            f'<text class="mono" x="{x + 16}" y="{y + 10.5}" font-size="8.5" font-weight="700" style="fill:var(--teal)">LIVE</text>')


def repo_card(idx, slug, key, desc, lang, live_url, mobile=False):
    """Desktop: 192x92 (svg 200x100), 4 per row.  Mobile: 320x88 (svg 320x96), one per row."""
    col = CATS[key]["color"]
    W, H = (MW, M_H) if mobile else (D_W, D_H)
    lines = wrap_balanced(desc, 52 if mobile else 32)
    out = [f'<g class="rise" style="--d:{0.1 + (idx % 6) * 0.08:.2f}s">', frame(W, H, col)]
    out.append(f'<rect x="14" y="16" width="6" height="6" fill="var(--{col})"/>')
    out.append(f'<text class="mono" x="26" y="23" font-size="{12.5 if mobile else 11.5}" font-weight="700">{esc(slug)}</text>')
    fs, lh, y0 = (11, 14, 44) if mobile else (10.5, 13, 42)
    for i, ln in enumerate(lines):
        out.append(f'<text class="mute" x="14" y="{y0 + i * lh}" font-size="{fs}">{esc(ln)}</text>')
    sep, fy = (66, 79) if mobile else (66, 80)
    out.append(f'<line x1="14" y1="{sep}" x2="{W - SHADOW - 14}" y2="{sep}" stroke="var(--line)" stroke-width="2" stroke-dasharray="4 4"/>')
    out.append(f'<rect x="14" y="{fy - 6}" width="5" height="5" fill="var(--{col})"/>')
    out.append(f'<text class="mono mute" x="24" y="{fy}" font-size="9">{esc(lang)}</text>')
    if live_url:
        out.append(live_pill(W - SHADOW - 14 - 42, fy - 11))
    out.append("</g>")
    return svg(W + (0 if mobile else GUT), H + GUT, "".join(out), f"{slug}: {desc}")


# ---- link buttons ("try them live", contact) ------------------------------------------------
def button(label, col, icon=None, delay=0.0, live=False):
    """Pixel button, drawn at its natural size (+ GUT gutter) so a row of them wraps by itself."""
    tw = round(len(label) * 0.6 * 11)
    lead = 14 + (16 + 8 if icon else 6 + 8)
    W, H = lead + tw + 10 + 10 + 12 + SHADOW, 30
    out = [f'<g class="rise" style="--d:{delay:.2f}s">', frame(W, H, col)]
    if icon:
        out.append(sprite(icon, 14, 5, 2, col, delay + 0.2))
    else:
        out.append(f'<rect class="pulse" x="14" y="10" width="6" height="6" style="fill:var(--teal)"/>')
    out.append(f'<text class="mono" x="{lead}" y="18" font-size="11" font-weight="700">{esc(label)}</text>')
    out.append(sprite(ARROW, lead + tw + 10, 8, 2, col, delay + 0.3))
    out.append("</g>")
    return svg(W + GUT, H + GUT, "".join(out), label)


# ---- section headings + divider -------------------------------------------------------------
def heading(label, accent, idx=None, W=WIDE, cell=4, bold=True):
    H = 7 * cell + 6
    mid = 4 + 7 * cell / 2
    tw = text_width(label, cell, 0, bold=bold)
    start, end = 20 + tw + 14, W - (46 if idx else 0)
    out = [f'<rect class="blink" x="0" y="{mid - 5:g}" width="10" height="10" fill="var(--{accent})"/>',
           pixel_text(label, 20, 4, cell, 0, 'class="ink"', bold=bold)]
    if end - start >= 24:
        out.append(f'<line class="march" x1="{start}" y1="{mid:g}" x2="{end - 8}" y2="{mid:g}" stroke="var(--line)" '
                   f'stroke-width="{4 if cell >= 4 else 3}" stroke-dasharray="4 4"/>')
    if idx:
        out.append(f'<text class="mono mute" x="{W}" y="{mid + 4:g}" font-size="12" letter-spacing="1" text-anchor="end">// {idx:02d}</text>')
    return svg(W, H, "".join(out), label.title())


def divider(W=WIDE):
    cols = ["blue", "red", "amber", "teal"]
    out = [f'<rect class="wave" style="--d:{i * .06:.2f}s;fill:var(--{cols[i % 4]})" x="{i * 8}" y="4" width="4" height="4"/>'
           for i in range(W // 8)]
    return svg(W, 12, "".join(out), "divider")


# ---- README ----------------------------------------------------------------------------------
EMAIL = "help.pushkar@gmail.com"
ORG = "https://github.com/orgs/nullstacks/repositories"


def write_readme():
    def pic(name, alt):
        """Desktop card as the <img>; phones (max-width:600px) get NAME-m.svg. No width attribute: see docstring."""
        a = html.escape(alt)
        return (f'<picture><source media="(max-width: 600px)" srcset="{RAW}/{name}-m.svg" />'
                f'<img src="{RAW}/{name}.svg" alt="{a}" /></picture>')

    def plain(name, alt):
        return f'<img src="{RAW}/{name}.svg" alt="{html.escape(alt)}" />'

    def block(inner):
        return f'<p align="center">{inner}</p>'

    parts = [block(f'<a href="{ORG}">{pic("hero", HERO_ALT)}</a>'), "",
             block(pic("heading-projects", "Projects")), ""]
    for key, cat in CATS.items():
        cards = "".join(f'<a href="https://github.com/nullstacks/{r[0]}">{pic(r[0], r[0])}</a>' for r in REPOS if r[1] == key)
        parts.append(f'<p align="center">\n<a href="{ORG}">{pic("banner-" + key, cat["label"].title())}</a><br>\n{cards}\n</p>')
        parts.append("")
    parts += [block(pic("heading-live", "Try them live")), ""]
    # generated from the same field that drives the live pill on each card
    live = "".join(f'<a href="{url}">{plain("live-" + slug, LIVE_LABELS.get(slug, slug) + " (live)")}</a>'
                   for slug, _k, _d, _l, url in REPOS if url)
    parts += [f'<p align="center">\n{live}\n</p>', "",
              block(pic("heading-contact", "Contact")), "",
              "<p align=\"center\">Open an issue on any repo, or email:</p>", "",
              f'<p align="center">\n<a href="mailto:{EMAIL}">{plain("contact-email", "Email " + EMAIL)}</a>'
              f'<a href="{ORG}">{plain("contact-repos", "All repositories")}</a>\n</p>', "",
              block(pic("divider", "")), ""]
    with open(os.path.join(ROOT, "profile", "README.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts))
    print("wrote README.md")


def main():
    if os.path.isdir(CARDS):
        for f in os.listdir(CARDS):
            if f.endswith(".svg"):
                os.remove(os.path.join(CARDS, f))
    write("hero.svg", hero())
    write("hero-m.svg", hero_m())
    for i, key in enumerate(CATS):
        write(f"banner-{key}.svg", banner(key, 0.9 + i * 0.1))
        write(f"banner-{key}-m.svg", banner(key, 0.9 + i * 0.1, mobile=True))
    for i, (slug, key, desc, lang, live_url) in enumerate(REPOS):
        write(f"{slug}.svg", repo_card(i, slug, key, desc, lang, live_url))
        write(f"{slug}-m.svg", repo_card(i, slug, key, desc, lang, live_url, mobile=True))
    for i, (slug, key, _d, _l, url) in enumerate(r for r in REPOS if r[4]):
        write(f"live-{slug}.svg", button(LIVE_LABELS.get(slug, slug), CATS[key]["color"], delay=i * 0.08))
    write("contact-email.svg", button(EMAIL, "amber", MAIL))
    write("contact-repos.svg", button("all repositories", "blue", BOOK, delay=0.08))
    for name, label, col, idx in (("projects", "PROJECTS", "blue", 1), ("live", "TRY THEM LIVE", "teal", 2),
                                  ("contact", "CONTACT", "amber", 3)):
        write(f"heading-{name}.svg", heading(label, col, idx))
        write(f"heading-{name}-m.svg", heading(label, col, idx, W=MW, cell=3, bold=False))
    write("divider.svg", divider())
    write("divider-m.svg", divider(MW))
    write_readme()


if __name__ == "__main__":
    main()
