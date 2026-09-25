#!/usr/bin/env python3
"""Build the profile hero card: avatar, name and a rotating typewriter line.

Usage:
    GITHUB_TOKEN=... python3 tools/generate_hero.py

Writes assets/hero.svg
"""
import base64
import io
import json
import os
import urllib.request

USER = os.environ.get("GITHUB_USER", "abdullahasim1")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

PANEL = "#161B22"
HEAD = "#21262D"
BORDER = "#30363D"
MUTED = "#8B949E"
ACCENT = "#38BDF8"
GREEN = "#3FB950"
DOTS = ["#F85149", "#D29922", "#3FB950"]
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "Inter,Segoe UI,Helvetica,Arial,sans-serif"

W = 940
TITLE_H = 44
HEIGHT = 262
AV = 140
AV_X = 44
AV_Y = 86
TX = 216

LINES = [
    "Full-Stack Developer",
    "AI & Automation Enthusiast",
    "Building Modern Web Applications",
    "Open Source Contributor",
]
SLOT = 3.6        # seconds each line owns
TYPE_IN = 1.25    # seconds spent typing it out
HOLD = 1.7        # seconds it stays fully written
TOTAL = SLOT * len(LINES)

TYPE_FONT = 25
CHAR_W = TYPE_FONT * 0.6      # monospace advance width
CURSOR_W = 11
TYPE_Y = AV_Y + 96            # typewriter baseline
CLIP_Y = AV_Y + 70            # clip must cover the typewriter row, not the name
CLIP_H = 40


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def api_get(url: str) -> bytes:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"User-Agent": "readme-hero"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return r.read()


