#!/usr/bin/env python3
"""Fetch GitHub metrics and render themed SVG cards for the profile README.

Usage:
    GITHUB_TOKEN=... python3 tools/generate_github_cards.py

Writes assets/contributions.svg and assets/dashboard.svg
"""
import datetime
import json
import math
import os
import sys
import urllib.request

USER = os.environ.get("GITHUB_USER", "abdullahasim1")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

BG = "#0D1117"
PANEL = "#161B22"
HEAD = "#21262D"
BORDER = "#30363D"
FG = "#C9D1D9"
MUTED = "#8B949E"
ACCENT = "#38BDF8"
GREEN = "#3FB950"
YELLOW = "#D29922"
RED = "#F85149"
PURPLE = "#BC8CFF"
BLUE = "#79C0FF"

DOTS = [(RED, 24), (YELLOW, 48), (GREEN, 72)]

# 5-step scale: empty -> bright accent
SCALE = ["#161B22", "#0E3A52", "#14607F", "#1E88A8", "#38BDF8"]


def gh_graphql(query: str, variables=None) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN not set")
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "readme-cards",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.load(r)
    if payload.get("errors"):
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
      nodes { stargazerCount forkCount }
    }
    followers { totalCount }
  }
}
"""


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def header(width: int, title: str, right: str = "") -> list:
    p = [
        f'<rect width="{width}" height="H_H" rx="12" fill="{PANEL}" stroke="{BORDER}"/>',
    ]
    return p


def stats_from(cal: dict) -> dict:
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    by_date = {d["date"]: d["contributionCount"] for d in days}

    today = datetime.date.today()

    # current streak — today may still be empty, so allow skipping it once
    cur, cursor, skipped = 0, today, False
    while True:
        c = by_date.get(cursor.isoformat(), 0)
        if c > 0:
            cur += 1
            cursor -= datetime.timedelta(days=1)
        elif cursor == today and not skipped:
            skipped = True
            cursor -= datetime.timedelta(days=1)
        else:
            break

    best = run = 0
    for d in days:
        if d["contributionCount"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0

    active = [d["contributionCount"] for d in days if d["contributionCount"] > 0]
    peak = max(days, key=lambda d: d["contributionCount"])
    return {
        "days": days,
        "total": cal["totalContributions"],
        "current_streak": cur,
        "longest_streak": best,
        "active_days": len(active),
        "avg_active": round(cal["totalContributions"] / max(len(active), 1), 1),
        "peak": peak["contributionCount"],
        "peak_date": peak["date"],
    }


def title_bar(width: int, height: int, title: str, right: str = "") -> str:
    """macOS-style window chrome, shared by every card."""
    o = [
        f'<path d="M0 12 A12 12 0 0 1 12 0 H{width - 12} A12 12 0 0 1 {width} 12 V44 H0 Z" fill="{HEAD}"/>',
    ]
    for color, cx in DOTS:
        o.append(f'<circle cx="{cx}" cy="22" r="7" fill="{color}"/>')
    o.append(
        f'<text x="{width // 2}" y="27" fill="{MUTED}" font-size="13" '
        f'text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">'
        f'{esc(title)}</text>'
    )
    if right:
        o.append(
            f'<text x="{width - 24}" y="27" fill="{ACCENT}" font-size="13" font-weight="700" '
            f'text-anchor="end" font-family="ui-monospace,Menlo,Consolas,monospace">{esc(right)}</text>'
        )
    return "".join(o)


def contribution_card(stats: dict) -> str:
    days = stats["days"]
    W = 940
    CELL, GAP = 13, 3
    PITCH = CELL + GAP
    X0 = 52
    TITLE_H = 44
    GRID_TOP = 88
    LEG_Y = 226
    HEIGHT = 322

    weeks = []
    for d in days:
        dt = datetime.date.fromisoformat(d["date"])
        if not weeks or dt.weekday() == 6:
            weeks.append([])
        weeks[-1].append(d)
    # left-align if the first week is partial
    if weeks and len(weeks[0]) < 7:
        weeks[0] = [None] * (7 - len(weeks[0])) + weeks[0]

    grid_w = len(weeks) * PITCH
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HEIGHT}" '
        f'viewBox="0 0 {W} {HEIGHT}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect width="{W}" height="{HEIGHT}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>',
        title_bar(W, TITLE_H, "~/github — contributions", f'{stats["total"]} total'),
    ]

    # legend — own row under the grid so it never collides with month labels
    lx = W - 24 - 190
    o.append(f'<text x="{lx}" y="{LEG_Y + 11}" fill="{MUTED}" font-size="11">less</text>')
    sx = lx + 34
    for i, c in enumerate(SCALE):
        o.append(
            f'<rect x="{sx + i * 20}" y="{LEG_Y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{c}" stroke="{BORDER}" stroke-width="0.5"/>'
        )
    o.append(
        f'<text x="{sx + len(SCALE) * 20 + 4}" y="{LEG_Y + 11}" fill="{MUTED}" font-size="11">more</text>'
    )

    # month labels
    last_month = None
    for wi, week in enumerate(weeks):
        first = next((d for d in week if d), None)
        if not first:
            continue
        dt = datetime.date.fromisoformat(first["date"])
        if dt.month != last_month:
            last_month = dt.month
            x = X0 + wi * PITCH
            o.append(
                f'<text x="{x}" y="{GRID_TOP - 12}" fill="{MUTED}" font-size="12">'
                f'{dt.strftime("%b")}</text>'
            )

    # weekday labels
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        o.append(
            f'<text x="{X0 - 12}" y="{GRID_TOP + row * PITCH + CELL - 3}" fill="{MUTED}" '
            f'font-size="11" text-anchor="end">{label}</text>'
        )

    # cells — 4 intensity steps scaled against the busiest day
    peak = max(stats["peak"], 1)
    for wi, week in enumerate(weeks):
        for di, d in enumerate(week):
            if d is None:
                continue
            count = d["contributionCount"]
            if count <= 0:
                idx = 0
            elif count >= peak * 0.5:
                idx = 4
            elif count >= peak * 0.15:
                idx = 3
            elif count >= peak * 0.05:
                idx = 2
            else:
                idx = 1
            x = X0 + wi * PITCH
            y = GRID_TOP + di * PITCH
            tip = f'{d["date"]}: {count} contribution{"s" if count != 1 else ""}'
            o.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                f'fill="{SCALE[idx]}" stroke="{BORDER}" stroke-width="0.5"><title>{esc(tip)}</title></rect>'
            )

    # stats strip
    items = [
        ("LONGEST STREAK", f'{stats["longest_streak"]}d', ACCENT),
        ("CURRENT STREAK", f'{stats["current_streak"]}d', GREEN),
        ("BEST DAY", str(stats["peak"]), YELLOW),
        ("ACTIVE DAYS", str(stats["active_days"]), PURPLE),
        ("AVG / ACTIVE DAY", str(stats["avg_active"]), BLUE),
    ]
    sy = 262
    col_w = (W - 56) // len(items)
    for i, (label, value, color) in enumerate(items):
        cx = 28 + i * col_w
        o.append(f'<text x="{cx}" y="{sy}" fill="{MUTED}" font-size="11" letter-spacing="1">{esc(label)}</text>')
        o.append(
            f'<text x="{cx}" y="{sy + 30}" fill="{color}" font-size="26" font-weight="700">{esc(value)}</text>'
        )
        if i:
            o.append(
                f'<line x1="{cx - 16}" y1="{sy - 16}" x2="{cx - 16}" y2="{sy + 34}" '
                f'stroke="{BORDER}" stroke-width="1"/>'
            )

    o.append("</svg>")
    return "".join(o)


def dashboard_card(data: dict) -> str:
    W = 940
    TILE_W, TILE_H, GAP = 215, 96, 14
    COLS = 4
    TITLE_H = 44
    TOP = 66
    rows = math.ceil(len(data) / COLS)
    HEIGHT = TOP + rows * TILE_H + (rows - 1) * GAP + 24

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HEIGHT}" '
        f'viewBox="0 0 {W} {HEIGHT}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect width="{W}" height="{HEIGHT}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>',
        title_bar(W, TITLE_H, "~/github — dashboard", f'updated {datetime.date.today().isoformat()}'),
    ]

    for i, (label, value, sub, color) in enumerate(data):
        col, row = i % COLS, i // COLS
        x = 20 + col * (TILE_W + GAP)
        y = TOP + row * (TILE_H + GAP)
        o.append(
            f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="10" '
            f'fill="{BG}" stroke="{BORDER}"/>'
        )
        o.append(f'<rect x="{x}" y="{y}" width="4" height="{TILE_H}" rx="2" fill="{color}"/>')
        o.append(
            f'<text x="{x + 20}" y="{y + 46}" fill="{color}" font-size="30" font-weight="700">'
            f'{esc(value)}</text>'
        )
        o.append(
            f'<text x="{x + 20}" y="{y + 70}" fill="{FG}" font-size="13" font-weight="600">'
            f'{esc(label)}</text>'
        )
        o.append(
            f'<text x="{x + 20}" y="{y + 87}" fill="{MUTED}" font-size="11">{esc(sub)}</text>'
        )

    o.append("</svg>")
    return "".join(o)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    data = gh_graphql(QUERY, {"login": USER})["user"]
    cal = data["contributionsCollection"]["contributionCalendar"]
    stats = stats_from(cal)
    repos = data["repositories"]
    stars = sum(n["stargazerCount"] for n in repos["nodes"])
    forks = sum(n["forkCount"] for n in repos["nodes"])

    contrib = contribution_card(stats)
    with open(os.path.join(OUT, "contributions.svg"), "w", encoding="utf-8") as f:
        f.write(contrib)

    tiles = [
        ("Total Contributions", f'{stats["total"]}', "last 12 months", ACCENT),
        ("Commits", f'{data["contributionsCollection"]["totalCommitContributions"]}', "authored this year", GREEN),
        ("Pull Requests", f'{data["contributionsCollection"]["totalPullRequestContributions"]}', "opened this year", PURPLE),
        ("Public Repos", f'{repos["totalCount"]}', "repositories", BLUE),
        ("Longest Streak", f'{stats["longest_streak"]}d', "consecutive days", YELLOW),
        ("Stars Earned", f'{stars}', f"{forks} fork{'s' if forks != 1 else ''}", RED),
        ("Followers", f'{data["followers"]["totalCount"]}', "on GitHub", ACCENT),
        ("Best Day", f'{stats["peak"]}', stats["peak_date"], GREEN),
    ]
    dash = dashboard_card(tiles)
    with open(os.path.join(OUT, "dashboard.svg"), "w", encoding="utf-8") as f:
        f.write(dash)

    meta = {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stats": {k: v for k, v in stats.items() if k != "days"},
        "repos": repos["totalCount"],
        "stars": stars,
    }
    with open(os.path.join(OUT, ".cards-meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("wrote contributions.svg, dashboard.svg")
    print(json.dumps(meta["stats"], indent=2))


if __name__ == "__main__":
    main()
