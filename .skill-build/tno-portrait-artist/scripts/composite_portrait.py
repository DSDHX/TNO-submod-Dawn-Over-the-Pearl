#!/usr/bin/env python3
"""Extract, grade, reframe, feather, and composite a TNO portrait deterministically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment guidance
    raise SystemExit("Install Pillow, numpy, and opencv-python before running this script") from exc


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = value.lower().split("x", 1)
        return int(width), int(height)
    except (ValueError, AttributeError) as exc:
        raise argparse.ArgumentTypeError("Size must look like 156x210") from exc


def parse_rgb(value: str) -> tuple[int, int, int]:
    try:
        channels = tuple(int(channel.strip()) for channel in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("RGB must look like 0,107,255") from exc
    if len(channels) != 3 or any(channel < 0 or channel > 255 for channel in channels):
        raise argparse.ArgumentTypeError("RGB channels must be three values from 0 to 255")
    return channels  # type: ignore[return-value]


def largest_border_component(condition: np.ndarray) -> np.ndarray:
    count, labels = cv2.connectedComponents(condition.astype(np.uint8), connectivity=8)
    if count <= 1:
        raise RuntimeError("No connected background component found; supply true alpha or adjust key thresholds")
    border = np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))
    values = border[border > 0]
    if not values.size:
        raise RuntimeError("No keyed background touches the image border")
    label = int(np.bincount(values).argmax())
    return labels == label


def extract_alpha(
    rgba: np.ndarray,
    luma_min: float,
    chroma_max: float,
    key_color: tuple[int, int, int] | None,
    key_distance: float,
    erode: int,
    feather: float,
) -> tuple[np.ndarray, str]:
    source_alpha = rgba[..., 3].astype(np.float32) / 255.0
    if float(source_alpha.min()) < 0.999:
        alpha = source_alpha
        method = "source-alpha"
    else:
        rgb = rgba[..., :3].astype(np.float32)
        if key_color is not None:
            key = np.asarray(key_color, dtype=np.float32)
            condition = np.linalg.norm(rgb - key[None, None, :], axis=2) <= key_distance
            method = "connected-key-color"
        else:
            luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
            chroma = rgb.max(axis=2) - rgb.min(axis=2)
            condition = (luma >= luma_min) & (chroma <= chroma_max)
            method = "connected-light-neutral"
        background = largest_border_component(condition)
        alpha = (~background).astype(np.float32)
    if erode > 0:
        alpha = cv2.erode((alpha * 255).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=erode).astype(np.float32) / 255.0
    if feather > 0:
        alpha = cv2.GaussianBlur(alpha, (0, 0), feather)
    return np.clip(alpha, 0, 1), method


def fit_premultiplied(
    premultiplied: np.ndarray,
    alpha: np.ndarray,
    size: tuple[int, int],
    mode: str,
) -> tuple[np.ndarray, np.ndarray]:
    target_w, target_h = size
    source_h, source_w = alpha.shape
    if mode == "stretch":
        return (
            cv2.resize(premultiplied, size, interpolation=cv2.INTER_AREA),
            cv2.resize(alpha, size, interpolation=cv2.INTER_AREA),
        )
    ratio = max(target_w / source_w, target_h / source_h) if mode == "cover" else min(target_w / source_w, target_h / source_h)
    new_w = max(1, round(source_w * ratio))
    new_h = max(1, round(source_h * ratio))
    resized_p = cv2.resize(premultiplied, (new_w, new_h), interpolation=cv2.INTER_AREA)
    resized_a = cv2.resize(alpha, (new_w, new_h), interpolation=cv2.INTER_AREA)
    canvas_p = np.zeros((target_h, target_w, 3), dtype=np.float32)
    canvas_a = np.zeros((target_h, target_w), dtype=np.float32)
    if mode == "cover":
        x0 = max(0, (new_w - target_w) // 2)
        y0 = max(0, (new_h - target_h) // 2)
        return resized_p[y0 : y0 + target_h, x0 : x0 + target_w], resized_a[y0 : y0 + target_h, x0 : x0 + target_w]
    x0 = (target_w - new_w) // 2
    y0 = (target_h - new_h) // 2
    canvas_p[y0 : y0 + new_h, x0 : x0 + new_w] = resized_p
    canvas_a[y0 : y0 + new_h, x0 : x0 + new_w] = resized_a
    return canvas_p, canvas_a


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subject", type=Path)
    parser.add_argument("background", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--size", type=parse_size, default=(156, 210))
    parser.add_argument("--fit", choices=("cover", "contain", "stretch"), default="cover")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--shift-x", type=float, default=0.0, help="Final-pixel horizontal shift")
    parser.add_argument("--shift-y", type=float, default=0.0, help="Final-pixel vertical shift")
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--offset", type=float, default=0.0)
    parser.add_argument("--saturation", type=float, default=1.0)
    parser.add_argument("--highlight-compress", type=float, default=0.0)
    parser.add_argument("--highlight-start", type=float, default=60.0)
    parser.add_argument("--highlight-span", type=float, default=100.0)
    parser.add_argument("--luma-min", type=float, default=225.0)
    parser.add_argument("--chroma-max", type=float, default=8.0)
    parser.add_argument("--key-color", type=parse_rgb)
    parser.add_argument("--key-distance", type=float, default=24.0)
    parser.add_argument("--erode", type=int, default=2, help="Erosion iterations in source pixels")
    parser.add_argument("--source-feather", type=float, default=1.35)
    parser.add_argument("--edge-feather", type=float, default=0.55, help="Additional feather in final pixels")
    parser.add_argument("--shadow-radius", type=float, default=0.0)
    parser.add_argument("--shadow-opacity", type=float, default=0.0)
    parser.add_argument("--resize-background", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if args.scale <= 0 or args.highlight_span <= 0:
        raise SystemExit("--scale and --highlight-span must be positive")

    source = np.asarray(Image.open(args.subject).convert("RGBA"), dtype=np.uint8)
    alpha, extraction_method = extract_alpha(
        source,
        args.luma_min,
        args.chroma_max,
        args.key_color,
        args.key_distance,
        args.erode,
        args.source_feather,
    )
    rgb = source[..., :3].astype(np.float32)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    compressed = args.highlight_compress * np.clip((luma - args.highlight_start) / args.highlight_span, 0, 1)
    graded = np.clip(rgb * args.gain + args.offset - compressed[..., None], 0, 255)
    graded_luma = graded[..., 0] * 0.2126 + graded[..., 1] * 0.7152 + graded[..., 2] * 0.0722
    graded = np.clip(graded_luma[..., None] + args.saturation * (graded - graded_luma[..., None]), 0, 255)
    premultiplied = graded * alpha[..., None]

    output_w, output_h = args.size
    work_size = (output_w * 2, output_h * 2)
    work_p, work_a = fit_premultiplied(premultiplied, alpha, work_size, args.fit)
    center_x, center_y = work_size[0] / 2, work_size[1] / 2
    matrix = np.array(
        [
            [args.scale, 0, (1 - args.scale) * center_x + args.shift_x * 2],
            [0, args.scale, (1 - args.scale) * center_y + args.shift_y * 2],
        ],
        dtype=np.float32,
    )
    work_p = cv2.warpAffine(work_p, matrix, work_size, flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    work_a = cv2.warpAffine(work_a, matrix, work_size, flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    final_p = cv2.resize(np.clip(work_p, 0, None), args.size, interpolation=cv2.INTER_AREA)
    final_a = cv2.resize(np.clip(work_a, 0, 1), args.size, interpolation=cv2.INTER_AREA)

    if args.edge_feather > 0:
        binary = (final_a > 0.5).astype(np.uint8)
        boundary = (
            cv2.dilate(binary, np.ones((3, 3), np.uint8), iterations=1)
            - cv2.erode(binary, np.ones((3, 3), np.uint8), iterations=1)
        ).astype(np.float32)
        weight = np.clip(cv2.GaussianBlur(boundary, (0, 0), max(0.1, args.edge_feather)), 0, 1)
        blurred_p = cv2.GaussianBlur(final_p, (0, 0), args.edge_feather)
        blurred_a = cv2.GaussianBlur(final_a, (0, 0), args.edge_feather)
        final_p = final_p * (1 - weight[..., None]) + blurred_p * weight[..., None]
        final_a = np.clip(final_a * (1 - weight) + blurred_a * weight, 0, 1)

    background_image = Image.open(args.background).convert("RGB")
    if background_image.size != args.size:
        if not args.resize_background:
            raise SystemExit(f"Background is {background_image.size}, expected {args.size}; pass --resize-background explicitly")
        background_image = background_image.resize(args.size, Image.Resampling.LANCZOS)
    background = np.asarray(background_image, dtype=np.float32)

    if args.shadow_radius > 0 and args.shadow_opacity > 0:
        outer_shadow = np.clip(cv2.GaussianBlur(final_a, (0, 0), args.shadow_radius) - final_a, 0, 1)
    else:
        outer_shadow = np.zeros_like(final_a)
    shadowed_background = background * (1 - args.shadow_opacity * outer_shadow[..., None])
    composite = np.clip(final_p + shadowed_background * (1 - final_a[..., None]), 0, 255).astype(np.uint8)
    exact_background = (final_a < 1e-5) & (outer_shadow < 1e-4)
    background_u8 = background.astype(np.uint8)
    composite[exact_background] = background_u8[exact_background]
    rgba_output = np.dstack((composite, np.full((output_h, output_w), 255, dtype=np.uint8)))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba_output).save(args.output, optimize=True)
    report = {
        "subject": str(args.subject),
        "background": str(args.background),
        "output": str(args.output),
        "size": [output_w, output_h],
        "extraction_method": extraction_method,
        "exact_background_pixels": int(exact_background.sum()),
        "max_shadow_alpha": round(float(outer_shadow.max()), 6),
        "settings": {
            "scale": args.scale,
            "shift_x": args.shift_x,
            "shift_y": args.shift_y,
            "gain": args.gain,
            "offset": args.offset,
            "saturation": args.saturation,
            "edge_feather": args.edge_feather,
            "shadow_radius": args.shadow_radius,
            "shadow_opacity": args.shadow_opacity,
        },
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
