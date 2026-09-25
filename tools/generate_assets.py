#!/usr/bin/env python3
"""Generate unique SVG assets for the profile README."""
import html
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

BG = "#0D1117"
PANEL = "#161B22"
BORDER = "#30363D"
FG = "#C9D1D9"
MUTED = "#8B949E"
ACCENT = "#38BDF8"
GREEN = "#3FB950"
YELLOW = "#D29922"
RED = "#F85149"
PROMPT = "#7EE787"

# ---------------------------------------------------------------- terminal
TERM_W, TERM_H = 940, 340
DOTS = [(RED, 24), (YELLOW, 48), (GREEN, 72)]

lines = [
    (PROMPT, "$ ", FG, "whoami"),
    (FG, "abdullah-bin-asim", MUTED, ""),
    (PROMPT, "$ ", FG, "cat role.txt"),
    (ACCENT, "Full-Stack Developer · AI & Automation", MUTED, ""),
    (PROMPT, "$ ", FG, "ls skills/"),
    (FG, "typescript  react  nextjs  nodejs  python  docker", MUTED, ""),
    (PROMPT, "$ ", FG, "uptime"),
    (GREEN, "building modern web apps", MUTED, " — always online"),
]

term = []
term.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{TERM_W}" height="{TERM_H}" '
    f'viewBox="0 0 {TERM_W} {TERM_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
)
term.append(f'<defs><linearGradient id="tg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="#38BDF8"/><stop offset="100%" stop-color="#7EE787"/>'
            f'</linearGradient></defs>')
term.append(f'<rect width="{TERM_W}" height="{TERM_H}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')
term.append(f'<path d="M0 12 A12 12 0 0 1 12 0 H{TERM_W - 12} A12 12 0 0 1 {TERM_W} 12 V44 H0 Z" fill="#21262D"/>')
for color, cx in DOTS:
    term.append(f'<circle cx="{cx}" cy="22" r="7" fill="{color}"/>')
term.append(f'<text x="{TERM_W // 2}" y="27" fill="{MUTED}" font-size="13" text-anchor="middle">abdullah@portfolio — zsh</text>')

y = 78
step = 30
for idx, (prompt_color, prompt, text_color, text) in enumerate(lines):
    x = 24
    term.append(f'<text x="{x}" y="{y}" fill="{prompt_color}" font-size="15" font-weight="700">{html.escape(prompt)}</text>')
    x += len(prompt) * 9.1
    if text:
        safe = html.escape(text)
        term.append(f'<text x="{x:.0f}" y="{y}" fill="{text_color}" font-size="15">{safe}</text>')
        x += len(text) * 9.1
    if idx == len(lines) - 1:
        term.append(
            f'<rect x="{x + 6:.0f}" y="{y - 13}" width="9" height="17" fill="{ACCENT}">'
            f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>'
        )
    y += step

term.append('</svg>')
with open(os.path.join(OUT, "terminal.svg"), "w", encoding="utf-8") as f:
    f.write("".join(term))

# ------------------------------------------------------------ skill bars
skills = [
    ("TypeScript", 92, "#3178C6"),
    ("JavaScript", 90, "#F7DF1E"),
    ("React / Next.js", 88, "#61DAFB"),
    ("Node.js / Express", 85, "#339933"),
    ("Python", 78, "#3776AB"),
    ("PostgreSQL / MongoDB", 80, "#4169E1"),
    ("Docker / DevOps", 72, "#2496ED"),
]

BAR_X = 250
BAR_W = 560
ROW_H = 52
PAD_TOP = 28
W = 940
H = PAD_TOP * 2 + ROW_H * len(skills) - 14

sk = []
sk.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
)
sk.append('<defs>')
for i, (_, _, c) in enumerate(skills):
    sk.append(
        f'<linearGradient id="g{i}" gradientUnits="userSpaceOnUse" '
        f'x1="{BAR_X}" y1="0" x2="{BAR_X + BAR_W}" y2="0">'
        f'<stop offset="0%" stop-color="{c}" stop-opacity="0.45"/>'
        f'<stop offset="65%" stop-color="{c}" stop-opacity="0.9"/>'
        f'<stop offset="100%" stop-color="{c}"/></linearGradient>'
    )
