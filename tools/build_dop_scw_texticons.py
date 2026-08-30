from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "gfx" / "texticons" / "scw"
DEFAULT_PREVIEW = ROOT / "artifacts" / "scw-texticons-preview"
TEMPLATE = ROOT / "gfx" / "texticons" / "guangdong" / "huaren.dds"
SIZE = 18
HEADER_SIZE = 128

ICON_NAMES = (
    "audience_patience_texticon",
    "supervisor_attitude_texticon",
    "stage_integrity_texticon",
)

BLACK = (20, 18, 16, 255)
GOLD = (224, 181, 56, 255)
CORRUPTION_GREEN = (45, 177, 157, 255)
CORRUPTION_IVORY = (239, 226, 184, 255)
CORRUPTION_RED = (177, 56, 78, 255)


def read_header(path: Path) -> dict[str, int]:
    raw = path.read_bytes()
    if len(raw) < HEADER_SIZE or raw[:4] != b"DDS ":
        raise ValueError(f"not a DDS with 128-byte header: {path}")
    return {
        "flags": struct.unpack_from("<I", raw, 8)[0],
        "height": struct.unpack_from("<I", raw, 12)[0],
        "width": struct.unpack_from("<I", raw, 16)[0],
        "pitch": struct.unpack_from("<I", raw, 20)[0],
        "depth": struct.unpack_from("<I", raw, 24)[0],
        "mips": struct.unpack_from("<I", raw, 28)[0],
        "pf_size": struct.unpack_from("<I", raw, 76)[0],
        "pf_flags": struct.unpack_from("<I", raw, 80)[0],
        "fourcc": struct.unpack_from("<I", raw, 84)[0],
        "rgb_bits": struct.unpack_from("<I", raw, 88)[0],
        "r_mask": struct.unpack_from("<I", raw, 92)[0],
        "g_mask": struct.unpack_from("<I", raw, 96)[0],
        "b_mask": struct.unpack_from("<I", raw, 100)[0],
        "a_mask": struct.unpack_from("<I", raw, 104)[0],
        "caps": struct.unpack_from("<I", raw, 108)[0],
        "bytes": len(raw),
    }


EXPECTED = {
    "flags": 0x2100F,
    "height": SIZE,
    "width": SIZE,
    "pitch": SIZE * 4,
    "depth": 1,
    "mips": 1,
    "pf_size": 32,
    "pf_flags": 0x41,
    "fourcc": 0,
    "rgb_bits": 32,
    "r_mask": 0x00FF0000,
    "g_mask": 0x0000FF00,
    "b_mask": 0x000000FF,
    "a_mask": 0xFF000000,
    "caps": 0x1000,
    "bytes": HEADER_SIZE + SIZE * SIZE * 4,
}


