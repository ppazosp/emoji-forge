"""Register raster cels and annotation masks against a reference body."""

import math
from pathlib import Path

from PIL import Image

if __package__:
    from .common import cli, image, mask_geometry, read_timing
else:
    from common import cli, image, mask_geometry, read_timing
import json


def configure(parser):
    parser.add_argument("timing", type=Path)
    parser.add_argument("output", type=Path, help="new directory")
    parser.add_argument("--reference", type=int, default=1, help="1-based exposure")
    parser.add_argument("--size", type=int, help="output square size; defaults to reference canvas")


def register(args):
    rows, delays = read_timing(args.timing)
    if not 1 <= args.reference <= len(rows) or (args.size is not None and args.size < 1):
        raise ValueError("invalid reference exposure or output size")
    root = args.timing.parent
    reference = rows[args.reference - 1]
    reference_mask = image(root / reference["body"], "L")
    (target_x, target_y), (width, height) = mask_geometry(reference_mask)
    size = (args.size, args.size) if args.size else reference_mask.size
    target_x += (size[0] - reference_mask.width) / 2
    target_y += (size[1] - reference_mask.height) / 2

    cels = {}
    for row in rows:
        source = image(root / row["file"])
        body = image(root / row["body"], "L")
        face = image(root / row["face"], "L") if "face" in row else None
        if body.size != source.size or (face and face.size != source.size):
            raise ValueError(f"mask canvas differs from cel: {row['file']}")
        (x, y), (w, h) = mask_geometry(body)
        scale = math.sqrt(width * height / (w * h))
        dx, dy, dw = row.get("motion", [0, 0, 0])
        scale *= (width + dw) / width
        if scale <= 0:
            raise ValueError("expected motion produces a nonpositive scale")
        cx, cy = target_x + dx, target_y + dy
        cels.setdefault(
            (row["file"], row["body"], row.get("face"), dx, dy, dw),
            (source, body, face, (1 / scale, 0, x - cx / scale, 0, 1 / scale, y - cy / scale)),
        )

    args.output.mkdir(parents=True, exist_ok=False)
    outputs = {}
    for index, (key, (source, body, face, transform)) in enumerate(cels.items(), 1):
        outputs[key] = {}
        for role, layer in (("file", source), ("body", body), ("face", face)):
            if layer is None:
                continue
            name = f"{index:03d}-{role}.png"
            resample = Image.Resampling.BICUBIC if role == "file" else Image.Resampling.NEAREST
            layer.transform(size, Image.Transform.AFFINE, transform, resample=resample).save(
                args.output / name
            )
            outputs[key][role] = name

    result = []
    for row, ms in zip(rows, delays, strict=True):
        key = (row["file"], row["body"], row.get("face"), *row.get("motion", [0, 0, 0]))
        result.append({**row, **outputs[key], "ms": ms})
    (args.output / "timing.json").write_text(json.dumps({"frames": result}, indent=2) + "\n")


if __name__ == "__main__":
    cli(__doc__, configure, register)
