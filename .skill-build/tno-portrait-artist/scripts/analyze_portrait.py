#!/usr/bin/env python3
"""Measure TNO portrait tone, color, sharpness, alpha, and face composition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment guidance
    raise SystemExit("Install Pillow, numpy, and opencv-python before running this script") from exc


DOP_GNG_GATES: dict[str, tuple[float, float]] = {
    "luma_mean": (108.0, 128.0),
    "p95_minus_p5": (200.0, 216.0),
    "saturation_pct": (20.0, 27.0),
    "shadow_pct": (22.0, 34.0),
    "highlight_pct": (9.0, 17.0),
    "sharpness": (440.0, 730.0),
    "skin_luma_255": (120.0, 145.0),
    "skin_r_minus_b": (44.0, 55.0),
    "skin_saturation_pct": (29.0, 35.0),
    "face_height_ratio": (0.55, 0.60),
    "eye_zone_estimate": (0.38, 0.47),
}


def srgb_to_lab_l(rgb: np.ndarray) -> np.ndarray:
    value = rgb.astype(np.float64) / 255.0
    linear = np.where(value <= 0.04045, value / 12.92, ((value + 0.055) / 1.055) ** 2.4)
    xyz_y = linear[..., 0] * 0.2126729 + linear[..., 1] * 0.7151522 + linear[..., 2] * 0.0721750
    epsilon = 216 / 24389
    kappa = 24389 / 27
    f_y = np.where(xyz_y > epsilon, np.cbrt(xyz_y), (kappa * xyz_y + 16) / 116)
    return 116 * f_y - 16


def detect_face(rgb_u8: np.ndarray) -> dict[str, Any] | None:
    bgr = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    frontal = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    candidates: list[tuple[int, int, int, int, str]] = []
    for x, y, w, h in frontal.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(45, 45)):
        candidates.append((int(x), int(y), int(w), int(h), "frontal"))
    for x, y, w, h in profile.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(45, 45)):
        candidates.append((int(x), int(y), int(w), int(h), "profile"))
    flipped = cv2.flip(gray, 1)
    for x, y, w, h in profile.detectMultiScale(flipped, scaleFactor=1.05, minNeighbors=3, minSize=(45, 45)):
        candidates.append((int(rgb_u8.shape[1] - x - w), int(y), int(w), int(h), "profile-flipped"))
    if not candidates:
        return None
    x, y, w, h, detector = max(candidates, key=lambda box: box[2] * box[3])
    return {
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "height_ratio": round(h / rgb_u8.shape[0], 4),
        "eye_zone_estimate": round((y + h * 0.40) / rgb_u8.shape[0], 4),
        "detector": detector,
    }


def analyze(path: Path, preset: str) -> dict[str, Any]:
    source = Image.open(path).convert("RGBA")
    rgba = np.asarray(source, dtype=np.float64)
    alpha_u8 = rgba[..., 3].astype(np.uint8)
    alpha = rgba[..., 3:4] / 255.0
    rgb = rgba[..., :3] * alpha + 255.0 * (1.0 - alpha)
    rgb_u8 = np.clip(rgb, 0, 255).astype(np.uint8)
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
    top_corners = np.concatenate((luma[:corner_h, :corner_w].ravel(), luma[:corner_h, -corner_w:].ravel()))

    x0, x1 = round(w * 0.22), round(w * 0.78)
    y0, y1 = round(h * 0.18), round(h * 0.69)
    face_region = rgb[y0:y1, x0:x1]
    r, g, b = face_region[..., 0], face_region[..., 1], face_region[..., 2]
    skin_mask = (
        (r > 65)
        & (g > 45)
        & (b > 35)
        & (r > g)
        & (g > b)
        & ((r - b) > 10)
        & ((r - g) < 75)
    )
    skin = face_region[skin_mask]

    padded = np.pad(luma, 1, mode="edge")
    laplacian = (
        padded[1:-1, :-2]
        + padded[1:-1, 2:]
        + padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        - 4 * luma
    )

    result: dict[str, Any] = {
        "file": str(path),
        "width": w,
        "height": h,
        "mode": source.mode,
        "alpha_min": int(alpha_u8.min()),
        "alpha_max": int(alpha_u8.max()),
        "alpha_unique_values": int(np.unique(alpha_u8).size),
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
        "face": detect_face(rgb_u8),
    }
    if skin.size:
        skin_luma = skin[:, 0] * 0.2126 + skin[:, 1] * 0.7152 + skin[:, 2] * 0.0722
        skin_max = skin.max(axis=1)
        skin_min = skin.min(axis=1)
        skin_sat = np.divide(skin_max - skin_min, skin_max, out=np.zeros_like(skin_max), where=skin_max > 0)
        result.update(
            {
                "skin_lab_l": round(float(srgb_to_lab_l(skin).mean()), 2),
                "skin_luma_255": round(float(skin_luma.mean()), 2),
                "skin_r_minus_b": round(float((skin[:, 0] - skin[:, 2]).mean()), 2),
                "skin_saturation_pct": round(float(skin_sat.mean() * 100), 2),
            }
        )

    violations: list[dict[str, Any]] = []
    warnings: list[str] = []
    if preset == "dop-gng":
        if (w, h) != (156, 210):
            violations.append({"metric": "dimensions", "value": [w, h], "expected": [156, 210]})
        face = result["face"]
        if face is None:
            warnings.append("No face detected; composition requires manual review")
        else:
            result["face_height_ratio"] = face["height_ratio"]
            result["eye_zone_estimate"] = face["eye_zone_estimate"]
        for metric, (lower, upper) in DOP_GNG_GATES.items():
            if metric not in result:
                continue
            value = float(result[metric])
            if value < lower or value > upper:
                violations.append({"metric": metric, "value": value, "expected": [lower, upper]})
    result["preset"] = preset
    result["numeric_gate_pass"] = not violations
    result["violations"] = violations
    result["warnings"] = warnings
    result["note"] = "Numeric pass never overrides visual hard-fail defects or mixed-board review."
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--preset", choices=("none", "dop-gng"), default="none")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = [analyze(path, args.preset) for path in args.paths]
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
