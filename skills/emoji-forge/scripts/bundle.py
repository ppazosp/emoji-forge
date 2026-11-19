"""Build an overview and a multiscale distribution from the original masters."""

from argparse import Namespace
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image, ImageColor

if __package__:
    from . import assemble_gif, build_preview
    from .common import (
        cli,
        decode,
        gif_delays,
        output_path,
        pack_entries,
        read_cel,
        read_json,
        read_timing,
    )
else:
    import assemble_gif
    import build_preview
    from common import (
        cli,
        decode,
        gif_delays,
        output_path,
        pack_entries,
        read_cel,
        read_json,
        read_timing,
    )

DEFAULT_SCALES = (64, 128, 256, 512)
TARGETS = {"slack": (128, 128000, 50), "generic": (256, 1000000, 120)}


def configure(parser):
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path, help="new distribution folder")
    parser.add_argument(
        "--zip", type=Path, help="defaults to a sibling of the output folder"
    )
    parser.add_argument(
        "--preset", choices=TARGETS, help="platform budget for the upload scale"
    )
    parser.add_argument("--size", type=int, help="override the upload size")
    parser.add_argument(
        "--scales",
        help="comma-separated output sizes; defaults to supported 64,128,256,512",
    )
    parser.add_argument(
        "--2x", action="store_true", dest="double", help="also render a larger overview"
    )
    parser.add_argument(
        "--pixel-art", action="store_true", help="use nearest-neighbor scaling"
    )


def master_info(entry, source, root):
    path = root / entry["master"] if entry.get("master") else source
    if path.suffix.lower() == ".json":
        rows, _ = read_timing(path)
        extent = min(min(read_cel(path.parent, row).size) for row in rows)
    else:
        with Image.open(path) as master:
            extent = min(master.size)
    return path, extent