def avatar_b64() -> str:
    uid = json.loads(api_get(f"https://api.github.com/users/{USER}"))["id"]
    raw = api_get(f"https://avatars.githubusercontent.com/u/{uid}?v=4")
    try:
        from PIL import Image
    except ImportError:
        return base64.b64encode(raw).decode()
    im = Image.open(io.BytesIO(raw)).convert("RGB").resize((160, 160), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=86, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def slot_points(i: int) -> list:
    """Timeline points for line i, in seconds, always strictly increasing."""
    start = i * SLOT
    end = start + TYPE_IN + HOLD
    pts = [0.0] if start <= 0 else [0.0, start]
    pts += [start + TYPE_IN, end, min(end + 0.06, TOTAL), TOTAL]
    deduped = []
    for p in pts:
        if not deduped or p > deduped[-1] + 1e-6:
            deduped.append(p)
    return deduped


def keys_for(i: int) -> str:
    return ";".join(f"{p / TOTAL:.4f}" for p in slot_points(i))


def clip_values(i: int) -> str:
    """width: 0 -> full while typing, hold, then snap back to 0."""
    pts = slot_points(i)
    vals = ["0"] * len(pts)
    # pts layout: [0, start?, type_end, hold_end, snap, TOTAL]
    base = 1 if i == 0 else 2
    vals[base] = "9999"       # reaches full width at type_end
    vals[base + 1] = "9999"   # stays full through hold_end
    return ";".join(vals)


def cursor_values(i: int, line: str) -> str:
    end_x = round(TX + len(line) * CHAR_W - CURSOR_W, 1)
    vals = [str(TX)] * len(slot_points(i))
    base = 1 if i == 0 else 2
    vals[base] = str(end_x)
    vals[base + 1] = str(end_x)
    return ";".join(vals)


def build() -> str:
    avatar = avatar_b64()
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HEIGHT}" '
        f'viewBox="0 0 {W} {HEIGHT}">',
        "<defs>",
        '<linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{ACCENT}"/>'
        '<stop offset="55%" stop-color="#7EE787"/>'
        '<stop offset="100%" stop-color="#7EE787" stop-opacity="0.35"/>'
        "</linearGradient>",
        '<linearGradient id="ruleGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{ACCENT}"/>'
        f'<stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>'
        "</linearGradient>",
        f'<clipPath id="avatarClip"><circle cx="{AV_X + AV // 2}" cy="{AV_Y + AV // 2}" '
        f'r="{AV // 2}"/></clipPath>',
    ]
    for i in range(len(LINES)):
        # Base width: line 0 starts fully revealed so the card still reads
        # correctly if a renderer never starts the animation. The remaining
        # lines start hidden and are only brought in by the SMIL timeline.
        base_w = 9999 if i == 0 else 0
        o.append(
            f'<clipPath id="clip{i}"><rect x="{TX}" y="{CLIP_Y}" width="{base_w}" height="{CLIP_H}">'
            f'<animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" '
            f'fill="freeze" values="{clip_values(i)}" keyTimes="{keys_for(i)}"/>'
            f"</rect></clipPath>"
        )
    o.append("</defs>")

    # card + window chrome
    o.append(f'<rect width="{W}" height="{HEIGHT}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')
    o.append(
        f'<path d="M0 12 A12 12 0 0 1 12 0 H{W - 12} A12 12 0 0 1 {W} 12 V{TITLE_H} H0 Z" fill="{HEAD}"/>'
    )
    for i, c in enumerate(DOTS):
        o.append(f'<circle cx="{24 + i * 24}" cy="22" r="7" fill="{c}"/>')
    o.append(
        f'<text x="{W // 2}" y="27" fill="{MUTED}" font-size="13" text-anchor="middle" '
        f'font-family="{MONO}">~/{USER} — whoami</text>'
    )
    o.append(f'<circle cx="{W - 176}" cy="19" r="5" fill="{GREEN}"/>')
    o.append(
        f'<text x="{W - 164}" y="24" fill="{GREEN}" font-size="13" font-weight="700" '
        f'font-family="{MONO}">open to work</text>'
    )

    # avatar
    o.append(
        f'<image href="data:image/jpeg;base64,{avatar}" x="{AV_X}" y="{AV_Y}" width="{AV}" '
        f'height="{AV}" clip-path="url(#avatarClip)" preserveAspectRatio="xMidYMid slice"/>'
    )
    o.append(
        f'<circle cx="{AV_X + AV // 2}" cy="{AV_Y + AV // 2}" r="{AV // 2 - 1}" fill="none" '
        f'stroke="{ACCENT}" stroke-width="3"/>'
    )

    # name + rule
    o.append(
        f'<text x="{TX}" y="{AV_Y + 34}" font-family="{SANS}" font-size="42" font-weight="800" '
        f'fill="url(#nameGrad)" letter-spacing="-0.5">Abdullah Bin Asim</text>'
    )
    o.append(f'<rect x="{TX}" y="{AV_Y + 46}" width="360" height="3" rx="1.5" fill="url(#ruleGrad)"/>')

    # typewriter lines
    for i, line in enumerate(LINES):
        parked = TX if i else round(TX + len(line) * CHAR_W - CURSOR_W, 1)
        o.append(
            f'<g clip-path="url(#clip{i})">'
            f'<text x="{TX}" y="{TYPE_Y}" font-family="{MONO}" font-size="{TYPE_FONT}" '
            f'font-weight="600" fill="{ACCENT}">{esc(line)}</text>'
            f'<rect x="{parked}" y="{TYPE_Y - 20}" width="{CURSOR_W}" height="26" fill="{ACCENT}">'
            f'<animate attributeName="x" dur="{TOTAL}s" repeatCount="indefinite" fill="freeze" '
            f'values="{cursor_values(i, line)}" keyTimes="{keys_for(i)}"/>'
            f"</rect>"
            f"</g>"
        )

    # meta line
    o.append(
        f'<text x="{TX}" y="{AV_Y + 142}" font-family="{MONO}" font-size="15" fill="{MUTED}">'
        f'Lahore, Pakistan  ·  ExpertsCloud  ·  TypeScript / React / Node.js</text>'
    )

    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    svg = build()
    with open(os.path.join(OUT, "hero.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote hero.svg ({len(svg)} bytes)")
