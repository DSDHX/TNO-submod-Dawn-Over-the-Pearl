#!/usr/bin/env python3
"""Report reproducible portrait metrics without modifying the input files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def srgb_to_lab_l(rgb: np.ndarray) -> np.ndarray:
    value = rgb.astype(np.float64) / 255.0
    linear = np.where(value <= 0.04045, value / 12.92, ((value + 0.055) / 1.055) ** 2.4)
    xyz_y = linear[..., 0] * 0.2126729 + linear[..., 1] * 0.7151522 + linear[..., 2] * 0.0721750
    epsilon = 216 / 24389
    kappa = 24389 / 27
    f_y = np.where(xyz_y > epsilon, np.cbrt(xyz_y), (kappa * xyz_y + 16) / 116)
    return 116 * f_y - 16


def analyze(path: Path) -> dict[str, float | int | str]:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float64)
    alpha = rgba[..., 3:4] / 255.0
    rgb = rgba[..., :3] * alpha + 255.0 * (1.0 - alpha)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    channel_max = rgb.max(axis=2)
    channel_min = rgb.min(axis=2)
    saturation = np.divide(
        channel_max - channel_min,
        channel_max,
        out=np.zeros_like(channel_max),
        where=channel_max > 0,
    )

    h, w = luma.shape
    corner_h = max(1, round(h * 0.12))
    corner_w = max(1, round(w * 0.12))
    top_corners = np.concatenate(
        [
            luma[:corner_h, :corner_w].ravel(),
            luma[:corner_h, -corner_w:].ravel(),
        ]
    )

    x0, x1 = round(w * 0.22), round(w * 0.78)
    y0, y1 = round(h * 0.18), round(h * 0.69)
    face = rgb[y0:y1, x0:x1]
    r, g, b = face[..., 0], face[..., 1], face[..., 2]
    skin_mask = (
        (r > 65)
        & (g > 45)
        & (b > 35)
        & (r > g)
        & (g > b)
        & ((r - b) > 10)
        & ((r - g) < 75)
    )
    skin = face[skin_mask]

    padded = np.pad(luma, 1, mode="edge")
    laplacian = (
        padded[1:-1, :-2]
        + padded[1:-1, 2:]
        + padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        - 4 * luma
    )

    result: dict[str, float | int | str] = {
        "file": str(path),
        "width": w,
        "height": h,
        "luma_mean": round(float(luma.mean()), 2),
        "luma_sd": round(float(luma.std()), 2),
        "p95_minus_p5": round(float(np.percentile(luma, 95) - np.percentile(luma, 5)), 2),
        "saturation_pct": round(float(saturation.mean() * 100), 2),
        "global_r_minus_b": round(float((rgb[..., 0] - rgb[..., 2]).mean()), 2),
        "background_top_corner_luma": round(float(top_corners.mean()), 2),
        "shadow_pct": round(float((luma < 64).mean() * 100), 2),
        "highlight_pct": round(float((luma > 210).mean() * 100), 2),
        "sharpness": round(float(laplacian.var()), 2),
        "skin_pixels": int(skin.shape[0]),
    }
    if skin.size:
        skin_luma = skin[:, 0] * 0.2126 + skin[:, 1] * 0.7152 + skin[:, 2] * 0.0722
        skin_max = skin.max(axis=1)
        skin_min = skin.min(axis=1)
        skin_sat = np.divide(skin_max - skin_min, skin_max, out=np.zeros_like(skin_max), where=skin_max > 0)
        result["skin_lab_l"] = round(float(srgb_to_lab_l(skin).mean()), 2)
        result["skin_luma_255"] = round(float(skin_luma.mean()), 2)
        result["skin_r_minus_b"] = round(float((skin[:, 0] - skin[:, 2]).mean()), 2)
        result["skin_saturation_pct"] = round(float(skin_sat.mean() * 100), 2)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = [analyze(path) for path in args.paths]
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
