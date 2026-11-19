"""Build Tavvik's release preview, logo files and social card from the pack masters."""

import argparse
import re
from itertools import pairwise
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image, ImageDraw, ImageFont
from scripts.common import decode, gif_delays, preview_frame

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "examples/mascot/tavvik"
BRAND = ROOT / "assets/brand"
OVERVIEW = "overview@2x.gif"
GIF_BUDGET = 10_000_000


def pack_items(pack):
    names = [
        match[1]
        for match in re.finditer(
            r"^\| \d+ \| `([\w-]+)` \|",
            (pack / "NAMES.md").read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    ]
    if not names:
        raise ValueError("the pack needs at least one named emoji")
    for name in names:
        yield name, ".gif" if (pack / "emoji/256" / f"{name}.gif").is_file() else ".png"


def build_overview(pack, destination):
    timelines = [
        (name, decode(pack / "emoji/256" / (name + ext)))
        for name, ext in pack_items(pack)
    ]
    if any(frame.size != (256, 256) for _, cel in timelines for frame in cel.frames):
        raise ValueError("use the 256 px pack files for the overview")

    duration = max(cel.duration for _, cel in timelines)
    boundaries = {0, duration}
    for _, cel in timelines:
        if len(cel.frames) > 1:
            boundaries.update(
                cycle + mark
                for cycle in range(0, duration, cel.duration)
                for mark in cel.starts
                if cycle + mark < duration
            )
    starts = sorted(boundaries)
    label = ImageFont.load_default(size=32)
    height = 320 * ((len(timelines) + 3) // 4)

    def grid(ms):
        canvas = Image.new("RGBA", (1200, height), "#20252f")
        draw = ImageDraw.Draw(canvas)
        for index, (name, cel) in enumerate(timelines):
            row, column = divmod(index, 4)
            row_count = min(4, len(timelines) - row * 4)
            left = (1200 - 300 * row_count) // 2 + 300 * column
            top = 320 * row
            canvas.alpha_composite(
                preview_frame(cel, cel.starts, ms), (left + 22, top + 8)
            )
            draw.text(
                (left + 150, top + 270), name, fill="#f6f8ff", font=label, anchor="mt"
            )
        return canvas.convert("RGB")

    # Learn one palette from each part of the loop, including the bright impact poses.
    samples = starts[: -1 : max(1, (len(starts) - 1) // 24)]
    sheet = Image.new("RGB", (600, height // 2 * len(samples)))
    for row, mark in enumerate(samples):
        image = grid(mark).resize((600, height // 2), Image.Resampling.LANCZOS)
        sheet.paste(image, (0, row * (height // 2)))
    palette = sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    frames = (
        grid(mark).quantize(palette=palette, dither=Image.Dither.NONE)
        for mark in starts[:-1]
    )
    first = next(frames)
    first.save(
        destination,
        save_all=True,
        append_images=frames,
        duration=gif_delays([b - a for a, b in pairwise(starts)]),
        loop=0,
        disposal=1,
        optimize=True,
    )
    if destination.stat().st_size >= GIF_BUDGET:
        raise ValueError(f"overview exceeds {GIF_BUDGET:,} bytes")


def place(canvas, art, center, extent):
    box = art.getbbox()
    if box:
        art = art.crop(box)
    art.thumbnail((extent, extent), Image.Resampling.LANCZOS)
    canvas.alpha_composite(
        art, (center[0] - art.width // 2, center[1] - art.height // 2)
    )


def build_brand(pack, output):
    masters = pack / "emoji/512"
    logo = decode(masters / "logo.png").frames[0]
    if logo.size != (512, 512):
        raise ValueError("use the 512 px logo master")
    copy2(masters / "logo.png", output / "logo.png")
    for size in (128, 256):
        logo.resize((size, size), Image.Resampling.LANCZOS).save(
            output / f"logo-{size}.png", optimize=True
        )

    card = Image.new("RGBA", (1280, 640), "#e7edf3")
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((816, 46, 1229, 595), radius=36, fill="#d9e2e9")
    draw.arc((829, 102, 1213, 539), 185, 355, fill="#becedb", width=3)
    draw.rounded_rectangle((80, 128, 159, 137), radius=4, fill="#b77b45")
    draw.text(
        (76, 149),
        "emoji-forge",
        font=ImageFont.load_default(size=92),
        fill="#202936",
        stroke_width=2,
    )
    draw.text(
        (81, 283),
        "Make custom emoji with your AI agent.",
        font=ImageFont.load_default(size=36),
        fill="#344e62",
    )
    place(card, logo.copy(), (1023, 324), 378)

    for left, (name, ms) in zip(
        (82, 247, 412),
        (("hammering", 840), ("quench", 750), ("idea", 750)),
        strict=True,
    ):
        timeline = decode(masters / f"{name}.gif")
        art = preview_frame(timeline, timeline.starts, ms).copy()
        if art.size != (512, 512):
            raise ValueError(f"use the 512 px master for {name}")
        draw.rounded_rectangle((left, 390, left + 146, 529), radius=18, fill="#f4f7fb")
        place(card, art, (left + 73, 460), 122)
    social = output / "social-preview.png"
    card.convert("RGB").save(social, optimize=True)
    if social.stat().st_size >= 1_000_000:
        raise ValueError("social preview exceeds 1 MB")


def build_zip(pack, overview, destination):
    files = {
        file.relative_to(pack).as_posix(): file
        for file in pack.rglob("*")
        if file.is_file()
    }
    files[OVERVIEW] = overview
    with ZipFile(destination, "w") as archive:
        for name, source in sorted(files.items()):
            entry = ZipInfo(name)
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, source.read_bytes(), ZIP_DEFLATED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--brand", type=Path, default=BRAND)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="forge-tavvik-previews-") as temporary:
        output = Path(temporary)
        overview = output / OVERVIEW
        build_overview(args.pack, overview)
        build_brand(args.pack, output)
        bundle = output / f"{args.pack.name}.zip"
        build_zip(args.pack, overview, bundle)
        copy2(overview, args.pack / OVERVIEW)
        copy2(bundle, args.pack.with_suffix(".zip"))
        args.brand.mkdir(parents=True, exist_ok=True)
        for name in ("logo.png", "logo-128.png", "logo-256.png", "social-preview.png"):
            copy2(output / name, args.brand / name)
        if args.pack == PACK:
            copy2(
                output / "social-preview.png",
                PACK.parent / "branding/social-preview.png",
            )


if __name__ == "__main__":
    main()
