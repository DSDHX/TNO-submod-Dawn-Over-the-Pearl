#!/usr/bin/env python3
"""Validate TNO-style teal-filtered DOP texticons against their portraits and template."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image

TNO_OVERLAY_RGB = np.asarray([89, 199, 194], dtype=np.int32)
SOURCE_WEIGHT = 4
OVERLAY_WEIGHT = 1
TOTAL_WEIGHT = SOURCE_WEIGHT + OVERLAY_WEIGHT
HEADER_SIZE = 128
CANVAS_WIDTH = 170
CANVAS_HEIGHT = 224
PORTRAIT_X = 7
PORTRAIT_Y = 7
PORTRAIT_WIDTH = 156
PORTRAIT_HEIGHT = 210


def read_dds(path: Path) -> tuple[dict[str, int], np.ndarray, bytes]:
    """Read the uncompressed 32-bit BGRA DDS format used by TNO texticons."""
    raw = path.read_bytes()
    if len(raw) < HEADER_SIZE or raw[:4] != b"DDS ":
        raise RuntimeError(f"Not a DDS file: {path}")

    height, width = struct.unpack_from("<II", raw, 12)
    bits_per_pixel = struct.unpack_from("<I", raw, 88)[0]
    expected_size = HEADER_SIZE + (width * height * 4)
    if bits_per_pixel != 32 or len(raw) != expected_size:
        raise RuntimeError(
            f"Unexpected DDS format for {path}: "
            f"{width}x{height}, {bits_per_pixel}bpp, {len(raw)} bytes"
        )

    bgra = np.frombuffer(raw, dtype=np.uint8, offset=HEADER_SIZE).reshape(height, width, 4)
    rgba = bgra[..., [2, 1, 0, 3]].copy()
    return {
        "width": width,
        "height": height,
        "bits_per_pixel": bits_per_pixel,
    }, rgba, raw


def verify(template_path: Path, portrait_path: Path, texticon_path: Path, preview_dir: Path) -> dict[str, object]:
    template_header, template_rgba, template_raw = read_dds(template_path)
    header, rgba, raw = read_dds(texticon_path)
    portrait = np.asarray(Image.open(portrait_path).convert("RGBA"), dtype=np.uint8)
    if portrait.shape != (PORTRAIT_HEIGHT, PORTRAIT_WIDTH, 4):
        raise RuntimeError(f"Unexpected portrait shape for {portrait_path}: {portrait.shape}")

    expected = portrait.copy()
    # TNO's original Guangdong texticons use an exact 80/20 normal blend:
    # source portrait + RGB(89, 199, 194), rounded to the nearest integer.
    blended = (
        portrait[..., :3].astype(np.int32) * SOURCE_WEIGHT
        + TNO_OVERLAY_RGB * OVERLAY_WEIGHT
    )
    expected[..., :3] = ((blended + TOTAL_WEIGHT // 2) // TOTAL_WEIGHT).astype(np.uint8)
    inner = rgba[
        PORTRAIT_Y : PORTRAIT_Y + PORTRAIT_HEIGHT,
        PORTRAIT_X : PORTRAIT_X + PORTRAIT_WIDTH,
    ]

    border_mask = np.ones((CANVAS_HEIGHT, CANVAS_WIDTH), dtype=bool)
    border_mask[
        PORTRAIT_Y : PORTRAIT_Y + PORTRAIT_HEIGHT,
        PORTRAIT_X : PORTRAIT_X + PORTRAIT_WIDTH,
    ] = False
    header_matches = raw[:HEADER_SIZE] == template_raw[:HEADER_SIZE]
    border_matches = bool(np.array_equal(rgba[border_mask], template_rgba[border_mask]))
    inner_matches = bool(np.array_equal(inner, expected))
    actual_delta = inner[..., :3].astype(np.int16) - portrait[..., :3].astype(np.int16)

    preview_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba).save(preview_dir / f"{texticon_path.stem}.png")
    valid = bool(
        header == template_header
        and header_matches
        and border_matches
        and inner_matches
        and header["width"] == CANVAS_WIDTH
        and header["height"] == CANVAS_HEIGHT
    )
    return {
        "texticon": str(texticon_path),
        "portrait": str(portrait_path),
        "bytes": len(raw),
        "header": header,
        "header_matches_template": header_matches,
        "border_matches_template": border_matches,
        "inner_matches_tno_teal_overlay_portrait": inner_matches,
        "source_weight": SOURCE_WEIGHT,
        "overlay_weight": OVERLAY_WEIGHT,
        "overlay_rgb": TNO_OVERLAY_RGB.tolist(),
        "actual_mean_delta_rgb": np.round(actual_delta.mean(axis=(0, 1)), 3).tolist(),
        "alpha_min": int(rgba[..., 3].min()),
        "alpha_max": int(rgba[..., 3].max()),
        "valid": valid,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--portrait-dir", required=True, type=Path)
    parser.add_argument("--texticon-dir", required=True, type=Path)
    parser.add_argument("--preview-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    names = ["Yeung_Kwong", "Yamashita_Toshihiko", "Fok_Ying_Tung", "Niwa_Uichiro"]
    results = [
        verify(
            args.template,
            args.portrait_dir / f"DOP_{name}.png",
            args.texticon_dir / f"DOP_{name}_texticon.dds",
            args.preview_dir,
        )
        for name in names
    ]
    text = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if not all(result["valid"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
