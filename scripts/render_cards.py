#!/usr/bin/env python3
"""Render the animated SVG cards for the nullstacks org profile README.

Run from the repo root:   python scripts/render_cards.py
Writes:                   profile/cards/*.svg and profile/README.md
STATIC=1 python ...       renders the final frame (no animation) for screenshots.

Everything works inside <img> on GitHub: inline <style>, CSS keyframes,
prefers-color-scheme and prefers-reduced-motion. No scripts, no external requests.

SIZING, which is the whole point of this file
---------------------------------------------
GitHub's README column is about 428 CSS px wide on the org overview page. An SVG
shown through <img width="49.5%"> is scaled to fit that fraction of the column,
so type inside the SVG shrinks by the same factor. Authoring a card at 310 px and
displaying it at 139 px renders 13.5 px text at 6 px - unreadable.

So every card here is authored at exactly the pixel width it will be displayed
at (COL for full width, COL2 for two-up). Scale 1.0 means the font sizes in this
file are the font sizes a visitor sees. COL was measured from the live page;
re-measure it if GitHub changes the layout.
"""
import html
import math
import os
import textwrap

OUT = os.path.join(os.path.dirname(__file__), "..", "profile", "cards")
STATIC = os.environ.get("STATIC") == "1"

# Measured width of the README column on github.com/<org>. Authored 1:1.
COL = 428
COL2 = 212          # two-up: 49.5% of COL, floored for the gutter

SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"

# ---- content (from the READMEs of the public repos) -------------------------
CATS = {
    "gateways": dict(label="MODEL GATEWAYS", color="blue"),
    "services": dict(label="APIS & SERVICES", color="red"),
    "extensions": dict(label="BROWSER EXTENSIONS", color="amber"),
    "apps": dict(label="WEB APPS & TOOLS", color="teal"),
}

# slug, category, description, language, live-demo link or None
REPOS = [
    ("kilo-gateway", "gateways",
     "Kilo's free models, keyless, as an OpenAI-compatible endpoint.",
     "Python", None),
    ("opencode-gateway", "gateways",
     "OpenCode models, free tier included, in any harness.",
     "Python", None),
    ("cline2api", "gateways",
     "Cline's free models as an API, refreshing every 10 min.",
     "Python", None),
    ("qoder2api", "gateways",
     "Qoder as a self-hosted OpenAI-compatible API.",
     "Python", None),
    ("mailapi", "services",
     "Your Gmail as a REST API. One key, any account.",
     "JavaScript", "https://mailapi.nullstacks.workers.dev"),
    ("heardlist", "services",
     "Free proxy-list API, refreshed hourly. JSON or CSV.",
     "JavaScript", "https://heardlist.nullstacks.workers.dev"),
    ("tack", "services",
     "Paste a page, get a rendered and a raw link.",
     "HTML", "https://tack.nullstacks.workers.dev"),
    ("temp-mail-extension", "extensions",
     "Disposable inbox for Chrome & Brave. OTP copy.",
     "JavaScript", None),
    ("cookie-manager", "extensions",
     "Cookie editor for Chrome & Brave. JSON or cookies.txt.",
     "JavaScript", None),
    ("google-forms-copilot", "extensions",
     "AI filler for Google Forms. Bring your own key.",
     "JavaScript", None),
    ("papersnap", "apps",
     "Local PDF and image toolkit. 30 tools, no uploads.",
     "TypeScript", "https://papersnap.nullstacks.workers.dev"),
    ("curl-toolkit", "apps",
     "cURL to 18 languages, plus a browser API client.",
     "TypeScript", "https://nullstacks.github.io/curl-toolkit/"),
    ("jee", "apps",
     "JEE Main 2027: PYQ-ranked chapters and JoSAA cut-offs.",
     "TypeScript", "https://jee.nullstacks.workers.dev"),
    ("mai-image", "apps",
     "Free image generation via Bing. Agent skill plus CLI.",
     "Python", None),
]

