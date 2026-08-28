#!/usr/bin/env python3
"""Measure the color transform between TNO Guangdong leader portraits and their texticons."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


HEADER_SIZE = 128
INNER_X = 7
INNER_Y = 7
INNER_WIDTH = 156
INNER_HEIGHT = 210


def read_dds_rgba(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    if raw[:4] != b"DDS ":
        raise RuntimeError(f"Not a DDS file: {path}")
    height = struct.unpack_from("<I", raw, 12)[0]
    width = struct.unpack_from("<I", raw, 16)[0]
    bits_per_pixel = struct.unpack_from("<I", raw, 88)[0]
    if bits_per_pixel != 32 or len(raw) != HEADER_SIZE + width * height * 4:
        raise RuntimeError(f"Unsupported DDS layout: {path}")
    bgra = np.frombuffer(raw, dtype=np.uint8, offset=HEADER_SIZE).reshape(height, width, 4)
    return bgra[..., [2, 1, 0, 3]].copy()


def fit_channel(source: np.ndarray, target: np.ndarray) -> dict[str, float]:
    design = np.column_stack([source.astype(np.float64), np.ones(source.size)])
    slope, intercept = np.linalg.lstsq(design, target.astype(np.float64), rcond=None)[0]
    predicted = design @ np.asarray([slope, intercept])
    return {
        "slope": round(float(slope), 6),
        "intercept": round(float(intercept), 6),
        "rmse": round(float(np.sqrt(np.mean((predicted - target) ** 2))), 4),
    }


def analyze_pair(leader_path: Path, texticon_path: Path) -> tuple[dict[str, object], np.ndarray, np.ndarray]:
    leader = np.asarray(Image.open(leader_path).convert("RGBA"), dtype=np.uint8)
    texticon = read_dds_rgba(texticon_path)
    inner = texticon[INNER_Y : INNER_Y + INNER_HEIGHT, INNER_X : INNER_X + INNER_WIDTH]
    if leader.shape != inner.shape:
        raise RuntimeError(f"Shape mismatch: {leader_path} {leader.shape} vs {texticon_path} {inner.shape}")

    source = leader[..., :3].reshape(-1, 3)
    target = inner[..., :3].reshape(-1, 3)
    channel_names = ["red", "green", "blue"]
    channel_fits = {
        channel_names[index]: fit_channel(source[:, index], target[:, index]) for index in range(3)
    }

    design = np.column_stack([source.astype(np.float64), np.ones(source.shape[0])])
    coefficients = np.linalg.lstsq(design, target.astype(np.float64), rcond=None)[0]
    predicted = design @ coefficients
    report = {
        "name": leader_path.stem,
        "source_mean_rgb": np.round(source.mean(axis=0), 3).tolist(),
        "texticon_mean_rgb": np.round(target.mean(axis=0), 3).tolist(),
        "mean_delta_rgb": np.round((target.astype(np.float64) - source).mean(axis=0), 3).tolist(),
        "mean_absolute_error": round(float(np.abs(target.astype(np.float64) - source).mean()), 4),
        "channel_affine": channel_fits,
        "rgb_matrix_rows_source_plus_bias": np.round(coefficients, 6).tolist(),
        "rgb_matrix_rmse": round(float(np.sqrt(np.mean((predicted - target) ** 2))), 4),
    }
    return report, leader, inner


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tno_root", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()

    names = ["Morita_Akio", "Ibuka_Masaru", "Matsushita_Masaharu", "Li_Ka-Shing"]
    args.output_directory.mkdir(parents=True, exist_ok=True)
    reports = []
    panels = []
    for name in names:
        report, leader, inner = analyze_pair(
            args.tno_root / "gfx" / "leaders" / "GNG" / f"{name}.png",
            args.tno_root / "gfx" / "texticons" / "guangdong" / f"{name}_texticon.dds",
        )
        reports.append(report)
        panels.extend([leader, inner])

    cell_width = 156
    cell_height = 230
    sheet = Image.new("RGB", (cell_width * 4, cell_height * 2), (28, 30, 30))
    draw = ImageDraw.Draw(sheet)
    for index, panel in enumerate(panels):
        pair_index = index // 2
        row = pair_index // 2
        column = (pair_index % 2) * 2 + (index % 2)
        image = Image.fromarray(panel, "RGBA").convert("RGB")
        sheet.paste(image, (column * cell_width, row * cell_height))
        label = f"{names[pair_index]} {'leader' if index % 2 == 0 else 'texticon'}"
        draw.text((column * cell_width + 3, row * cell_height + 212), label, fill=(230, 230, 230))

    (args.output_directory / "tno_texticon_filter_analysis.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    sheet.save(args.output_directory / "tno_texticon_filter_pairs.png")
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
