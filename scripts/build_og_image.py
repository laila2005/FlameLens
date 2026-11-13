#!/usr/bin/env python3
"""Build the social preview image (frontend/dist/og-image.png, 1200x630) and the touch icon from frontend/dist/logo.png.

Run from the repo root:  python scripts/build_og_image.py   (needs Pillow)
The run and investigation counts are read from data/curated/runs.csv, never typed by hand.
"""
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "frontend" / "dist"
FONTS = Path("C:/Windows/Fonts")


def font(name, size):
    for candidate in (FONTS / name, Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def flame(img, cx, cy, r):
    """Round microgravity flame: soft glow, orange body, pale core, dashed cyan ring."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((cx - r * 1.5, cy - r * 1.5, cx + r * 1.5, cy + r * 1.5), fill=(255, 138, 36, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(r * 0.45)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 138, 36, 255))
    d.ellipse((cx - r * 0.55, cy - r * 0.45, cx + r * 0.55, cy + r * 0.65), fill=(255, 233, 168, 255))
    for a in range(0, 360, 12):
        d.arc((cx - r * 1.25, cy - r * 1.25, cx + r * 1.25, cy + r * 1.25), a, a + 6, fill=(92, 214, 255, 255), width=max(2, r // 22))


def main():
    with open(ROOT / "data" / "curated" / "runs.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    n_runs, n_inv = len(rows), len({r["psi_id"] for r in rows})

    img = Image.new("RGBA", (1200, 630), (10, 14, 34, 255))
    logo = Image.open(OUT / "logo.png").convert("RGBA")  # round crop of the team's FlameLens illustration
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((215 - 190, 315 - 190, 215 + 190, 315 + 190), fill=(255, 120, 30, 110))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    big = logo.resize((300, 300), Image.LANCZOS)
    img.alpha_composite(big, (215 - 150, 315 - 150))
    d = ImageDraw.Draw(img)
    d.text((400, 150), "FlameLens", font=font("segoeuib.ttf", 112), fill=(234, 237, 250))
    d.text((404, 292), "Is your habitat design backed by", font=font("seguisb.ttf", 44), fill=(154, 163, 199))
    d.text((404, 348), "NASA fire experiments?", font=font("seguisb.ttf", 44), fill=(154, 163, 199))
    d.text((404, 440), f"{n_runs:,} real NASA PSI runs  ·  {n_inv} investigations", font=font("seguisb.ttf", 36), fill=(92, 214, 255))
    d.text((404, 520), "Team AstroSpark  ·  NASA Space Apps 2026", font=font("segoeui.ttf", 28), fill=(154, 163, 199))
    img.convert("RGB").save(OUT / "og-image.png", optimize=True)

    icon = Image.new("RGBA", (180, 180), (10, 14, 34, 255))
    small = logo.resize((164, 164), Image.LANCZOS)
    icon.alpha_composite(small, (8, 8))
    icon.convert("RGB").save(OUT / "apple-touch-icon.png", optimize=True)
    print(f"wrote og-image.png and apple-touch-icon.png ({n_runs:,} runs, {n_inv} investigations)")


if __name__ == "__main__":
    main()