# ---- shared svg bits ---------------------------------------------------------
CSS = """
:root{--bg:#fbfaf6;--card:#ffffff;--ink:#17171a;--mute:#6b6b73;--line:#e3e0d6;
--blue:#2f6fed;--red:#e5484d;--amber:#c98100;--teal:#12a37f}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--card:#12171e;--ink:#ecebe6;--mute:#8b949e;--line:#262c36;
--blue:#6ea0ff;--red:#ff7b7f;--amber:#f5b942;--teal:#3ddbb0}}
text{font-family:%(sans)s;fill:var(--ink)}
.serif{font-family:%(serif)s}.mono{font-family:%(mono)s}.mute{fill:var(--mute)}
.rise{animation:rise .8s cubic-bezier(.2,.8,.2,1) var(--d,0s) backwards}
.swing{transform-box:fill-box;transform-origin:50%% 100%%;animation:swing 1s cubic-bezier(.2,1.2,.3,1) var(--d,0s) backwards}
.pop{transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,1.4,.4,1) var(--d,0s) backwards}
.tick{opacity:0;animation:tick .13s linear var(--d,0s) both}
.final{animation:fade .3s ease-out var(--d,0s) backwards}
.blink{animation:blink 1.1s steps(1) infinite}
.ring{transform-box:fill-box;transform-origin:center;animation:ring 3.2s ease-out var(--d,0s) infinite}
.nudge{animation:nudge 2.6s ease-in-out var(--d,0s) infinite}
.pulse{animation:pulse 2s ease-in-out infinite}
.orbit{animation:orbit 3.6s ease-in-out var(--d,0s) infinite}
.zip{animation:zip 1.2s ease-out var(--d,0s) infinite}
@keyframes rise{from{opacity:0;transform:translateY(14px)}}
@keyframes swing{from{opacity:0;transform:translateY(26px) rotate(-3deg)}60%%{transform:translateY(-4px) rotate(.6deg)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes fade{from{opacity:0}}
@keyframes tick{0%%,99%%{opacity:1}100%%{opacity:0}}
@keyframes blink{50%%{opacity:0}}
@keyframes ring{0%%{opacity:.5;transform:scale(.6)}70%%,100%%{opacity:0;transform:scale(2.2)}}
@keyframes nudge{0%%,100%%{transform:translate(0,0)}50%%{transform:translate(3px,-3px)}}
@keyframes pulse{50%%{opacity:.35}}
@keyframes orbit{0%%,100%%{opacity:.35}50%%{opacity:1}}
@keyframes zip{0%%,100%%{opacity:.4}50%%{opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.tick{opacity:0}.orbit,.zip{opacity:1}}
""" % dict(sans=SANS, serif=SERIF, mono=MONO)

if STATIC:
    CSS += "*{animation:none!important}.tick{opacity:0}.orbit,.zip{opacity:1}"


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>'
        f"<style>{CSS}</style>{body}</svg>"
    )


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"wrote {name} {len(content)} bytes")


def esc(s):
    return html.escape(s, quote=False)


def text_w(s, size, mono=False, bold=False):
    """Approximate advance width, used to fit chips and truncate labels."""
    cw = 0.60 if mono else 0.55
    if bold:
        cw += 0.02
    return len(s) * cw * size


def fit(s, max_w, size, mono=False, bold=False, ellipsis="\u2026"):
    """Trim s until it fits max_w, appending an ellipsis. Prevents overflow."""
    if text_w(s, size, mono, bold) <= max_w:
        return s
    out = s
    while out and text_w(out + ellipsis, size, mono, bold) > max_w:
        out = out[:-1]
    return out.rstrip(" ,.-") + ellipsis


def chip(x, y, label, color="mute", size=10, h=18):
    w = text_w(label, size, mono=True) + 14
    fill = "" if color == "mute" else f' style="fill:var(--{color})"'
    return w, (
        f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="none" stroke="var(--line)"/>'
        f'<text class="mono" x="{x + 7:.1f}" y="{y + h*0.71:.1f}" font-size="{size}"{fill}>{esc(label)}</text>'
    )


