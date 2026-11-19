"""Compare cels with style references and neighboring exposures."""

import json
from collections import Counter
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

if __package__:
    from . import pack_assets
    from .common import cli, output_path, read_timing
    from .import_cels import Cutout, load_cutout
else:
    import pack_assets
    from common import cli, output_path, read_timing
    from import_cels import Cutout, load_cutout


@dataclass
class Measures:
    palette: dict
    silhouette: int
    perceptual: int


def bits(values, predicate):
    return sum(1 << index for index, value in enumerate(values) if predicate(value))


def describe(cutout):
    mask = cutout.body.point(lambda value: 255 if value >= 128 else 0)
    box = mask.getbbox()
    if box is None:
        raise ValueError("style or cel mask has no opaque foreground")
    mask = mask.crop(box)
    art = cutout.art.crop(box)
    art.putalpha(ImageChops.darker(art.getchannel("A"), mask))
    sample = ImageOps.contain(art, (32, 32), Image.Resampling.LANCZOS)
    foreground = Counter(
        (r // 64, g // 64, b // 64) for r, g, b, a in sample.getdata() if a >= 128
    )
    total = sum(foreground.values())
    if not total:
        raise ValueError("style or cel is too thin to measure at 32 pixels")
    palette = {color: count / total for color, count in foreground.items()}
    offset = ((32 - sample.width) // 2, (32 - sample.height) // 2)
    alpha = Image.new("L", (32, 32))
    alpha.paste(sample.getchannel("A"), offset)
    shape = bits(alpha.getdata(), lambda value: value >= 128)
    matte = Image.new("RGBA", (32, 32), (127, 127, 127, 255))
    matte.alpha_composite(sample, offset)
    gray = matte.convert("L").resize((8, 8), Image.Resampling.LANCZOS).getdata()
    average = sum(gray) / 64
    return Measures(palette, shape, bits(gray, lambda value: value > average))


def compare(a, b):
    overlap = sum(
        min(value, b.palette.get(color, 0)) for color, value in a.palette.items()
    )
    return {
        "color_distance": round(max(0, 1 - overlap), 4),
        "mask_iou": round(
            (a.silhouette & b.silhouette).bit_count()
            / (a.silhouette | b.silhouette).bit_count(),
            4,
        ),
        "hash_distance": round((a.perceptual ^ b.perceptual).bit_count() / 64, 4),
    }


def score(result):
    return result["color_distance"] + (1 - result["mask_iou"]) + result["hash_distance"]


def issues(result, args):
    return {
        name
        for name, active in (
            ("palette", result["color_distance"] > args.color),
            ("silhouette", result["mask_iou"] < args.iou),
            ("perceptual-hash", result["hash_distance"] > args.hash_distance),
        )
        if active
    }


def load_series(path, background):
    rows, _ = read_timing(path)
    return [
        (Path(row["file"]).name, describe(load_cutout(path.parent, row, background)))
        for row in rows
    ]


def configure(parser):
    parser.add_argument("cels", type=Path, help="cel folder or timing JSON")
    parser.add_argument(
        "style",
        type=Path,
        nargs="?",
        help="one style pose image or folder of separately cropped reference poses",
    )
    parser.add_argument("output", type=Path, help="JSON report")
    parser.add_argument(
        "--props",
        action="store_true",
        help="compare annotated asset crops in a production project",
    )
    parser.add_argument(
        "--crops", type=Path, help="override project/lineup.json with --props"
    )
    parser.add_argument(
        "--color", type=float, default=0.45, help="maximum colour histogram distance"
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.52,
        help="minimum silhouette intersection over union",
    )
    parser.add_argument(
        "--hash-distance", type=float, default=0.36, help="maximum mean-hash distance"
    )


def closest(frame, styles):
    return min(
        ((name, compare(frame, style)) for name, style in styles),
        key=lambda item: score(item[1]),
    )


def asset_drift(args):
    _, assets = pack_assets.read_lineup(args.cels, args.crops)

    def measure(record):
        art = pack_assets.crop(args.cels, record)
        return describe(Cutout(art, art.getchannel("A"), None))

    results = []
    for key, row in assets.items():
        styles = [(record["file"], measure(record)) for record in row["references"]]
        for emoji, records in row["appearances"].items():
            for record in records:
                reference, metrics = closest(measure(record), styles)
                results.append(
                    {
                        "asset": key,
                        "emoji": emoji,
                        "crop": record,
                        "reference": reference,
                        **metrics,
                        "flags": sorted(issues(metrics, args)),
                    }
                )
    return {"assets": results, "flagged": sum(bool(row["flags"]) for row in results)}


def cel_drift(args):
    frames, styles = load_series(args.cels, "keep"), load_series(args.style, "auto")
    neighbors = [compare(a, b) for (_, a), (_, b) in pairwise(frames)]
    results = []
    for index, (name, frame) in enumerate(frames):
        reference, style = closest(frame, styles)
        prev = neighbors[index - 1] if index else None
        next_ = neighbors[index] if index < len(neighbors) else None
        reasons = [f"style:{item}" for item in sorted(issues(style, args))]
        if prev and next_:
            reasons.extend(
                f"neighbors:{item}"
                for item in sorted(issues(prev, args) & issues(next_, args))
            )
        results.append(
            {
                "frame": index + 1,
                "file": name,
                "style": {"file": reference, **style},
                "previous": prev,
                "next": next_,
                "flags": reasons,
            }
        )
    return {"flagged": sum(bool(row["flags"]) for row in results), "frames": results}


def run(args):
    if not all(0 <= value <= 1 for value in (args.color, args.iou, args.hash_distance)):
        raise ValueError("thresholds must be between 0 and 1")
    if args.props == bool(args.style):
        raise ValueError(
            "use CELS STYLE OUTPUT for cel drift or PROJECT OUTPUT --props for asset drift"
        )
    if args.crops and not args.props:
        raise ValueError("--crops requires --props")
    report = asset_drift(args) if args.props else cel_drift(args)
    output_path(args.output).write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    cli(__doc__, configure, run)
