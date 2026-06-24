---
name: export-slides
description: Export this repo's Component Compass LinkedIn carousel ("CC LinkedIn Carousel v2.html") to one PNG per slide. Use when the user wants to export the carousel/slides as PNGs or images, regenerate the slide exports, or produce shareable slide images.
---

# Export carousel slides to PNGs

Exports each slide of `CC LinkedIn Carousel v2.html` as its own PNG into `exports/`.

## How it works

Rather than relying on Chrome's print/pagination engine (which infers page
boundaries and reinterprets px→pt), this renders the deck as one tall image and
slices it at exact pixel lines — deterministic and pixel-perfect to LinkedIn's
1080×1350 (4:5) spec.

1. Inject a `<base href>` so relative assets (`uploads/...`, the logo) resolve.
2. Flatten the layout: drop the dark `#11121C` wrapper background, gaps,
   shadows, and rounded corners so slides stack as clean `1080×1350` blocks.
3. Render to one tall PNG with headless Chrome at **2×** (`force-device-scale-factor=2`).
4. Slice into `N` images of `2160×2700` with Pillow at exact pixel boundaries.

## Usage

```bash
python3 .claude/skills/export-slides/export.py
```

Output lands in `exports/slide-1.png … slide-N.png` (gitignored; local only).
The slide count is detected automatically from the source HTML.

## Requirements

- Google Chrome (default macOS path). Override with `CHROME="/path/to/chrome"`.
- Python with Pillow (`python3 -c "import PIL"`).

## Notes / gotchas

- This is **tailored to this deck**: it tags slides by matching the exact style
  string `width:1080px; height:1350px; background:#F5F2EB; border-radius:8px;`
  and the wrapper `background:#11121C; min-height:100vh;`. If the slide styling
  changes, update `SLIDE` / `WRAPPER` (and `SLIDE_W`/`SLIDE_H`) in `export.py`.
- For a vector **PDF** instead, use Chrome's `--print-to-pdf` on a print-flavored
  copy (text stays sharp, but boundaries are engine-inferred). PNGs are the more
  deterministic route for fixed-size slides.
