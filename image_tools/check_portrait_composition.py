#!/usr/bin/env python3
"""Detect the dominant face and report its size/position for portrait QA."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2


def detect(path: Path) -> dict[str, object]:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Unable to read {path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    frontal = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    candidates: list[tuple[int, int, int, int, str]] = []
    for x, y, w, h in frontal.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(45, 45)):
        candidates.append((int(x), int(y), int(w), int(h), "frontal"))
    for x, y, w, h in profile.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(45, 45)):
        candidates.append((int(x), int(y), int(w), int(h), "profile"))
    flipped = cv2.flip(gray, 1)
    for x, y, w, h in profile.detectMultiScale(flipped, scaleFactor=1.05, minNeighbors=3, minSize=(45, 45)):
        candidates.append((int(image.shape[1] - x - w), int(y), int(w), int(h), "profile-flipped"))
    candidates.sort(key=lambda box: box[2] * box[3], reverse=True)
    best = candidates[0] if candidates else None
    result: dict[str, object] = {
        "file": str(path),
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
        "face": None,
    }
    if best:
        x, y, w, h, detector = best
        result["face"] = {
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "height_ratio": round(h / image.shape[0], 4),
            "eye_zone_estimate": round((y + h * 0.40) / image.shape[0], 4),
            "detector": detector,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = [detect(path) for path in args.paths]
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
