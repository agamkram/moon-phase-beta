#!/usr/bin/env python3
"""Generate The Moon home-screen icons."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MOON_TEXTURE = ROOT / "moon.jpg"


def sky_pixel(x: int, y: int, size: int) -> tuple[int, int, int]:
    t = min(1.0, math.hypot(x - size * 0.38, y - size * 0.18) / (size * 0.72))
    inner = (18, 26, 47)
    outer = (2, 3, 8)
    return tuple(int(inner[i] + (outer[i] - inner[i]) * t) for i in range(3))


def draw_stars(draw: ImageDraw.ImageDraw, size: int, seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(60):
        x = rng.randint(0, size - 1)
        y = rng.randint(0, size - 1)
        b = rng.randint(120, 255)
        r = rng.choice([0, 0, 1, 2])
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, min(255, b + 24)))


def render_moon(diameter: int, phase: float = 0.48) -> Image.Image:
    texture = Image.open(MOON_TEXTURE).convert("L")
    moon = ImageOps.fit(texture, (diameter, diameter), Image.Resampling.LANCZOS)
    moon_rgb = Image.merge("RGB", (moon, moon, moon))

    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)
    shaded = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    shaded.paste(moon_rgb, (0, 0), mask)

    radius = diameter / 2
    center = diameter / 2
    shadow = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    pixels = shadow.load()
    terminator = 1.0 - phase * 2.0

    for py in range(diameter):
        for px in range(diameter):
            dx = px - center + 0.5
            dy = py - center + 0.5
            if dx * dx + dy * dy > radius * radius:
                continue
            nx = dx / radius
            if nx < terminator:
                t = min(1.0, max(0.0, (terminator - nx) / 0.55))
                pixels[px, py] = (2, 3, 8, int(230 * t))

    return Image.alpha_composite(shaded, shadow)


def build_icon(size: int) -> Image.Image:
    canvas = Image.new("RGB", (size, size))
    pixels = canvas.load()
    for y in range(size):
        for x in range(size):
            pixels[x, y] = sky_pixel(x, y, size)

    draw = ImageDraw.Draw(canvas)
    draw_stars(draw, size, 17)

    moon_size = int(size * 0.56)
    moon = render_moon(moon_size, phase=0.48)
    top_left = ((size - moon_size) // 2, (size - moon_size) // 2)
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.alpha_composite(moon, top_left)

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cx = size // 2
    cy = size // 2
    r = moon_size // 2
    glow_draw.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=(90, 130, 220, 30))
    canvas_rgba = Image.alpha_composite(canvas_rgba, glow.filter(ImageFilter.GaussianBlur(radius=size // 36)))
    return canvas_rgba.convert("RGB")


def save_icons() -> None:
    icon_512 = build_icon(512)
    icon_512.save(ROOT / "icon-512.png", "PNG")
    icon_512.resize((180, 180), Image.Resampling.LANCZOS).save(ROOT / "apple-touch-icon.png", "PNG")
    print(f"Wrote icons in {ROOT}")


if __name__ == "__main__":
    save_icons()