#!/usr/bin/env python3
"""Build labeled or hidden TNO portrait contact sheets for visual QA."""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover - environment guidance
    raise SystemExit("Install Pillow before running this script") from exc


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = value.lower().split("x", 1)
        return int(width), int(height)
    except (ValueError, AttributeError) as exc:
        raise argparse.ArgumentTypeError("Size must look like 156x210") from exc


def parse_color(value: str) -> tuple[int, int, int]:
    text = value.strip().lstrip("#")
    if len(text) != 6:
        raise argparse.ArgumentTypeError("Color must be a six-digit hex value")
    try:
        return tuple(int(text[index : index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Color must be a six-digit hex value") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tile-size", type=parse_size, default=(156, 210))
    parser.add_argument("--columns", type=int)
    parser.add_argument("--zoom", type=int, default=1)
    parser.add_argument("--hide-labels", action="store_true")
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--background", type=parse_color, default=(24, 24, 24))
    args = parser.parse_args()

    items = list(args.paths)
    if args.shuffle:
        random.Random(args.seed).shuffle(items)
    columns = args.columns or len(items)
    if columns < 1 or args.zoom < 1:
        raise SystemExit("--columns and --zoom must be positive")

    tile_w, tile_h = args.tile_size
    label_h = 0 if args.hide_labels else 20
    rows = math.ceil(len(items) / columns)
    board = Image.new("RGB", (tile_w * columns, (tile_h + label_h) * rows), args.background)
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default()

    for index, path in enumerate(items):
        row, column = divmod(index, columns)
        x = column * tile_w
        y = row * (tile_h + label_h)
        image = Image.open(path).convert("RGB")
        fitted = ImageOps.contain(image, (tile_w, tile_h), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (tile_w, tile_h), args.background)
        tile.paste(fitted, ((tile_w - fitted.width) // 2, (tile_h - fitted.height) // 2))
        board.paste(tile, (x, y))
        if not args.hide_labels:
            label = path.stem
            draw.text((x + 3, y + tile_h + 3), label[:26], fill=(235, 235, 235), font=font)

    if args.zoom != 1:
        board = board.resize((board.width * args.zoom, board.height * args.zoom), Image.Resampling.NEAREST)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    board.save(args.output)
    print(f"saved={args.output} size={board.width}x{board.height} items={len(items)}")


if __name__ == "__main__":
    main()
