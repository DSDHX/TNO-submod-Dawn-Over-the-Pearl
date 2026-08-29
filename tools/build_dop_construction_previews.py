from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = Path(
    r"D:\Creations\DOP_pre_full_rollback_20260829_075704\workspace"
    r"\output\imagegen\construction_previews\sources"
)
OUTPUT_DIR = ROOT / "gfx/interface/bop"
CONTACT_SHEET = ROOT / "docs/DOP_construction_contact_sheet.png"
WIDTH = 182
HEIGHT = 423
BORDER = 2
ACADEMY_BORDER_COLOR = (89, 199, 194, 255)
CONTENT_WIDTH = WIDTH - BORDER * 2
CONTENT_HEIGHT = HEIGHT - BORDER * 2


@dataclass(frozen=True)
class Source:
    id: int
    file_name: str
    focus_x: float
    focus_y: float

    @property
    def stem(self) -> str:
        return f"DOP_construction_project_{self.id:02d}"


# Crop focus is source-only composition metadata. No old frame, strip, border
# or finished preview is consumed by this build.
SOURCES = (
    Source(1, "01_sky_tower.jpg", 0.50, 0.45),
    Source(2, "02_rose_garden.jpg", 0.48, 0.50),
    Source(3, "03_alice_dream_factory.jpg", 0.52, 0.45),
    Source(4, "04_daya_bay_nuclear_plant.jpg", 0.58, 0.48),
    Source(5, "05_guangdong_shinkansen.jpg", 0.50, 0.45),
    Source(6, "06_chaoshan_university.jpg", 0.50, 0.50),
    Source(7, "07_mountain_reservoirs.jpg", 0.50, 0.50),
    Source(8, "08_western_guangdong_granary.jpg", 0.52, 0.50),
    Source(9, "09_pinglu_canal.jpg", 0.50, 0.50),
    Source(10, "10_south_china_sea_oil.jpg", 0.50, 0.45),
    Source(11, "11_wenchang_space_center.jpg", 0.50, 0.45),
    Source(12, "12_guangxi_industrial_institute.jpg", 0.50, 0.52),
    Source(13, "13_guangxi_expressway.jpg", 0.50, 0.52),
    Source(14, "14_nanyue_folk_park.jpg", 0.50, 0.48),
    Source(15, "15_lijiang_waterway.jpg", 0.54, 0.50),
    Source(16, "16_friendship_pass.jpg", 0.50, 0.46),
    Source(17, "17_prd_maglev.jpg", 0.52, 0.50),
    Source(18, "18_shantou_integration.jpg", 0.50, 0.52),
    Source(19, "19_granite_uranium_mining.jpg", 0.55, 0.52),
    Source(20, "20_shale_oil_refineries.jpg", 0.50, 0.48),
)


def focused_crop(image: Image.Image, focus_x: float, focus_y: float) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    source_width, source_height = image.size
    target_ratio = CONTENT_WIDTH / CONTENT_HEIGHT
    source_ratio = source_width / source_height
    if source_ratio > target_ratio:
        crop_height = source_height
        crop_width = round(crop_height * target_ratio)
    else:
        crop_width = source_width
        crop_height = round(crop_width / target_ratio)
    left = round((source_width - crop_width) * focus_x)
    top = round((source_height - crop_height) * focus_y)
    left = max(0, min(left, source_width - crop_width))
    top = max(0, min(top, source_height - crop_height))
    return image.crop((left, top, left + crop_width, top + crop_height)).resize(
        (CONTENT_WIDTH, CONTENT_HEIGHT), Image.Resampling.LANCZOS
    )


def apply_tno_style(image: Image.Image, seed: int) -> Image.Image:
    image = ImageOps.autocontrast(image, cutoff=0.5)
    image = ImageEnhance.Color(image).enhance(0.28)

    # Use a real duotone grade instead of a pale cyan overlay. Deep navy
    # shadows and steel-blue highlights make the cold-blue cast visible while
    # retaining detail. A darker gamma, higher contrast and lower saturation
    # answer the in-GUI readability feedback.
    blue_grade = ImageOps.colorize(
        ImageOps.grayscale(image),
        black=(2, 8, 17),
        white=(142, 167, 193),
    )
    image = Image.blend(image, blue_grade, 0.62)
    image = ImageEnhance.Contrast(image).enhance(1.75)
    image = ImageEnhance.Brightness(image).enhance(0.72)
    image = image.point(
        tuple(round(((value / 255) ** 1.10) * 255) for value in range(256)) * 3
    )
    image = ImageEnhance.Color(image).enhance(0.52)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(2, image.height, 4):
        draw.line((0, y, image.width - 1, y), fill=(0, 5, 15, 34), width=1)
    image = Image.alpha_composite(image.convert("RGBA"), overlay)

    # Match the existing Guangdong Science Academy project preview exactly:
    # its visible crop uses a two-pixel #59C7C2 solid border. The content is
    # cropped for the inset instead of being covered by the frame.
    return ImageOps.expand(
        image,
        border=BORDER,
        fill=ACADEMY_BORDER_COLOR,
    )


