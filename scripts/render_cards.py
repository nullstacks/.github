#!/usr/bin/env python3
"""Render the pixel-themed animated SVG cards for the nullstacks org profile README.

Run from the repo root:    python scripts/render_cards.py
Writes:                    profile/cards/*.svg  and  profile/README.md
STATIC=1 python ...        renders final frames (no animation) for screenshots.

SIZING RULE (why this file is built the way it is)
  GitHub's README column is fluid: ~428px wide at a 780px viewport, ~592px at 1000px.
  An <img> shown narrower than its authored width is scaled DOWN and the type gets
  illegible, so every card is authored at the exact pixel width it renders at in the
  narrow case:
        FULL = 428   (hero, section headings, divider)   -> width="100%"
        HALF = 212   (tiles, repo cards; two per row)    -> width="49.5%"
  Wider columns scale the cards UP slightly, which stays sharp and legible.
  Two-up images are written back-to-back with no whitespace between the tags so
  49.5% + 49.5% always fits on one line.

Everything works inside <img> on GitHub: inline <style>, CSS keyframes,
prefers-color-scheme and prefers-reduced-motion. No scripts, no external requests,
no web fonts (the pixel lettering is drawn from rects, so it needs no font file).
"""
import html
import math
import os
import textwrap

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CARDS = os.path.join(ROOT, "profile", "cards")
STATIC = os.environ.get("STATIC") == "1"

FULL, HALF, SHADOW = 428, 212, 4
RAW = "https://raw.githubusercontent.com/nullstacks/.github/main/profile/cards"

SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"

# ---- content (from the READMEs of the public repos) ---------------------------------
CATS = {
    "gateways": dict(label="MODEL GATEWAYS", color="blue"),
    "services": dict(label="APIS & SERVICES", color="red"),
    "extensions": dict(label="BROWSER EXTENSIONS", color="amber"),
    "apps": dict(label="WEB APPS & TOOLS", color="teal"),
}

# slug, category, description (2 lines max at 212px), language, live demo?
REPOS = [
    ("kilo-gateway", "gateways", "Kilo's free models, keyless, as an OpenAI/Anthropic API.", "Python", False),
    ("opencode-gateway", "gateways", "OpenCode models and free tier in any harness. No key.", "Python", False),
    ("cline2api", "gateways", "Cline's free models as an API. Catalog auto-refreshes.", "Python", False),
    ("qoder2api", "gateways", "Qoder (intl) as a self-hosted OpenAI-compatible API.", "Python", False),
    ("mailapi", "services", "Your Gmail as a REST API. One key, many accounts.", "JavaScript", True),
    ("heardlist", "services", "Free proxy-list API. Hourly refresh, JSON/TXT/CSV.", "JavaScript", True),
    ("tack", "services", "Paste a page, get a rendered link and a raw link.", "HTML", True),
    ("temp-mail-extension", "extensions", "Disposable inbox for Chrome & Brave. Autofill, OTP copy.", "JavaScript", False),
    ("cookie-manager", "extensions", "Cookie editor for Chrome & Brave. JSON/cookies.txt export.", "JavaScript", False),
    ("google-forms-copilot", "extensions", "AI filler for Google Forms. You review every answer.", "JavaScript", False),
    ("papersnap", "apps", "Local PDF and image toolkit. 30 tools, no uploads.", "TypeScript", False),
    ("curl-toolkit", "apps", "cURL to 18 languages plus an in-browser API client.", "TypeScript", True),
    ("jee", "apps", "JEE Main 2027: PYQ chapters, rank predictor, JoSAA.", "TypeScript", False),
    ("mai-image", "apps", "Free image gen via Bing Image Creator. Skill + CLI.", "Python", False),
]

LIVE = [
    ("heardlist", "https://heardlist.pushkarsingh4343.workers.dev"),
    ("tack", "https://tack.nullstacks.workers.dev"),
    ("cURL Toolkit", "https://nullstacks.github.io/curl-toolkit/"),
    ("mailapi", "https://mailapi.pushkarsingh4343.workers.dev"),
]

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
    with open(os.path.join(CARDS, name), "w", encoding="utf-8") as fh:
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


def glyph_d(ch, x, y, cell, pitch, bold=False):
    rows = FONT[ch].split()
    lit = set()
    for r, row in enumerate(rows):
        for c, bit in enumerate(row):
            if bit == "1":
                lit.add((r, c))
                if bold:  # thicken every stroke by one pixel to the right
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


