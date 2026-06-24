#!/usr/bin/env python3
"""Export the Component Compass LinkedIn carousel slides to PNGs.

Tailored to this repo's deck: each slide is a 1080x1350 div with the
background #F5F2EB, stacked inside a dark #11121C wrapper. The script:

  1. Reads the source HTML and injects a <base> so relative assets resolve.
  2. Flattens the layout (drops the wrapper bg, gaps, shadows, radius) so the
     slides stack as clean 1080x1350 blocks.
  3. Renders the whole thing to one tall image with headless Chrome at 2x.
  4. Slices that image into one PNG per slide at exact pixel boundaries.

Usage:
    python3 .claude/skills/export-slides/export.py
    CHROME="/path/to/chrome" python3 .../export.py   # override Chrome binary
"""
import os
import pathlib
import subprocess
import sys

from PIL import Image

# Repo root is four levels up: .claude/skills/export-slides/export.py
ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / "CC LinkedIn Carousel v2.html"
TMP = ROOT / "tmp"
OUT = ROOT / "exports"

SLIDE_W, SLIDE_H = 1080, 1350      # LinkedIn 4:5 carousel spec
SCALE = 2                          # 2x for crisp retina PNGs

WRAPPER = '<div style="background:#11121C; min-height:100vh;'
SLIDE = '<div style="width:1080px; height:1350px; background:#F5F2EB; border-radius:8px;'

CHROME = os.environ.get(
    "CHROME",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)


def build_flat_html() -> tuple[pathlib.Path, int]:
    html = SRC.read_text(encoding="utf-8")
    n = html.count(SLIDE)
    if n == 0:
        sys.exit(f"No slides found in {SRC.name} (expected divs starting '{SLIDE}').")

    base = f'<base href="{ROOT.as_uri()}/">'
    html = html.replace("<head>", "<head>\n" + base, 1)
    html = html.replace(WRAPPER, WRAPPER.replace('style="', 'class="pdf-wrap" style="'), 1)
    html = html.replace(SLIDE, SLIDE.replace('style="', 'class="pdf-slide" style="'))

    flat_css = """
<style>
  html, body { margin:0 !important; padding:0 !important; background:#fff !important; }
  .pdf-wrap { background:#fff !important; padding:0 !important; gap:0 !important;
              display:block !important; min-height:0 !important; width:1080px; }
  .pdf-slide { border-radius:0 !important; box-shadow:none !important; margin:0 !important; }
</style>
"""
    html = html.replace("</head>", flat_css + "</head>", 1)

    TMP.mkdir(exist_ok=True)
    flat = TMP / "carousel-flat.html"
    flat.write_text(html, encoding="utf-8")
    return flat, n


def render(flat: pathlib.Path, n: int) -> pathlib.Path:
    shot = TMP / "flat@2x.png"
    total_h = SLIDE_H * n
    subprocess.run(
        [
            CHROME,
            "--headless=new", "--disable-gpu", "--hide-scrollbars",
            f"--force-device-scale-factor={SCALE}",
            f"--window-size={SLIDE_W},{total_h}",
            "--virtual-time-budget=12000",
            "--run-all-compositor-stages-before-draw",
            f"--screenshot={shot}",
            str(flat),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not shot.exists():
        sys.exit("Chrome did not produce a screenshot. Check the CHROME path.")
    return shot


def slice_into_pngs(shot: pathlib.Path, n: int) -> None:
    OUT.mkdir(exist_ok=True)
    im = Image.open(shot).convert("RGB")
    page_h = im.height / n
    for i in range(n):
        crop = im.crop((0, round(i * page_h), im.width, round((i + 1) * page_h)))
        path = OUT / f"slide-{i + 1}.png"
        crop.save(path, optimize=True)
        print(f"  {path.relative_to(ROOT)}  {crop.size}")


def main() -> None:
    if not SRC.exists():
        sys.exit(f"Source not found: {SRC}")
    flat, n = build_flat_html()
    print(f"Found {n} slides. Rendering at {SCALE}x...")
    shot = render(flat, n)
    slice_into_pngs(shot, n)
    # Clean up intermediates.
    flat.unlink(missing_ok=True)
    shot.unlink(missing_ok=True)
    print(f"Done -> {OUT.relative_to(ROOT)}/ ({n} PNGs at {SLIDE_W*SCALE}x{SLIDE_H*SCALE})")


if __name__ == "__main__":
    main()