sk.append('</defs>')
sk.append(f'<rect width="{W}" height="{H}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')

for i, (name, pct, color) in enumerate(skills):
    cy = PAD_TOP + i * ROW_H + 16
    bw = BAR_W * pct / 100
    sk.append(f'<text x="28" y="{cy + 5}" fill="{FG}" font-size="15" font-weight="600">{html.escape(name)}</text>')
    sk.append(f'<rect x="{BAR_X}" y="{cy - 8}" width="{BAR_W}" height="16" rx="8" fill="#0D1117" stroke="{BORDER}"/>')
    sk.append(
        f'<rect x="{BAR_X}" y="{cy - 8}" width="{bw:.0f}" height="16" rx="8" fill="url(#g{i})">'
        f'<animate attributeName="width" from="0" to="{bw:.0f}" dur="1.4s" '
        f'begin="{0.15 * i:.2f}s" fill="freeze" calcMode="spline" '
        f'keySplines="0.16 1 0.3 1" keyTimes="0;1"/></rect>'
    )
    sk.append(f'<text x="{BAR_X + BAR_W + 18}" y="{cy + 5}" fill="{color}" font-size="14" font-weight="700">{pct}%</text>')
    # tick marks
    for t in (25, 50, 75):
        tx = BAR_X + BAR_W * t / 100
        sk.append(f'<line x1="{tx:.0f}" y1="{cy - 6}" x2="{tx:.0f}" y2="{cy + 6}" stroke="{BORDER}" stroke-width="1"/>')

sk.append('</svg>')
with open(os.path.join(OUT, "skills.svg"), "w", encoding="utf-8") as f:
    f.write("".join(sk))

# ---------------------------------------------------------------- setup
# Edit these values with your real gear, then re-run this script.
setup = [
    ("Machine", "Your laptop model here", "#38BDF8"),
    ("OS", "Your OS / distro here", "#3FB950"),
    ("Editor", "Your editor here", "#D29922"),
    ("Terminal", "Your terminal + shell here", "#BC8CFF"),
    ("Keyboard", "Your keyboard here", "#F85149"),
    ("Mouse / Trackpad", "Your mouse here", "#FF7B72"),
    ("Display", "Your monitor here", "#79C0FF"),
    ("Coffee", "Your fuel of choice here", "#A5D6FF"),
]

S_W = 940
S_ROW = 46
S_TOP = 66
S_H = S_TOP + S_ROW * len(setup) + 24

su = []
su.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{S_W}" height="{S_H}" '
    f'viewBox="0 0 {S_W} {S_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
)
su.append(f'<rect width="{S_W}" height="{S_H}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')
su.append(f'<path d="M0 12 A12 12 0 0 1 12 0 H{S_W - 12} A12 12 0 0 1 {S_W} 12 V44 H0 Z" fill="#21262D"/>')
for color, cx in DOTS:
    su.append(f'<circle cx="{cx}" cy="22" r="7" fill="{color}"/>')
su.append(
    f'<text x="{S_W // 2}" y="27" fill="{MUTED}" font-size="13" text-anchor="middle">'
    f'~/setup — cat rig.json</text>'
)

for i, (label, value, color) in enumerate(setup):
    cy = S_TOP + i * S_ROW
    su.append(f'<circle cx="30" cy="{cy - 5}" r="5" fill="{color}"/>')
    su.append(
        f'<text x="52" y="{cy}" fill="{FG}" font-size="15" font-weight="600">'
        f'{html.escape(label)}</text>'
    )
    su.append(
        f'<text x="300" y="{cy}" fill="{color}" font-size="15">{html.escape(value)}</text>'
    )
    if i < len(setup) - 1:
        su.append(
            f'<line x1="30" y1="{cy + 16}" x2="{S_W - 30}" y2="{cy + 16}" '
            f'stroke="{BORDER}" stroke-width="1" stroke-dasharray="3 5"/>'
        )

su.append('</svg>')
with open(os.path.join(OUT, "setup.svg"), "w", encoding="utf-8") as f:
    f.write("".join(su))

print("wrote", sorted(os.listdir(OUT)))
