#!/usr/bin/env python3
"""Render a captured terminal log as a PNG screenshot (for lab reports)."""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render(log_path: Path, out_path: Path, title: str, width: int = 1100) -> None:
    raw = log_path.read_text(encoding="utf-8", errors="replace")
    text = ANSI_RE.sub("", raw).replace("\r\n", "\n").replace("\t", "    ")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and not lines[-1]:
        lines.pop()

    font = load_font(15)
    title_font = load_font(18)
    line_height = 21
    padding = 22
    header = 46

    dummy = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(dummy)
    max_width = max((draw.textlength(line, font=font) for line in lines), default=800)
    img_width = max(width, int(max_width) + padding * 2)
    img_height = header + padding * 2 + line_height * max(len(lines), 1)

    img = Image.new("RGB", (img_width, img_height), "#0b1020")
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, img_width, header], fill="#161b33")
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        cx = 22 + i * 24
        draw.ellipse([cx - 7, header // 2 - 7, cx + 7, header // 2 + 7], fill=color)
    draw.text((104, 13), title, font=title_font, fill="#e6e9f5")

    y = header + padding
    for line in lines:
        color = "#d7dceb"
        if line.startswith("==="):
            color = "#7ee787"
        elif line.startswith(">") or line.startswith("✔"):
            color = "#79c0ff"
        elif "true" in line.lower() and "false" not in line.lower():
            color = "#7ee787"
        elif "false" in line.lower():
            color = "#ff7b72"
        draw.text((padding, y), line, font=font, fill=color)
        y += line_height

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"wrote {out_path} ({img_width}x{img_height})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("log")
    parser.add_argument("out")
    parser.add_argument("--title", default="Terminal")
    parser.add_argument("--width", type=int, default=1100)
    args = parser.parse_args()
    render(Path(args.log), Path(args.out), args.title, args.width)
