"""Production asset inventories, annotated crops, and cross-pack review sheets."""

import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

if __package__:
    from .common import output_path, read_json
else:
    from common import output_path, read_json

LEVELS = ("asset", "integration", "consistency")
BRIEFS = {
    "asset": "Compare each asset's views and states against the bible. Check silhouette, palette, scale, construction and resemblance to existing designs.",
    "integration": "Check the fit, grip, contact and overlaps in the integration sheets and in the relevant motion exposures. Call out any apparent resizing or detached parts.",
    "consistency": "Read each lineup row across the whole pack. Check repeated features, relative prop size, silhouette, the scale report and the final motion on light and dark.",
}


def inventory(project):
    return read_json(project / "assets.json").get("assets", {})


def prepare(root, names, source):
    assets = read_json(source).get("assets", {}) if source else {}
    templates = {
        "model": "Show front, side and three-quarter where useful. Record states, scale against the character, palette, line weight and construction.",
        "integration": "Show how it is held, worn, placed or layered. Record scale, contact points, overlap and the poses or effects that use it.",
    }
    for key, asset in assets.items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", key):
            raise ValueError(f"invalid asset name: {key!r}")
        uses = asset.get("uses", [])
        if not uses or len(set(uses)) != len(uses) or not set(uses) <= set(names):
            raise ValueError(f"{key}: uses must name one or more distinct pack emoji")
        folder = root / "images" / "assets" / key
        folder.mkdir(parents=True)
        asset.setdefault("status", "todo")
        for kind, instructions in templates.items():
            asset.setdefault(kind, [f"images/assets/{key}/{kind}.png"])
            if not asset[kind] or not all(
                isinstance(path, str) and Path(path).suffix.lower() == ".png"
                for path in asset[kind]
            ):
                raise ValueError(f"{key}: {kind} must list PNG reference paths")
            for file in asset[kind]:
                project_path(root, file).parent.mkdir(parents=True, exist_ok=True)
            (folder / f"{kind}.md").write_text(
                f"# {asset.get('name', key)} · {kind}\n\n{instructions}\n",
                encoding="utf-8",
            )
    return assets


def project_path(project, file):
    path = project / file
    if not path.resolve().is_relative_to(project.resolve()):
        raise ValueError(f"asset path leaves the project: {file}")
    return path


def drawing_references(assets, emoji):
    return {
        key: [*asset["model"], *asset["integration"]]
        for key, asset in assets.items()
        if emoji in asset["uses"]
    }


def crop(project, record):
    path = project_path(project, record["file"])
    with Image.open(path) as source:
        if "frame" in record:
            source.seek(record["frame"] - 1)
        art = source.convert("RGBA")
    if "box" not in record:
        return art
    box = record["box"]
    if (
        len(box) != 4
        or not all(type(value) is int for value in box)
        or not 0 <= box[0] < box[2] <= art.width
        or not 0 <= box[1] < box[3] <= art.height
    ):
        raise ValueError(f"{record['file']}: crop must lie inside the canvas")
    return art.crop(box)


def read_lineup(project, crops=None):
    manifest = read_json(crops or project / "lineup.json")
    names = list(read_json(project / "production.json")["emojis"])
    assets = inventory(project)
    if not assets:
        raise ValueError("declare assets in assets.json before building a lineup")
    rows = manifest["assets"]
    if set(rows) != set(assets):
        raise ValueError("lineup.json must cover every asset in assets.json")
    for key, row in rows.items():
        used_in = set(assets[key]["uses"])
        if set(row["appearances"]) != used_in or not all(row["appearances"].values()):
            raise ValueError(f"{key}: supply crops for {', '.join(sorted(used_in))}")
        if not row["references"]:
            raise ValueError(f"{key}: supply at least one reference crop")
    return names, rows


def lineup(args):
    names, rows = read_lineup(args.project, args.crops)
    width, height = 136, 110
    slate = "#e2e8ef"
    canvas = Image.new(
        "RGB", (width * (len(names) + 2), height * len(rows) + 44), slate
    )
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=13)
    for column, name in enumerate(("Asset", "Reference", *names)):
        draw.text((column * width + 12, 14), name, fill="#162736", font=font)
    for index, (key, row) in enumerate(rows.items()):
        y = 44 + height * index
        background = "#ffffff" if index % 2 == 0 else "#f1f4f7"
        draw.rectangle((0, y, canvas.width, y + height), fill=background)
        draw.text((12, y + 44), key, fill="#162736", font=font)
        for column, records in enumerate(
            [row["references"], *(row["appearances"].get(name, []) for name in names)],
            1,
        ):
            if not records:
                continue
            # Pack several states into the same cell when the reviewer supplied them.
            span = min(width - 12, height - 18)
            columns = 1 if len(records) == 1 else 2
            rows_needed = (len(records) + columns - 1) // columns
            tile = max(
                1, min(span, (width - 12) // columns, (height - 10) // rows_needed)
            )
            for position, record in enumerate(records):
                art = crop(args.project, record)
                unit = record.get("pixels_per_unit", max(art.size))
                if (
                    type(unit) not in (int, float)
                    or not math.isfinite(unit)
                    or unit <= 0
                ):
                    raise ValueError("pixels_per_unit must be finite and positive")
                scale = tile / max(unit, *art.size)
                art = art.resize(
                    tuple(max(1, round(axis * scale)) for axis in art.size),
                    Image.Resampling.LANCZOS,
                )
                x = (
                    column * width
                    + (width - tile * columns) // 2
                    + position % columns * tile
                )
                top = (
                    y + (height - tile * rows_needed) // 2 + position // columns * tile
                )
                canvas.paste(
                    art,
                    (x + (tile - art.width) // 2, top + (tile - art.height) // 2),
                    art,
                )
    output = output_path(args.output)
    canvas.save(output)
    return {"file": str(output), "assets": len(rows), "emojis": names}


def review_sources(project, level, asset_name, emoji):
    assets = inventory(project)
    if not assets:
        raise ValueError(
            "declare assets in assets.json before requesting an asset review"
        )
    if asset_name is not None and asset_name not in assets:
        raise ValueError(f"unknown asset {asset_name!r}")
    selected = {asset_name: assets[asset_name]} if asset_name else assets
    if emoji is not None:
        selected = {
            key: asset for key, asset in selected.items() if emoji in asset["uses"]
        }
        if not selected:
            raise ValueError(f"no selected assets are used in {emoji!r}")
    sources = [
        Path("style.md"),
        Path("assets.json"),
        Path("images/model"),
        Path("review") / f"{level}.md",
    ]
    for key, asset in selected.items():
        folder = Path("images/assets") / key
        sources.extend([folder / "model.md", *(Path(file) for file in asset["model"])])
        if level != "asset":
            sources.extend(
                [
                    folder / "integration.md",
                    *(Path(file) for file in asset["integration"]),
                ]
            )
    if level == "integration":
        for name in dict.fromkeys(
            name
            for asset in selected.values()
            for name in asset["uses"]
            if emoji is None or name == emoji
        ):
            folder = Path("emojis") / name
            sources.extend(
                folder / file
                for file in ("storyboard.md", "x-sheet.json", "keys", "cels", "strips")
            )
    if level == "consistency":
        sources.extend(
            Path(file)
            for file in (
                "lineup.json",
                "lineup.png",
                "prop-drift.json",
                "scale-check.json",
                "result/pack",
            )
        )
    return sources
