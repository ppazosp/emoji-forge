"""Register raster cels and annotation masks against a reference body."""

import json
import math
from pathlib import Path

from PIL import Image

if __package__:
    from .common import (
        add_timing_flags,
        cli,
        image,
        mask_geometry,
        read_cel,
        read_timing,
    )
    from .shader_config import parameter_images
else:
    from common import (
        add_timing_flags,
        cli,
        image,
        mask_geometry,
        read_cel,
        read_timing,
    )
    from shader_config import parameter_images


def configure(parser):
    parser.add_argument(
        "timing", type=Path, help="timing JSON, image, or folder of cels"
    )
    add_timing_flags(parser)
    parser.add_argument("output", type=Path, help="new directory")
    parser.add_argument("--reference", type=int, default=1, help="1-based exposure")
    parser.add_argument(
        "--size", type=int, help="output square size; defaults to reference canvas"
    )
    parser.add_argument(
        "--body-reference",
        type=Path,
        help="use an external model mask and match its body height and centroid",
    )


def body_mask(row, root, source=None):
    if "body" in row:
        return image(root / row["body"], "L")
    if source is None:
        source = read_cel(root, row)
    return source.getchannel("A")


def register(args):
    rows, delays = read_timing(args.timing, args.timing_spec, args.frame_ms)
    if not 1 <= args.reference <= len(rows) or (
        args.size is not None and args.size < 1
    ):
        raise ValueError("invalid reference exposure or output size")
    root = args.timing.parent
    reference = rows[args.reference - 1]
    reference_mask = (
        image(args.body_reference, "L")
        if args.body_reference
        else body_mask(reference, root)
    )
    (target_x, target_y), (width, height) = mask_geometry(reference_mask)
    size = (args.size, args.size) if args.size else reference_mask.size
    target_x += (size[0] - reference_mask.width) / 2
    target_y += (size[1] - reference_mask.height) / 2

    cels = {}
    for row in rows:
        source = read_cel(root, row)
        body = body_mask(row, root, source)
        face = image(root / row["face"], "L") if "face" in row else None
        if body.size != source.size or (face and face.size != source.size):
            raise ValueError(f"mask canvas differs from cel: {row['file']}")
        (x, y), (w, h) = mask_geometry(body)
        scale = (
            height / h if args.body_reference else math.sqrt(width * height / (w * h))
        )
        dx, dy, dw = row.get("motion", [0, 0, 0])
        scale *= (width + dw) / width
        squash = row.get("squash", {})
        if squash and not str(squash.get("reason", "")).strip():
            raise ValueError("whitelisted squash needs width, height, and a reason")
        scale_x = scale + squash.get("width", 0) / w
        scale_y = scale + squash.get("height", 0) / h
        if not all(math.isfinite(axis) and axis > 0 for axis in (scale_x, scale_y)):
            raise ValueError(
                "expected motion produces a nonpositive or nonfinite scale"
            )
        cx, cy = target_x + dx, target_y + dy
        key = tuple(row.get(role) for role in ("file", "source_frame", "body", "face"))
        key += (dx, dy, dw, squash.get("width", 0), squash.get("height", 0))
        cels.setdefault(
            key,
            (
                source,
                body,
                face,
                (1 / scale_x, 0, x - cx / scale_x, 0, 1 / scale_y, y - cy / scale_y),
            ),
        )

    args.output.mkdir(parents=True, exist_ok=False)
    outputs = {}
    for index, (key, (source, body, face, transform)) in enumerate(cels.items(), 1):
        outputs[key] = {}
        for role, layer in (("file", source), ("body", body), ("face", face)):
            if layer is None:
                continue
            name = f"{index:03d}-{role}.png"
            resample = (
                Image.Resampling.BICUBIC if role == "file" else Image.Resampling.NEAREST
            )
            layer.transform(
                size, Image.Transform.AFFINE, transform, resample=resample
            ).save(args.output / name)
            outputs[key][role] = name

    result = []
    for row, ms in zip(rows, delays, strict=True):
        squash = row.get("squash", {})
        key = tuple(row.get(role) for role in ("file", "source_frame", "body", "face"))
        key += (
            *row.get("motion", [0, 0, 0]),
            squash.get("width", 0),
            squash.get("height", 0),
        )
        updated = {**row, **outputs[key], "ms": ms}
        updated.pop("source_frame", None)
        if "params" in updated:
            updated["params"] = parameter_images(updated["params"], root)
        result.append(updated)
    (args.output / "timing.json").write_text(
        json.dumps({"frames": result}, indent=2) + "\n"
    )


if __name__ == "__main__":
    cli(__doc__, configure, register)