# ---- hero --------------------------------------------------------------------
def hero():
    W, H = COL, 176
    out = [f'<rect width="{W}" height="{H}" rx="14" fill="var(--bg)"/>'
           f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="13.5" fill="none" stroke="var(--line)"/>']

    # the "null" glyph as a grid of squares: ring + slash
    cols, rows, pitch, cell = 11, 9, 12, 9
    gx, gy = W - 148, 30
    cx, cy = (cols - 1) / 2, (rows - 1) / 2
    cells = []
    for r in range(rows):
        for c in range(cols):
            dx, dy = c - cx, r - cy
            d = math.hypot(dx, dy)
            ring = 3.1 <= d <= 4.3
            slash = abs(dx + dy) < 0.55 and abs(dy) <= 3.9
            if ring or slash:
                f = ((math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
                cells.append((d, c, r, "blue" if ring else "red", f, dy))
    cells.sort()
    START = 2.0
    for i, (d, c, r, col, f, dy) in enumerate(cells):
        loop = (f'class="orbit" style="--d:{START + f * 3.6:.2f}s"' if col == "blue"
                else f'class="zip" style="--d:{START + (4 - dy) * 0.11:.2f}s"')
        out.append(
            f'<g class="pop" style="--d:{0.5 + i * 0.02:.2f}s">'
            f'<rect {loop} x="{gx + c * pitch}" y="{gy + r * pitch}" '
            f'width="{cell}" height="{cell}" rx="2" fill="var(--{col})"/></g>'
        )

    out.append(
        '<text class="mono mute rise" style="--d:.1s" x="20" y="34" font-size="9.5" letter-spacing="1.5">'
        'GITHUB.COM/NULLSTACKS</text>'
        '<text class="serif rise" style="--d:.25s" x="18" y="86" font-size="46" font-weight="700" '
        'letter-spacing="-1.2">Nullstacks<tspan class="blink" style="fill:var(--blue)">_</tspan></text>'
        '<text class="rise" style="--d:.5s" x="20" y="112" font-size="13.5">'
        'Open-source AI tools and utilities.</text>'
        '<text class="serif mute rise" style="--d:.65s" x="20" y="132" font-size="13.5" font-style="italic">'
        'Small, sharp, composable.</text>'
    )

    x = 20
    for i, label in enumerate(["Cloudflare Workers", "Chrome MV3", "Python", "React", "MIT"]):
        w, c = chip(x, 148, label, size=9.5, h=17)
        out.append(f'<g class="rise" style="--d:{0.8 + i * 0.07:.2f}s">{c}</g>')
        x += w + 6
    return svg(W, H, "".join(out), "Nullstacks: open-source AI tools and utilities. Small, sharp, composable.")


# ---- category tile (two-up, so it gets COL2) ----------------------------------
def tile(key, delay):
    cat = CATS[key]
    names = [r[0] for r in REPOS if r[1] == key]
    n = len(names)
    W, H = COL2, 146
    col = cat["color"]
    d0 = delay
    out = [
        f'<g class="swing" style="--d:{d0:.2f}s">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="13" fill="var(--card)" stroke="var(--line)"/>',
        f'<rect x="1" y="1" width="{W-2}" height="4.5" rx="2.25" style="fill:var(--{col})"/>',
        f'<circle class="ring" style="--d:{d0+.6:.2f}s;stroke:var(--{col})" cx="{W-24}" cy="28" r="6.5" fill="none" stroke-width="1.8"/>',
        f'<circle cx="{W-24}" cy="28" r="3.2" style="fill:var(--{col})"/>',
        f'<text class="mono mute" x="16" y="31" font-size="9" letter-spacing="1.1">{esc(cat["label"])}</text>',
    ]
    # count-up: ticks 0..n-1 then the final number
    for i in range(n):
        out.append(
            f'<text class="tick serif" data-cu="1" style="--d:{d0+.45+i*.13:.2f}s;fill:var(--{col})" '
            f'x="16" y="82" font-size="42" font-weight="700">{i}</text>' 
        )
    out.append(
        f'<text class="final serif" data-cu="1" style="--d:{d0+.45+n*.13:.2f}s;fill:var(--{col})" '
        f'x="16" y="82" font-size="42" font-weight="700">{n}</text>' 
    )
    out.append(f'<text class="mute" x="{16 + 30}" y="82" font-size="11">repos</text>')
    # a tile is only 132px tall, so show three names and count the rest
    shown = names[:3]
    for i, nm in enumerate(shown):
        label = fit(nm, W - 46, 10, mono=True)
        out.append(f'<text class="mono rise" style="--d:{d0+.7+i*.08:.2f}s" x="16" y="{101 + i*14}" font-size="10">'
                   f'<tspan class="mute">› </tspan>{esc(label)}</text>')
    if len(names) > len(shown):
        out.append(f'<text class="mono mute" x="16" y="{99 + len(shown)*14}" font-size="9">'
                   f'+{len(names)-len(shown)} more</text>')
    out.append(f'<g class="nudge" style="--d:{d0:.2f}s"><text x="{W-22}" y="{H-12}" font-size="14" '
               f'style="fill:var(--{col})">↘</text></g></g>')
    return svg(W, H, "".join(out), f'{cat["label"].title()}: {", ".join(names)}')


# ---- repo card (two-up, authored at its rendered width) -----------------------
def repo_card(idx, slug, key, desc, lang, live):
    W, H = COL2, 86
    col = CATS[key]["color"]
    d0 = 0.1 + (idx % 6) * 0.08
    # leave room for the language badge on the title line
    name_max = W - 30 - text_w(lang, 9, bold=True) - 14
    name = fit(slug, name_max, 11.5, mono=True, bold=True)
    wrapped = textwrap.wrap(desc, 34)
    lines = wrapped[:2]
    if len(wrapped) > 2:
        # truncation must be visible: "no server." cut to "no" reads as a typo
        lines[1] = fit(lines[1] + " " + " ".join(wrapped[2:]), 34 * 5.4, 10.5,
                       ellipsis=" \u2026")
    out = [
        f'<g class="rise" style="--d:{d0:.2f}s">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="11" fill="var(--card)" stroke="var(--line)"/>',
        f'<rect x="1" y="13" width="3" height="18" rx="1.5" style="fill:var(--{col})"/>',
        f'<text class="mono" x="14" y="27" font-size="11.5" font-weight="700">{esc(name)}</text>',
        f'<text x="{W-12}" y="27" font-size="9" text-anchor="end" font-weight="600" '
        f'style="fill:var(--{col})">{esc(lang)}</text>',
    ]
    for i, ln in enumerate(lines):
        out.append(f'<text class="mute" x="14" y="{44 + i*13}" font-size="10.5">{esc(ln)}</text>')
    if live:
        out.append(f'<text class="mono pulse" x="{W-12}" y="{H-9}" font-size="8.5" '
                   f'text-anchor="end" style="fill:var(--teal)">● live</text>')
    out.append("</g>")
    return svg(W, H, "".join(out), f"{slug}: {desc}")


def write_readme():
    raw = "https://raw.githubusercontent.com/nullstacks/.github/main/profile/cards"
    L = [
        f'<p align="center">\n  <a href="https://github.com/orgs/nullstacks/repositories">'
        f'<img src="{raw}/hero.svg" width="100%" alt="Nullstacks: open-source AI tools and utilities. '
        f'Small, sharp, composable." /></a>\n</p>\n',
        '<p align="center">',
    ]
    for i, (k, c) in enumerate(CATS.items()):
        L.append(f'  <a href="#projects"><img src="{raw}/tile-{k}.svg" width="49.5%" '
                 f'alt="{esc(c["label"].title())}" /></a>')
        # two tiles per row; a new <p> starts the next row
        if i % 2 == 1 and i != len(CATS) - 1:
            L.append("</p>\n\n<p align=\"center\">")
    L.append("</p>\n\n## Projects\n")
    L.append("<p>")
    for i, r in enumerate(REPOS):
        L.append(f'  <a href="https://github.com/nullstacks/{r[0]}">'
                 f'<img src="{raw}/{r[0]}.svg" width="49.5%" alt="{r[0]}" /></a>')
        if i % 2 == 1 and i != len(REPOS) - 1:
            L.append("</p>\n\n<p>")
    L.append("</p>\n")
    # Live URLs: the old pushkarsingh4343.workers.dev subdomain no longer
    # resolves (NXDOMAIN); the Workers moved to nullstacks.workers.dev.
    LIVE = [(r[0], r[4]) for r in REPOS if r[4]]
    L.append("**Try them live:** " +
             " · ".join(f"[{label}]({url})" for label, url in LIVE) + "\n")
    L.append("## Contact\n\nOpen an issue, or email "
             "[help.pushkar@gmail.com](mailto:help.pushkar@gmail.com).\n")
    path = os.path.join(OUT, "..", "README.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("wrote README.md")


def main():
    write("hero.svg", hero())
    for i, key in enumerate(CATS):
        write(f"tile-{key}.svg", tile(key, 1.0 + i * 0.18))
    for i, (slug, key, desc, lang, live) in enumerate(REPOS):
        write(f"{slug}.svg", repo_card(i, slug, key, desc, lang, live))
    write_readme()


if __name__ == "__main__":
    main()