def validate_dds(path: Path) -> None:
    payload = path.read_bytes()
    width = struct.unpack_from("<I", payload, 16)[0]
    height = struct.unpack_from("<I", payload, 12)[0]
    depth = struct.unpack_from("<I", payload, 24)[0]
    mipmaps = struct.unpack_from("<I", payload, 28)[0]
    pixel_flags = struct.unpack_from("<I", payload, 80)[0]
    fourcc = payload[84:88]
    rgb_bits = struct.unpack_from("<I", payload, 88)[0]
    masks = tuple(struct.unpack_from("<I", payload, offset)[0] for offset in (92, 96, 100, 104))
    if (width, height, depth, mipmaps, pixel_flags, fourcc, rgb_bits, masks) != (
        WIDTH,
        HEIGHT,
        0,
        0,
        0x41,
        b"\0\0\0\0",
        32,
        (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000),
    ):
        raise ValueError(
            f"{path}: got {width}x{height}, depth={depth}, "
            f"mips={mipmaps}, pixel_flags={pixel_flags:#x}, "
            f"fourcc={fourcc!r}, rgb_bits={rgb_bits}, masks={masks!r}"
        )

    with Image.open(path) as decoded:
        decoded = decoded.convert("RGBA")
    for inset in (0, 1):
        ring = (
            [decoded.getpixel((x, inset)) for x in range(inset, WIDTH - inset)]
            + [decoded.getpixel((x, HEIGHT - 1 - inset)) for x in range(inset, WIDTH - inset)]
            + [decoded.getpixel((inset, y)) for y in range(inset + 1, HEIGHT - 1 - inset)]
            + [decoded.getpixel((WIDTH - 1 - inset, y)) for y in range(inset + 1, HEIGHT - 1 - inset)]
        )
        if set(ring) != {ACADEMY_BORDER_COLOR}:
            raise ValueError(f"{path}: inset {inset} does not match Academy border")


def find_font(size: int) -> ImageFont.ImageFont:
    candidates = (
        Path(r"C:\Windows\Fonts\consola.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def build_contact_sheet(previews: list[tuple[Source, Image.Image]]) -> None:
    columns = 5
    gap = 12
    label_height = 27
    rows = (len(previews) + columns - 1) // columns
    sheet_width = gap + columns * (WIDTH + gap)
    sheet_height = gap + rows * (HEIGHT + label_height + gap)
    sheet = Image.new("RGB", (sheet_width, sheet_height), (7, 18, 22))
    draw = ImageDraw.Draw(sheet)
    font = find_font(15)
    for index, (source, preview) in enumerate(previews):
        column = index % columns
        row = index // columns
        x = gap + column * (WIDTH + gap)
        y = gap + row * (HEIGHT + label_height + gap)
        sheet.paste(preview.convert("RGB"), (x, y))
        draw.text(
            (x, y + HEIGHT + 5),
            f"{source.id:02d}  project_{source.id:02d}",
            font=font,
            fill=(132, 232, 229),
        )
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET, optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build 20 independent DOP construction preview DDS files."
    )
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    args = parser.parse_args()

    missing = [
        source.file_name
        for source in SOURCES
        if not (args.source_dir / source.file_name).is_file()
    ]
    if missing:
        raise FileNotFoundError("missing sources: " + ", ".join(missing))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    previews: list[tuple[Source, Image.Image]] = []
    for source in SOURCES:
        with Image.open(args.source_dir / source.file_name) as original:
            preview = apply_tno_style(
                focused_crop(original, source.focus_x, source.focus_y), source.id
            )
        dds_path = OUTPUT_DIR / f"{source.stem}.dds"
        # The Academy reference is uncompressed 32-bit RGBA DDS. Using the
        # same format prevents a two-pixel border from sharing DXT blocks with
        # image content and changing colour along the edge.
        preview.save(dds_path)
        validate_dds(dds_path)
        with Image.open(dds_path) as decoded:
            decoded.load()
            previews.append((source, decoded.convert("RGBA")))
        print(f"{source.id:02d}/20 {source.file_name} -> {dds_path.name}")

    build_contact_sheet(previews)
    print(f"contact sheet -> {CONTACT_SHEET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