# ---- hero (428 wide) ----------------------------------------------------------------
def hero():
    W, H = FULL, 220
    out = [frame(W, H, "blue")]

    # twinkling stars
    for i, (sx, sy) in enumerate([(60, 100), (210, 98), (282, 102), (409, 128), (409, 160), (300, 164)]):
        out.append(f'<rect class="twinkle" style="--d:{i * .5:.1f}s;fill:var(--ink)" x="{sx}" y="{sy}" width="3" height="3"/>')

    # the "null" glyph: ring + slash, built from squares, then looping comet + zip
    cols, rows, pitch, cell = 13, 11, 8, 6
    gx, gy = 300, 22
    cx, cy = (cols - 1) / 2, (rows - 1) / 2
    cells = []
    for r in range(rows):
        for c in range(cols):
            dx, dy = c - cx, r - cy
            d = math.hypot(dx, dy)
            ring = 4.0 <= d <= 5.45
            slash = abs(dx + dy) < 0.6 and abs(dy) <= 5
            if ring or slash:
                f = ((math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
                cells.append((d, c, r, "blue" if ring else "red", f, dy))
    cells.sort()
    START = 2.1
    for i, (d, c, r, col, f, dy) in enumerate(cells):
        if col == "blue":
            loop = f'class="orbit" style="--d:{START + f * 3.6:.2f}s"'
        else:
            loop = f'class="zip" style="--d:{START + (5 - dy) * 0.11:.2f}s"'
        out.append(
            f'<g class="pop" style="--d:{0.5 + i * 0.018:.2f}s"><rect {loop} x="{gx + c * pitch}" y="{gy + r * pitch}" '
            f'width="{cell}" height="{cell}" fill="var(--{col})"/></g>'
        )

    out.append(
        '<text class="mono mute rise" style="--d:.1s" x="20" y="36" font-size="9.5" letter-spacing="1.5">GITHUB.COM/NULLSTACKS</text>'
        '<text class="rise" style="--d:.45s" x="20" y="62" font-size="13">Open-source AI tools and utilities.</text>'
        '<text class="serif mute rise" style="--d:.6s" x="20" y="82" font-size="13" font-style="italic">Small, sharp, composable.</text>'
    )

    # pixel title: flickers in letter by letter, then a blue glint travels across forever
    title = "NULLSTACKS"
    tx, ty = 20, 118
    out.append(pixel_text(title, tx, ty, 5, 1, 'class="title" fill="var(--ink)"',
                          lambda i: f'style="--d:{0.15 + i * 0.09:.2f}s;--g:{2.2 + i * 0.1:.2f}s"'))
    cursor_x = tx + text_width(title, 5, 1) + 8
    out.append(f'<rect class="blink" x="{cursor_x}" y="{ty + 18}" width="12" height="23" fill="var(--blue)"/>')

    x = 20
    for i, label in enumerate(["Cloudflare Workers", "Chrome MV3", "Python", "React", "MIT"]):
        w, c = chip(x, 176, label)
        out.append(f'<g class="rise" style="--d:{0.8 + i * 0.07:.2f}s">{c}</g>')
        x += w + 6
    return svg(W, H, "".join(out), "Nullstacks: open-source AI tools and utilities. Small, sharp, composable.")


# ---- category tiles (212 wide) --------------------------------------------------------
def tile(key, delay):
    cat = CATS[key]
    names = [r[0] for r in REPOS if r[1] == key]
    n = len(names)
    W, H = HALF, 88
    col = cat["color"]
    out = [f'<g class="rise" style="--d:{delay:.2f}s">', frame(W, H, col)]
    out.append(sprite(SPRITES[key], 14, 22, 4, col, delay + 0.2))
    out.append(f'<text class="mono mute" x="58" y="30" font-size="9.5" letter-spacing="1">{esc(cat["label"])}</text>')
    # count-up in pixel digits: 0 .. n-1 flash by, then the final number stays
    for i in range(n):
        out.append(pixel_text(str(i), 58, 40, 4, 1,
                              f'class="tick" style="--d:{delay + .45 + i * .13:.2f}s;fill:var(--{col})"', bold=True))
    out.append(pixel_text(str(n), 58, 40, 4, 1,
                          f'class="final" style="--d:{delay + .45 + n * .13:.2f}s;fill:var(--{col})"', bold=True))
    out.append(f'<text class="mono mute" x="96" y="73" font-size="10">repos</text>')
    out.append(f'<rect class="blink" x="{W - SHADOW - 16}" y="14" width="6" height="6" fill="var(--{col})"/>')
    out.append("</g>")
    return svg(W, H, "".join(out), f'{cat["label"].title()}: {", ".join(names)}')


# ---- repo cards (212 wide) --------------------------------------------------------------
def repo_card(idx, slug, key, desc, lang, live):
    W, H = HALF, 88
    col = CATS[key]["color"]
    d0 = 0.1 + (idx % 6) * 0.08
    lines = textwrap.wrap(desc, 33)[:2]
    out = [f'<g class="rise" style="--d:{d0:.2f}s">', frame(W, H, col)]
    out.append(f'<rect x="14" y="16" width="6" height="6" fill="var(--{col})"/>')
    out.append(f'<text class="mono" x="26" y="23" font-size="12" font-weight="700">{esc(slug)}</text>')
    for i, ln in enumerate(lines):
        out.append(f'<text class="mute" x="14" y="{42 + i * 13}" font-size="10.5">{esc(ln)}</text>')
    out.append(f'<rect x="14" y="68" width="5" height="5" fill="var(--{col})"/>')
    out.append(f'<text class="mono mute" x="24" y="74" font-size="9">{esc(lang)}</text>')
    if live:
        out.append(f'<rect class="pulse" x="{W - SHADOW - 44}" y="68" width="5" height="5" fill="var(--teal)"/>'
                   f'<text class="mono" x="{W - SHADOW - 12}" y="74" font-size="9" text-anchor="end" style="fill:var(--teal)">live</text>')
    out.append("</g>")
    return svg(W, H, "".join(out), f"{slug}: {desc}")


# ---- section headings + divider (428 wide) ----------------------------------------------
def heading(label, accent):
    W, H = FULL, 34
    cell, gap = 3, 1
    tw = text_width(label, cell, gap, bold=True)
    out = [
        f'<rect class="blink" x="0" y="8" width="10" height="10" fill="var(--{accent})"/>',
        pixel_text(label, 20, 4, cell, gap, 'class="ink"', bold=True),
        f'<line class="march" x1="{20 + tw + 14}" y1="10" x2="{W}" y2="10" stroke="var(--line)" stroke-width="4" stroke-dasharray="4 4"/>',
    ]
    return svg(W, H, "".join(out), label.title())


def divider():
    W, H = FULL, 12
    cols = ["blue", "red", "amber", "teal"]
    out = []
    for i in range(W // 8):
        out.append(f'<rect class="wave" style="--d:{i * .06:.2f}s;fill:var(--{cols[i % 4]})" x="{i * 8}" y="4" width="4" height="4"/>')
    return svg(W, H, "".join(out), "divider")


# ---- README ---------------------------------------------------------------------------------
def pair_rows(imgs):
    """Two images per line, no whitespace between the tags (so 49.5% + 49.5% never wraps)."""
    rows = []
    for i in range(0, len(imgs), 2):
        rows.append("".join(imgs[i:i + 2]))
    return "\n".join(rows)


def write_readme():
    org = "https://github.com/orgs/nullstacks/repositories"

    def img(name, alt, width):
        return f'<img src="{RAW}/{name}.svg" width="{width}" alt="{html.escape(alt)}" />'

    tiles = [f'<a href="{org}">{img("tile-" + k, c["label"].title(), "49.5%")}</a>' for k, c in CATS.items()]
    cards = [f'<a href="https://github.com/nullstacks/{r[0]}">{img(r[0], r[0], "49.5%")}</a>' for r in REPOS]
    live = " &nbsp;·&nbsp; ".join(f"[{n}]({u})" for n, u in LIVE)

    parts = [
        f'<p align="center"><a href="{org}">{img("hero", "Nullstacks: open-source AI tools and utilities. Small, sharp, composable.", "100%")}</a></p>',
        "",
        "<p>\n" + pair_rows(tiles) + "\n</p>",
        "",
        f'<p>{img("heading-projects", "Projects", "100%")}</p>',
        "",
        "<p>\n" + pair_rows(cards) + "\n</p>",
        "",
        f'<p>{img("heading-live", "Try them live", "100%")}</p>',
        "",
        live,
        "",
        f'<p>{img("heading-contact", "Contact", "100%")}</p>',
        "",
        "Open an issue, or email [help.pushkar@gmail.com](mailto:help.pushkar@gmail.com).",
        "",
        f'<p>{img("divider", "", "100%")}</p>',
        "",
    ]
    with open(os.path.join(ROOT, "profile", "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    print("wrote README.md")


def main():
    if os.path.isdir(CARDS):
        for f in os.listdir(CARDS):
            if f.endswith(".svg"):
                os.remove(os.path.join(CARDS, f))
    write("hero.svg", hero())
    for i, key in enumerate(CATS):
        write(f"tile-{key}.svg", tile(key, 1.0 + i * 0.18))
    for i, (slug, key, desc, lang, live) in enumerate(REPOS):
        write(f"{slug}.svg", repo_card(i, slug, key, desc, lang, live))
    write("heading-projects.svg", heading("PROJECTS", "blue"))
    write("heading-live.svg", heading("TRY THEM LIVE", "teal"))
    write("heading-contact.svg", heading("CONTACT", "amber"))
    write("divider.svg", divider())
    write_readme()


if __name__ == "__main__":
    main()
