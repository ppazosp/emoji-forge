"""Key flat backgrounds and align generated art on a shared canvas."""

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageOps

if __package__:
    from .common import add_timing_flags, cli, image, read_cel, read_timing
else:
    from common import add_timing_flags, cli, image, read_cel, read_timing


@dataclass
class Cutout:
    art: Image.Image
    body: Image.Image
    face: Image.Image | None


def key_region(rgb, color, tolerance):
    red, green, blue = ImageChops.difference(
        rgb, Image.new("RGB", rgb.size, color)
    ).split()
    distance = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    return distance.point(lambda value: 255 if value <= tolerance else 0)


def flat_border(region):
    w, h = region.size
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if not all(region.getpixel(point) for point in corners):
        return False
    sides = [(0, 0, w, 1), (0, h - 1, w, h), (0, 0, 1, h), (w - 1, 0, w, h)]
    matching = sum(region.crop(box).histogram()[255] for box in sides)
    return matching >= (w + h) * 1.8


def cut_background(art, background, tolerance):
    alpha = art.getchannel("A")
    if background == "keep" or (background == "auto" and alpha.getextrema()[0] < 255):
        return art
    rgb = art.convert("RGB")
    color = (
        rgb.getpixel((0, 0))
        if background == "auto"
        else ImageColor.getcolor(background, "RGB")
    )
    region = key_region(rgb, color, tolerance)
    if background == "auto" and (not flat_border(region) or not region.histogram()[0]):
        return art
    padded = ImageOps.expand(region, border=1, fill=255)
    ImageDraw.floodfill(padded, (0, 0), 128)
    keep = padded.crop((1, 1, art.width + 1, art.height + 1)).point(
        lambda value: 0 if value == 128 else 255
    )
    art.putalpha(ImageChops.multiply(alpha, keep))
    return art


def load_cutout(root, row, background="auto", tolerance=20):
    art = cut_background(read_cel(root, row), background, tolerance)
    alpha = art.getchannel("A")
    box = alpha.point(lambda value: 255 if value >= 16 else 0).getbbox()
    if box is None:
        raise ValueError(f"{row['file']}: no foreground remains after keying")
    masks = {}
    for name in ("body", "face"):
        if name in row:
            mask = image(root / row[name], "L")
            if mask.size != art.size:
                raise ValueError(
                    f"{row['file']}: {name} mask must match the source canvas"
                )
            masks[name] = ImageChops.darker(mask, alpha).crop(box)
    return Cutout(art.crop(box), masks.get("body", alpha.crop(box)), masks.get("face"))


def place(image, size, scale, anchor):
    span = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    resample = (
        Image.Resampling.LANCZOS if image.mode == "RGBA" else Image.Resampling.NEAREST
    )
    tile = image.resize(span, resample)
    canvas = Image.new(image.mode, (size, size))
    canvas.paste(tile, anchor)
    return canvas


def placement(art, canvas, span, scale, anchor):
    width, height = round(art.width * scale), round(art.height * scale)
    x = (canvas - max(1, width)) // 2
    if anchor == "bottom":
        y = (canvas + span) // 2 - max(1, height)
    else:
        y = (canvas - max(1, height)) // 2
    return x, y


def configure(parser):
    parser.add_argument(
        "input", type=Path, help="generated image, ordered folder, or timing JSON"
    )
    parser.add_argument("output", type=Path, help="new cel directory")
    parser.add_argument("--size", type=int, default=512, help="square working canvas")
    parser.add_argument(
        "--fill",
        type=float,
        default=0.8,
        help="fraction of canvas used by the longest side",
    )
    parser.add_argument("--anchor", choices=("center", "bottom"), default="center")
    parser.add_argument("--scale", choices=("fit", "shared"), default="fit")
    parser.add_argument(
        "--background", default="auto", help="auto, keep, or a CSS key colour"
    )
    parser.add_argument(
        "--tolerance", type=int, default=20, help="per-channel key tolerance, 0–255"
    )
    add_timing_flags(parser)


def run(args):
    if args.size < 1 or not 0 < args.fill <= 1 or not 0 <= args.tolerance <= 255:
        raise ValueError(
            "use a positive size, fill in (0, 1], and tolerance in [0, 255]"
        )
    rows, delays = read_timing(args.input, args.timing_spec, args.frame_ms)
    cutouts = [
        load_cutout(args.input.parent, row, args.background, args.tolerance)
        for row in rows
    ]
    largest = max(max(cel.art.size) for cel in cutouts)
    span = max(1, round(args.size * args.fill))
    args.output.mkdir(parents=True, exist_ok=False)
    frames = []
    for index, (cel, ms) in enumerate(zip(cutouts, delays, strict=True), 1):
        extent = largest if args.scale == "shared" else max(cel.art.size)
        scale = span / extent
        anchor = placement(cel.art, args.size, span, scale, args.anchor)
        frame = {"ms": ms}
        for role, layer, suffix in (
            ("file", cel.art, ""),
            ("body", cel.body, "-body"),
            ("face", cel.face, "-face"),
        ):
            if layer is not None:
                name = f"{index:03d}{suffix}.png"
                place(layer, args.size, scale, anchor).save(args.output / name)
                frame[role] = name
        frames.append(frame)
    (args.output / "timing.json").write_text(
        json.dumps({"frames": frames}, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    cli(__doc__, configure, run)