def square_contain(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    side = max(image.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(image, ((side - image.width) // 2, (side - image.height) // 2))
    return canvas


def overlay_hourglass(icon: Image.Image) -> None:
    rows = (
        "BBBBBBB",
        "BGGGGGB",
        ".BGGGB.",
        "..BGB..",
        "..BGB..",
        ".BGGGB.",
        "BGGGGGB",
        "BBBBBBB",
    )
    for row, pattern in enumerate(rows):
        for column, pixel in enumerate(pattern):
            if pixel == "B":
                icon.putpixel((11 + column, 10 + row), BLACK)
            elif pixel == "G":
                icon.putpixel((11 + column, 10 + row), GOLD)


def overlay_approval_check(icon: Image.Image) -> None:
    core = {
        (10, 13), (11, 14), (12, 15),
        (13, 14), (14, 13), (15, 12), (16, 11),
        (11, 13), (12, 14), (13, 13), (14, 12), (15, 11),
    }
    rim = {
        (x + dx, y + dy)
        for x, y in core
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        if 0 <= x + dx < SIZE and 0 <= y + dy < SIZE
    } - core
    for point in rim:
        icon.putpixel(point, GOLD)
    for point in core:
        icon.putpixel(point, BLACK)


def corruption_yen_icon() -> Image.Image:
    icon = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    outline_spans = {
        1: (6, 11), 2: (4, 13), 3: (3, 14), 4: (2, 15),
        5: (1, 16), 6: (1, 16), 7: (1, 16), 8: (1, 16),
        9: (1, 16), 10: (1, 16), 11: (1, 16), 12: (1, 16),
        13: (2, 15), 14: (3, 14), 15: (4, 13), 16: (6, 11),
    }
    for y, (left, right) in outline_spans.items():
        for x in range(left, right + 1):
            icon.putpixel((x, y), BLACK)
    for y in range(2, 16):
        left, right = outline_spans[y]
        for x in range(left + 1, right):
            icon.putpixel((x, y), CORRUPTION_GREEN)

    yen = {
        (5, 5), (6, 5), (12, 5), (13, 5),
        (6, 6), (7, 6), (11, 6), (12, 6),
        (7, 7), (8, 7), (10, 7), (11, 7),
        (8, 8), (9, 8), (10, 8),
        *( (x, 9) for x in range(5, 14) ),
        (8, 10), (9, 10), (10, 10),
        *( (x, 11) for x in range(5, 14) ),
        (8, 12), (9, 12), (10, 12),
        (8, 13), (9, 13), (10, 13),
        (8, 14), (9, 14), (10, 14),
    }
    for point in yen:
        icon.putpixel(point, CORRUPTION_IVORY)

    cracks = {
        (11, 2), (10, 3), (10, 4), (11, 5), (10, 6), (10, 7),
        (3, 12), (4, 12), (4, 13), (5, 13), (5, 14), (6, 14),
    }
    for point in cracks:
        icon.putpixel(point, BLACK)
    for point in ((11, 3), (5, 12)):
        icon.putpixel(point, CORRUPTION_RED)

    for point in ((13, 15), (14, 15), (15, 15), (13, 16), (14, 16), (14, 17)):
        icon.putpixel(point, BLACK)
    for point in ((14, 15), (14, 16)):
        icon.putpixel(point, CORRUPTION_GREEN)
    return icon


def native_tno_icons(tno_root: Path) -> dict[str, Image.Image]:
    flag_root = tno_root / "gfx" / "flags" / "small"
    texticon_root = tno_root / "gfx" / "texticons" / "guangdong"
    chi_path = flag_root / "CHI.tga"
    jap_path = flag_root / "JAP.tga"
    corruption_path = texticon_root / "corruption_yen_texticon.dds"
    for path in (chi_path, jap_path, corruption_path):
        if not path.exists():
            raise FileNotFoundError(path)

    icons: dict[str, Image.Image] = {}
    for name, path, overlay in (
        ("audience_patience_texticon", chi_path, overlay_hourglass),
        ("supervisor_attitude_texticon", jap_path, overlay_approval_check),
    ):
        canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        with Image.open(path) as opened:
            flag = opened.convert("RGBA").resize((SIZE, 11), Image.Resampling.BOX)
        canvas.alpha_composite(flag, (0, 1))
        overlay(canvas)
        icons[name] = canvas

    # The native component is a corruption-yen icon; redraw its core motif on
    # the final 18px grid so the yen and fractures survive text-size rendering.
    icons["stage_integrity_texticon"] = corruption_yen_icon()
    return icons


def make_dds(source: Path, output_png: Path, output_dds: Path, preview: Path, template: bytes) -> None:
    with Image.open(source) as opened:
        icon = square_contain(opened).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    icon.save(output_png, format="PNG")

    rgba = icon.tobytes()
    bgra = bytearray(len(rgba))
    for offset in range(0, len(rgba), 4):
        red, green, blue, alpha = rgba[offset : offset + 4]
        bgra[offset : offset + 4] = bytes((blue, green, red, alpha))
    payload = template[:HEADER_SIZE] + bytes(bgra)
    output_dds.write_bytes(payload)

    with Image.open(output_dds) as decoded:
        decoded.convert("RGBA").resize((SIZE * 16, SIZE * 16), Image.Resampling.NEAREST).save(preview, format="PNG")

    header = read_header(output_dds)
    if header != EXPECTED:
        raise RuntimeError(f"DDS header mismatch for {output_dds}: {header}")
    if not any(alpha for alpha in rgba[3::4]):
        raise RuntimeError(f"alpha is fully transparent: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild 18x18 uncompressed BGRA DDS assets from the committed SCW texticon PNGs"
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="directory containing the three authoritative 18x18 PNG files",
    )
    parser.add_argument(
        "--tno-root",
        type=Path,
        help="build from the exact TNO CHI/JAP flags and corruption texticon before packing DDS",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--preview-dir", type=Path, default=DEFAULT_PREVIEW)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    args = parser.parse_args()

    template = args.template.read_bytes()
    template_header = read_header(args.template)
    if template_header != EXPECTED:
        raise RuntimeError(f"template does not match required 18x18 convention: {template_header}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.preview_dir.mkdir(parents=True, exist_ok=True)
    if args.tno_root is not None:
        for name, icon in native_tno_icons(args.tno_root).items():
            icon.save(args.output_dir / f"{name}.png", format="PNG")
        args.source_dir = args.output_dir
    for name in ICON_NAMES:
        source = args.source_dir / f"{name}.png"
        if not source.exists():
            raise FileNotFoundError(source)
        make_dds(
            source,
            args.output_dir / f"{name}.png",
            args.output_dir / f"{name}.dds",
            args.preview_dir / f"{name}.png",
            template,
        )
        print(f"PASS {name}: {args.output_dir / (name + '.png')} and {args.output_dir / (name + '.dds')}")


if __name__ == "__main__":
    main()
