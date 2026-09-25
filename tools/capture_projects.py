#!/usr/bin/env python3
"""Capture project screenshots for the README featured-projects table.

Usage:
    python3 tools/capture_projects.py [--out assets/screenshots]

Requires playwright browsers (python -m playwright install chromium).
Screenshots are captured dark where the site honours prefers-color-scheme,
at a fixed viewport so the frame in frame_projects.py stays uniform.
"""
import argparse
import pathlib
import sys

PROJECTS = [
    ("fourai", "https://four-ai-dev.vercel.app/"),
    ("devrox", "https://thedevrox.com"),
    ("job", "https://job-recuitment.vercel.app"),
    ("portfolio", "https://abdullah-asim-dev.vercel.app/"),
]
VIEWPORT = {"width": 1280, "height": 800}
SETTLE_MS = 4000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/screenshots")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright not installed")

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
        ctx = browser.new_context(
            viewport=VIEWPORT,
            color_scheme="dark",
            device_scale_factor=1,
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
        )
        for name, url in PROJECTS:
            page = ctx.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception:
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                except Exception as exc:
                    print(f"skip {name}: {exc}")
                    page.close()
                    continue
            page.wait_for_timeout(SETTLE_MS)
            dest = out / f"{name}.png"
            page.screenshot(path=str(dest))
            size = dest.stat().st_size
            print(f"wrote {dest} ({size} bytes)")
            page.close()
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