def scale_frames(master, size, resample, matte):
    if master.suffix.lower() == ".json":
        rows, delays = read_timing(master)
        frames = (read_cel(master.parent, row) for row in rows)
    else:
        timeline = decode(master)
        frames, delays = timeline.frames, timeline.delays
    scaled = []
    for cel in frames:
        cel.thumbnail((size, size), resample)
        resized = Image.new(
            "RGBA", (size, size), (*matte, 255) if matte else (0, 0, 0, 0)
        )
        resized.alpha_composite(
            cel, ((size - cel.width) // 2, (size - cel.height) // 2)
        )
        scaled.append(resized)
    return scaled, delays


def write_variant(source, master, target, size, animated, entry, bounds, resample):
    limit, max_frames = bounds
    with Image.open(source) as existing:
        repeat = entry.get("loop", existing.info.get("loop", 0))
        if (
            existing.size == (size, size)
            and existing.format == ("GIF" if animated else "PNG")
            and (limit is None or source.stat().st_size <= limit)
            and (max_frames is None or getattr(existing, "n_frames", 1) <= max_frames)
        ):
            copyfile(source, target)
            return
    matte = ImageColor.getcolor(entry["matte"], "RGB") if entry.get("matte") else None
    frames, delays = scale_frames(master, size, resample, matte)
    if not animated:
        frames[0].save(target, optimize=True)
    else:
        if len(frames) < 2:
            raise ValueError(f"{entry['name']}: supply an animated master")
        assemble_gif.fit_bytes(
            frames, gif_delays(delays), target, repeat, matte, 128, limit, max_frames
        )
    if limit is not None and target.stat().st_size > limit:
        raise ValueError(f"{entry['name']}: upload exceeds {limit} bytes")


def overview(root, names, scale, stem, animated, pixel_art):
    with TemporaryDirectory(prefix="forge-overview-") as temp:
        manifest = Path(temp) / "pack.json"
        import json

        manifest.write_text(
            json.dumps(
                {
                    "emojis": [
                        {
                            "name": name,
                            "file": str(
                                (
                                    root / "emoji" / str(scale) / (name + suffix)
                                ).resolve()
                            ),
                        }
                        for name, suffix in names
                    ]
                }
            ),
            encoding="utf-8",
        )
        draft = Path(temp) / "preview"
        build_preview.build(
            Namespace(
                manifest=manifest,
                output=draft,
                columns=4,
                tile=min(192 if stem.endswith("@2x") else 96, scale),
                duration_ms=None,
                still_ms=0,
                background="#20252f",
                text="#ffffff",
                pixel_art=pixel_art,
                font_size=24 if stem.endswith("@2x") else 14,
            )
        )
        suffix = ".gif" if animated else ".png"
        copyfile(draft.with_suffix(suffix), root / f"{stem}{suffix}")


def upload_limits(entry, args, preset, source):
    if args.size is None and args.preset is None and "limits" in entry:
        recorded = entry["limits"]
        return recorded["size"], recorded["max_bytes"], recorded["max_frames"]
    if preset:
        size, limit, frames = TARGETS[preset]
    else:
        with Image.open(source) as original:
            size, limit, frames = max(original.size), None, None
    return args.size or size, limit, frames


def bundle(args):
    if args.size is not None and args.size < 1:
        raise ValueError("--size must be positive")
    data = read_json(args.manifest) if args.manifest.suffix.lower() == ".json" else {}
    preset = args.preset or data.get("target")
    entries = []
    for entry, source in pack_entries(args.manifest):
        with Image.open(source) as original:
            animated = getattr(original, "n_frames", 1) > 1
        master, extent = master_info(entry, source, args.manifest.parent)
        entries.append(
            (
                entry,
                source,
                master,
                extent,
                animated,
                upload_limits(entry, args, preset, source),
            )
        )
    available = min(item[3] for item in entries)
    targets = {item[5][0] for item in entries}
    scales = (
        [int(size) for size in args.scales.split(",")]
        if args.scales
        else [size for size in DEFAULT_SCALES if size <= available]
    )
    if any(size < 1 for size in scales) or max(set(scales) | targets) > available:
        raise ValueError(
            f"requested scales need larger masters; all emoji support up to {available}px without upscaling"
        )
    scales = sorted(set(scales) | targets)
    archive = args.zip or args.output.with_name(args.output.name + ".zip")
    if archive.exists() or archive.resolve().is_relative_to(args.output.resolve()):
        raise ValueError("ZIP must be a new path outside the distribution folder")
    args.output.mkdir(parents=True)
    names = [
        "# Emoji names",
        "",
        "| Order | Emoji | When to use | Upload |",
        "| ---: | --- | --- | --- |",
    ]
    variants = []
    resample = Image.Resampling.NEAREST if args.pixel_art else Image.Resampling.LANCZOS
    for index, (entry, source, master, _, animated, limits) in enumerate(entries, 1):
        name = entry["name"]
        suffix = ".gif" if animated else ".png"
        variants.append((name, suffix))
        for size in scales:
            target = output_path(args.output / "emoji" / str(size) / (name + suffix))
            write_variant(
                source,
                master,
                target,
                size,
                animated,
                entry,
                limits[1:] if size == limits[0] else (None, None),
                resample,
            )
        use = " ".join(entry.get("use", "").split()).replace("|", "&#124;")
        names.append(
            f"| {index} | `{name}` | {use} | [Upload](emoji/{limits[0]}/{name}{suffix}) |"
        )
    (args.output / "NAMES.md").write_text("\n".join(names) + "\n", encoding="utf-8")
    animated = any(suffix == ".gif" for _, suffix in variants)
    base_scale = min(scales, key=lambda size: (abs(size - 96), -size))
    overview(args.output, variants, base_scale, "overview", animated, args.pixel_art)
    if args.double:
        overview(
            args.output, variants, max(scales), "overview@2x", animated, args.pixel_art
        )
    with ZipFile(output_path(archive), "x") as zipped:
        for path in sorted(args.output.rglob("*")):
            if path.is_file():
                info = ZipInfo(path.relative_to(args.output).as_posix())
                info.external_attr = 0o100644 << 16
                zipped.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED)


if __name__ == "__main__":
    cli(__doc__, configure, bundle)
