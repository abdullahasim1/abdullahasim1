#!/usr/bin/env python3
"""Wrap a Platane/snk generated SVG in the themed window chrome used by the README.

Usage:
    python3 tools/frame_snake.py dist/github-snake.svg dist/github-snake-dark.svg

Rewrites each file in place so the snake sits inside a titled card.
"""
import os
import re
import sys

PANEL = "#161B22"
HEAD = "#21262D"
BORDER = "#30363D"
MUTED = "#8B949E"
ACCENT = "#38BDF8"
DOTS = ["#F85149", "#D29922", "#3FB950"]

W = 940
TITLE_H = 44
PAD_X = 20
PAD_BOTTOM = 24
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def frame(path: str) -> None:
    src = open(path, encoding="utf-8").read()

    m = re.search(r"<svg[^>]*>", src, re.S)
    if not m:
        sys.exit(f"{path}: no <svg> root found")
    root = m.group(0)

    vb = re.search(r'viewBox="([^"]+)"', root)
    ow = re.search(r'width="([\d.]+)"', root)
    oh = re.search(r'height="([\d.]+)"', root)
    if not vb or not ow or not oh:
        sys.exit(f"{path}: missing viewBox/width/height")

    viewBox = vb.group(1)
    inner_w, inner_h = float(ow.group(1)), float(oh.group(1))
    inner = src[m.end(): src.rindex("</svg>")]

    # Make the snk CSS variables resolve on the nested <svg> rather than :root,
    # so they still work when this file is embedded in a README <img>.
    inner = inner.replace(":root{", "svg.snk{", 1).replace(":root {", "svg.snk{", 1)

    avail_w = W - 2 * PAD_X
    scale = avail_w / inner_w
    draw_w = avail_w
    draw_h = inner_h * scale
    height = TITLE_H + PAD_BOTTOM * 2 + draw_h

    title = "contribution snake"
    dark = "dark" in os.path.basename(path)
    right = "github-dark" if dark else "github"

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height:.0f}" '
        f'viewBox="0 0 {W} {height:.0f}" font-family="{FONT}">',
        f'<rect width="{W}" height="{height:.0f}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>',
        f'<path d="M0 12 A12 12 0 0 1 12 0 H{W - 12} A12 12 0 0 1 {W} 12 V{TITLE_H} H0 Z" fill="{HEAD}"/>',
    ]
    for i, c in enumerate(DOTS):
        o.append(f'<circle cx="{24 + i * 24}" cy="22" r="7" fill="{c}"/>')
    o.append(
        f'<text x="{W // 2}" y="27" fill="{MUTED}" font-size="13" text-anchor="middle">{title}</text>'
    )
    o.append(
        f'<text x="{W - 24}" y="27" fill="{ACCENT}" font-size="13" font-weight="700" '
        f'text-anchor="end">{right}</text>'
    )

    o.append(
        f'<svg x="{PAD_X}" y="{TITLE_H + PAD_BOTTOM}" width="{draw_w}" '
        f'height="{draw_h:.2f}" viewBox="{viewBox}" class="snk" '
        f'preserveAspectRatio="xMidYMid meet">'
    )
    o.append(inner)
    o.append("</svg></svg>")

    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(o))
    print(f"framed {path} -> {W}x{height:.0f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        frame(p)
