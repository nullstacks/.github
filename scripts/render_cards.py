#!/usr/bin/env python3
"""Render the animated SVG cards for the nullstacks org profile README.

Run from the repo root:   python scripts/render_cards.py
Writes:                   profile/cards/*.svg
STATIC=1 python ...       renders the final frame (no animation) for screenshots.

Everything here works inside <img> on GitHub: inline <style>, CSS keyframes,
prefers-color-scheme and prefers-reduced-motion. No scripts, no external requests.
"""
import html
import math
import os
import textwrap

OUT = os.path.join(os.path.dirname(__file__), "..", "profile", "cards")
STATIC = os.environ.get("STATIC") == "1"

SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"

# ---- content (from the READMEs of the public repos) -------------------------
CATS = {
    "gateways": dict(label="MODEL GATEWAYS", color="blue", anchor="model-gateways"),
    "services": dict(label="APIS & SERVICES", color="red", anchor="apis--services"),
    "extensions": dict(label="BROWSER EXTENSIONS", color="amber", anchor="browser-extensions"),
    "apps": dict(label="WEB APPS & TOOLS", color="teal", anchor="web-apps--tools"),
}

# slug, category, short description (2 lines max), language, live?
REPOS = [
    ("kilo-gateway", "gateways", "Kilo's free models, keyless, as an OpenAI/Anthropic-compatible API.", "Python", False),
    ("opencode-gateway", "gateways", "OpenCode models incl. free tier in any harness. No account or key.", "Python", False),
    ("cline2api", "gateways", "Cline's free models as an API. Catalog auto-refreshes every 10 min.", "Python", False),
    ("qoder2api", "gateways", "Qoder (intl) as a self-hosted OpenAI-compatible API, device-flow login.", "Python", False),
    ("mailapi", "services", "Your Gmail as a REST API. One key, many accounts, +tag temp inboxes.", "JavaScript", True),
    ("heardlist", "services", "Free public proxy-list API. Hourly refresh, JSON/TXT/CSV, no key.", "JavaScript", True),
    ("tack", "services", "Paste a page, get a rendered link and a raw link. Durable Objects.", "HTML", True),
    ("temp-mail-extension", "extensions", "Disposable inbox for Chrome & Brave with autofill and OTP copy.", "JavaScript", False),
    ("cookie-manager", "extensions", "Cookie editor for Chrome & Brave. JSON, header and cookies.txt export.", "JavaScript", False),
    ("google-forms-copilot", "extensions", "AI filler for Google Forms. Bring your own key, you review answers.", "JavaScript", False),
    ("papersnap", "apps", "Local PDF and image toolkit. 30 tools, no uploads, no server.", "TypeScript", False),
    ("curl-toolkit", "apps", "cURL to 18 languages plus an API client that runs in your browser.", "TypeScript", True),
    ("jee", "apps", "JEE Main 2027: PYQ-ranked chapters, rank predictor, JoSAA cut-offs.", "TypeScript", False),
    ("mai-image", "apps", "Free image generation via Bing Image Creator. Agent skill + CLI.", "Python", False),
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
.fade{animation:fade .8s ease-out var(--d,0s) backwards}
.tick{opacity:0;animation:tick .13s linear var(--d,0s) both}
.final{animation:fade .3s ease-out var(--d,0s) backwards}
.blink{animation:blink 1.1s steps(1) infinite}
.ring{transform-box:fill-box;transform-origin:center;animation:ring 3.2s ease-out var(--d,0s) infinite}
.nudge{animation:nudge 2.6s ease-in-out var(--d,0s) infinite}
.pulse{animation:pulse 2s ease-in-out infinite}
.orbit{opacity:.4;transform-box:fill-box;transform-origin:center;animation:orbit 3.6s linear var(--d,0s) infinite}
.zip{opacity:.4;transform-box:fill-box;transform-origin:center;animation:zip 4.2s linear var(--d,0s) infinite}
@keyframes rise{from{opacity:0;transform:translateY(14px)}}
@keyframes swing{from{opacity:0;transform:translateY(26px) rotate(-3deg)}60%%{transform:translateY(-4px) rotate(.6deg)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes fade{from{opacity:0}}
@keyframes tick{0%%,99%%{opacity:1}100%%{opacity:0}}
@keyframes blink{50%%{opacity:0}}
@keyframes ring{0%%{opacity:.5;transform:scale(.6)}70%%,100%%{opacity:0;transform:scale(2.2)}}
@keyframes nudge{0%%,100%%{transform:translate(0,0)}50%%{transform:translate(3px,-3px)}}
@keyframes pulse{50%%{opacity:.35}}
@keyframes orbit{0%%{opacity:1;transform:scale(1.18)}22%%{opacity:.4;transform:scale(1)}100%%{opacity:.4}}
@keyframes zip{0%%{opacity:1;transform:scale(1.3)}14%%{opacity:.4;transform:scale(1)}100%%{opacity:.4}}
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
    print("wrote", name, len(content), "bytes")


def esc(s):
    return html.escape(s, quote=False)


def chip(x, y, label, color="mute", mono=True, size=11):
    cw = 0.6 * size if mono else 0.56 * size
    w = len(label) * cw + 18
    cls = ("mono " if mono else "") + ("mute" if color == "mute" else "")
    fill = "" if color == "mute" else f' style="fill:var(--{color})"'
    return w, (
        f'<rect x="{x}" y="{y}" width="{w:.1f}" height="22" rx="11" fill="none" stroke="var(--line)"/>'
        f'<text class="{cls.strip()}" x="{x + 9}" y="{y + 15}" font-size="{size}"{fill}>{esc(label)}</text>'
    )


# ---- hero --------------------------------------------------------------------
def hero():
    W, H = 960, 250
    out = [f'<rect width="{W}" height="{H}" rx="18" fill="var(--bg)"/>'
           f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="17.5" fill="none" stroke="var(--line)"/>']

    # the "null" glyph, drawn as a grid of squares: ring + slash
    cols, rows, pitch, cell = 13, 11, 17, 13
    gx, gy = 700, 32
    cx, cy = (cols - 1) / 2, (rows - 1) / 2
    cells = []
    for r in range(rows):
        for c in range(cols):
            dx, dy = c - cx, r - cy
            d = math.hypot(dx, dy)
            ring = 4.0 <= d <= 5.45
            slash = abs(dx + dy) < 0.6 and abs(dy) <= 5
            if ring or slash:
                # f: 0..1 clockwise position around the ring, starting at 12 o'clock
                f = ((math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
                cells.append((d, c, r, "blue" if ring else "red", f, dy))
    cells.sort()
    START = 2.1  # loop animations begin once the build-in has finished
    for i, (d, c, r, col, f, dy) in enumerate(cells):
        if col == "blue":
            loop = f'class="orbit" style="--d:{START + f * 3.6:.2f}s"'
        else:  # slash pixels flash bottom-left -> top-right
            loop = f'class="zip" style="--d:{START + (5 - dy) * 0.11:.2f}s"'
        out.append(
            f'<g class="pop" style="--d:{0.5 + i * 0.018:.2f}s"><rect {loop} x="{gx + c * pitch}" y="{gy + r * pitch}" '
            f'width="{cell}" height="{cell}" rx="3" fill="var(--{col})"/></g>'
        )

    out.append(
        '<text class="mono mute rise" style="--d:.1s" x="56" y="62" font-size="13" letter-spacing="2">'
        'GITHUB.COM/NULLSTACKS</text>'
        '<text class="serif rise" style="--d:.25s" x="52" y="132" font-size="72" font-weight="700" '
        'letter-spacing="-2">Nullstacks<tspan class="blink" style="fill:var(--blue)">_</tspan></text>'
        '<text class="rise" style="--d:.5s" x="56" y="172" font-size="19">'
        'Open-source AI tools and utilities.</text>'
        '<text class="serif mute rise" style="--d:.65s" x="56" y="200" font-size="19" font-style="italic">'
        'Small, sharp, composable.</text>'
    )

    x = 56
    for i, label in enumerate(["Cloudflare Workers", "Chrome MV3", "Python", "React", "MIT"]):
        w, c = chip(x, 214, label, size=11)
        out.append(f'<g class="rise" style="--d:{0.8 + i * 0.07:.2f}s">{c}</g>')
        x += w + 8
    return svg(W, H, "".join(out), "Nullstacks: open-source AI tools and utilities. Small, sharp, composable.")


# ---- category tiles ------------------------------------------------------------
def tile(key, delay):
    cat = CATS[key]
    names = [r[0] for r in REPOS if r[1] == key]
    n = len(names)
    W, H = 232, 190
    col = cat["color"]
    d0 = delay
    out = [
        f'<g class="swing" style="--d:{d0:.2f}s">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="var(--card)" stroke="var(--line)"/>',
        f'<rect x="1" y="1" width="{W-2}" height="6" rx="3" style="fill:var(--{col})"/>',
        f'<circle class="ring" style="--d:{d0+.6:.2f}s;stroke:var(--{col})" cx="{W-30}" cy="34" r="8" fill="none" stroke-width="2"/>',
        f'<circle cx="{W-30}" cy="34" r="4" style="fill:var(--{col})"/>',
        f'<text class="mono mute" x="20" y="38" font-size="10.5" letter-spacing="1.4">{esc(cat["label"])}</text>',
    ]
    # count-up: ticks 0..n-1 then the final number
    for i in range(n):
        out.append(
            f'<text class="tick serif" style="--d:{d0+.45+i*.13:.2f}s;fill:var(--{col})" x="20" y="102" '
            f'font-size="60" font-weight="700">{i}</text>'
        )
    out.append(
        f'<text class="final serif" style="--d:{d0+.45+n*.13:.2f}s;fill:var(--{col})" x="20" y="102" '
        f'font-size="60" font-weight="700">{n}</text>'
    )
    out.append(f'<text class="mute" x="{20 + 38}" y="102" font-size="13">repos</text>')
    for i, nm in enumerate(names):
        out.append(f'<text class="mono rise" style="--d:{d0+.7+i*.08:.2f}s" x="20" y="{128 + i*16}" font-size="11.5">'
                   f'<tspan class="mute">› </tspan>{esc(nm)}</text>')
    out.append(f'<g class="nudge" style="--d:{d0:.2f}s"><text x="{W-34}" y="{H-16}" font-size="18" '
               f'style="fill:var(--{col})">↘</text></g></g>')
    return svg(W, H, "".join(out), f'{cat["label"].title()}: {", ".join(names)}')


# ---- repo cards (compact, 3 per row) -----------------------------------------
def repo_card(idx, slug, key, desc, lang, live):
    W, H = 310, 88
    col = CATS[key]["color"]
    d0 = 0.1 + (idx % 6) * 0.08
    lines = textwrap.wrap(desc, 42)[:2]
    out = [
        f'<g class="rise" style="--d:{d0:.2f}s">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="var(--card)" stroke="var(--line)"/>',
        f'<rect x="1" y="14" width="3.5" height="22" rx="1.75" style="fill:var(--{col})"/>',
        f'<text class="mono" x="16" y="30" font-size="13.5" font-weight="700">{esc(slug)}</text>',
        f'<text x="{W-14}" y="30" font-size="10.5" text-anchor="end" font-weight="600" style="fill:var(--{col})">{esc(lang)}</text>',
    ]
    for i, ln in enumerate(lines):
        out.append(f'<text class="mute" x="16" y="{51 + i*16}" font-size="12">{esc(ln)}</text>')
    if live:
        out.append(f'<text class="mono pulse" x="{W-14}" y="{H-12}" font-size="9.5" text-anchor="end" style="fill:var(--teal)">● live</text>')
    out.append("</g>")
    return svg(W, H, "".join(out), f"{slug}: {desc}")


def write_readme():
    raw = "https://raw.githubusercontent.com/nullstacks/.github/main/profile/cards"
    L = [
        f'<p align="center">\n  <a href="https://github.com/orgs/nullstacks/repositories"><img src="{raw}/hero.svg" width="100%" alt="Nullstacks: open-source AI tools and utilities. Small, sharp, composable." /></a>\n</p>\n',
        '<p align="center">',
    ]
    for k, c in CATS.items():
        L.append(f'  <a href="#projects"><img src="{raw}/tile-{k}.svg" width="24.4%" alt="{esc(c["label"].title())}" /></a>')
    L.append("</p>\n\n## Projects\n")
    L.append("<p>")
    for r in REPOS:
        L.append(f'  <a href="https://github.com/nullstacks/{r[0]}"><img src="{raw}/{r[0]}.svg" width="32.5%" alt="{r[0]}" /></a>')
    L.append("</p>\n")
    # Live URLs: the old pushkarsingh4343.workers.dev subdomain no longer
    # resolves (NXDOMAIN) - the Workers moved to nullstacks.workers.dev.
    LIVE = [
        ("heardlist", "https://heardlist.nullstacks.workers.dev"),
        ("tack", "https://tack.nullstacks.workers.dev"),
        ("cURL Toolkit", "https://nullstacks.github.io/curl-toolkit/"),
        ("mailapi", "https://mailapi.nullstacks.workers.dev"),
        ("papersnap", "https://papersnap.nullstacks.workers.dev"),
        ("jee", "https://jee.nullstacks.workers.dev"),
    ]
    L.append("**Try them live:** " +
             " · ".join(f"[{label}]({url})" for label, url in LIVE) + "\n")
    L.append("## Contact\n\nOpen an issue, or email [help.pushkar@gmail.com](mailto:help.pushkar@gmail.com).\n")
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
