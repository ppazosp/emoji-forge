"""Scaffold production artifacts, render review sheets, and track hand-offs."""

import json
from argparse import Namespace
from datetime import UTC, datetime
from pathlib import Path
from shutil import copy2, make_archive
from textwrap import shorten

from PIL import Image, ImageDraw, ImageFont

if __package__:
    from . import pack_assets
    from .common import gif_delays, image, image_files, read_json
else:
    import pack_assets
    from common import gif_delays, image, image_files, read_json

SHEET_GROUPS = ("model", "expressions", "poses")
STAGES = ("bible", "storyboard", "keys", "inbetweens", "effects", "final")
REVIEW_BRIEFS = {
    "bible": "Compare the reference poses and palette. Check the silhouette, palette and name for resemblance to recognizable existing characters.",
    "storyboard": "Check whether the storyboard and timed thumbnail animatic communicate the idea.",
    "keys": "Compare the key drawings with the model, expression and pose sheets and the storyboard.",
    "inbetweens": "Inspect the cels, strips and timing. Call out off-model drawings, abrupt spacing, missed holds, and unintended scale or anchor changes by frame.",
    "effects": "Compare the clean and treated frames. Check that an impact flash or burst begins on contact and clears the character as it decays.",
    "final": "Check the delivered scale, frame and byte limits, then inspect the overview and final strips at their intended size.",
}
STAGE_FILES = {
    "bible": ("images/model", "references"),
    "storyboard": ("@storyboard.md", "@storyboard.json", "@panels"),
    "keys": (
        "expressions.md",
        "poses.md",
        "images/expressions",
        "images/poses",
        "@storyboard.md",
        "@keys",
    ),
    "inbetweens": (
        "@storyboard.md",
        "@x-sheet.json",
        "@raw",
        "@cels",
        "@strips",
        "@drift.json",
    ),
    "effects": ("@storyboard.md", "@x-sheet.json", "@cels", "@effects", "@strips"),
    "final": ("@storyboard.md", "@final", "@checks.json", "@strips"),
}
STAGE_SHEETS = {
    "bible": ("model.png",),
    "storyboard": ("model.png", "storyboard.png", "animatic.gif"),
    "keys": ("model.png", "expressions.png", "poses.png", "storyboard.png"),
    "inbetweens": ("model.png", "poses.png", "storyboard.png", "animatic.gif"),
    "effects": ("model.png", "storyboard.png"),
    "final": ("storyboard.png",),
}
TEMPLATES = {
    "style.md": """# Character bible / model sheet
\n## References and turnaround\n\nAdd useful views of the character in `images/model/`. Which front, three-quarter, side or back views are worth drawing?\n
## Construction\n\nNote the proportions, silhouette, line weight and texture that matter for this character.\n
## Palette\n\nRecord hex values for recurring fills and outlines when helpful.\n
## Do and don't\n\nRecord examples of what stays recognizable, what can change and where there is room to experiment.\n""",
    "expressions.md": "# Expression sheet\n\nPut the expression references you want to reuse in `images/expressions/` and describe where they fit.\n",
    "poses.md": "# Pose, hand and prop sheet\n\nPut reusable key poses, hands and props in `images/poses/`. Note any attachment points or scale choices.\n",
}


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def scaffold(root, names, asset_file=None):
    assets = {}
    registry = pack_assets.prepare(root, names, asset_file)
    (root / "images/assets").mkdir(parents=True, exist_ok=True)
    (root / "images/assets/README.md").write_text(
        "# Asset sheets\n\nDeclare props, effects and recurring design features in assets.json. "
        "Add each asset's model views and integration drawing before planning its cels.\n",
        encoding="utf-8",
    )
    for group in SHEET_GROUPS:
        (root / "images" / group).mkdir(parents=True, exist_ok=True)
    for name, template in TEMPLATES.items():
        (root / name).write_text(template, encoding="utf-8")
    for name in names:
        emoji = root / "emojis" / name
        for directory in ("panels", "keys", "raw"):
            (emoji / directory).mkdir(parents=True)
        (emoji / "storyboard.md").write_text(
            f"# {name} storyboard\n\nSketch the beats, action, expression and timing. Add panel PNGs to `panels/`.\n",
            encoding="utf-8",
        )
        save_json(
            emoji / "storyboard.json",
            {
                "style_sheet": "../../images/model/three-quarter.png",
                "asset_references": {
                    key: [f"../../{path}" for path in paths]
                    for key, paths in pack_assets.drawing_references(
                        registry, name
                    ).items()
                },
                "direction": "",
                "panels": [
                    {
                        "id": "opening",
                        "file": "panels/01.png",
                        "beat": "Opening",
                        "action": "",
                        "expression": "",
                        "ms": 400,
                    }
                ],
            },
        )
        save_json(
            emoji / "x-sheet.json",
            {
                "frames": [{"panel": "opening", "key_pose": "keys/01.png", "ms": 400}],
            },
        )
        assets[name] = (
            [{"asset": key} for key in pack_assets.drawing_references(registry, name)]
            if registry
            else [
                {"name": kind, "type": kind, "status": "todo", "file": ""}
                for kind in ("character", "prop", "effect", "background")
            ]
        )
    save_json(root / "assets.json", {"emojis": assets, "assets": registry})
    save_json(
        root / "production.json",
        {
            "emojis": {name: {"stage": "bible", "reviews": []} for name in names},
        },
    )


def select(root, name):
    state = read_json(root / "production.json")
    if name is None:
        if len(state["emojis"]) != 1:
            raise ValueError("select an emoji with --emoji")
        name = next(iter(state["emojis"]))
    if name not in state["emojis"]:
        raise ValueError(f"unknown emoji {name!r}")
    return state, name


def tile(label, path):
    canvas = Image.new("RGBA", (192, 216), "#eef3f7")
    art = image(path)
    art.thumbnail((176, 176), Image.Resampling.LANCZOS)
    canvas.alpha_composite(art, ((192 - art.width) // 2, (184 - art.height) // 2))
    font = ImageFont.load_default(size=13)
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (96, 195),
        shorten(label.replace("-", " "), width=28),
        fill="#142033",
        font=font,
        anchor="mm",
    )
    return canvas.convert("RGB")


def grid(tiles):
    columns = min(4, len(tiles))
    rows = (len(tiles) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * 192, rows * 216), "#e2e8ee")
    for index, panel in enumerate(tiles):
        canvas.paste(panel, (index % columns * 192, index // columns * 216))
    return canvas


def sheets(args):
    _, name = select(args.project, args.emoji)
    output = args.out or args.project / "review" / name / "sheets"
    output.mkdir(parents=True, exist_ok=True)
    written = []
    for group in SHEET_GROUPS:
        sources = [
            path
            for path in image_files(args.project / "images" / group)
            if path.name != "body-mask.png"
        ]
        if sources:
            target = output / f"{group}.png"
            grid([tile(path.stem, path) for path in sources]).save(target)
            written.append(target)
    emoji = args.project / "emojis" / name
    board = read_json(emoji / "storyboard.json")
    panels = [
        (row, emoji / row["file"]) for row in board.get("panels", []) if row.get("file")
    ]
    missing = [str(path) for _, path in panels if not path.is_file()]
    ready = [
        (row, tile(row.get("beat") or row["id"], path))
        for row, path in panels
        if path.is_file()
    ]
    if ready:
        times = gif_delays([row.get("ms", 200) for row, _ in ready])
        drawings = [drawing for _, drawing in ready]
        strip, animation = output / "storyboard.png", output / "animatic.gif"
        grid(drawings).save(strip)
        drawings[0].save(
            animation,
            save_all=True,
            append_images=drawings[1:],
            duration=times,
            loop=0,
            disposal=2,
        )
        written.extend((strip, animation))
    return {"files": [str(path) for path in written], "missing_panels": missing}


def timestamp():
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")


def review_pack(root, name, step, destination, review=None):
    shelf = root / "review" / name
    output = destination or shelf / f"{step}-{timestamp()}"
    prefix = f"emojis/{name}/"
    docs = ["style.md", "assets.json", *STAGE_FILES[step]]
    refs = [Path(path.replace("@", prefix, 1)) for path in docs]
    if step == "storyboard":
        board = root / prefix / "storyboard.json"
        for panel in read_json(board).get("panels", []) if board.is_file() else []:
            if panel.get("file"):
                path = (board.parent / panel["file"]).resolve()
                if path.is_relative_to(root.resolve()):
                    refs.append(path.relative_to(root.resolve()))
    else_dir = shelf / "sheets"
    refs.extend((else_dir / asset).relative_to(root) for asset in STAGE_SHEETS[step])
    return archive_review(
        root, output, refs, f"{name} / {step}", REVIEW_BRIEFS[step], review
    )


def archive_review(root, output, refs, title, brief, review=None):
    if output.exists() or output.with_name(output.name + ".zip").exists():
        raise ValueError(f"choose a new review pack path: {output}")
    sources = []
    # Gather before making the destination, so a stray source subfolder cannot include the output.
    for path in refs:
        source = root / path
        candidates = source.rglob("*") if source.is_dir() else [source]
        sources.extend(
            file
            for file in candidates
            if file.is_file() and not file.name.startswith(".")
        )
    output.mkdir(parents=True)
    for source in dict.fromkeys(sources):
        target = output / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(source, target)
    note = f"\nVerdict: {review['result']}\n\n{review['notes']}\n" if review else ""
    (output / "REVIEW.md").write_text(
        f"# {title}\n\n{brief}\n\nReturn pass or fail, with notes and frame or panel references where useful.\n{note}",
        encoding="utf-8",
    )
    archive = make_archive(str(output), "zip", output)
    return {
        "path": str(output),
        "archive": archive,
        "files": [str(file.relative_to(root)) for file in dict.fromkeys(sources)],
    }


def stage(args):
    state, name = select(args.project, args.emoji)
    record = state["emojis"][name]
    record["stage"] = args.stage
    if args.review:
        review = {"stage": args.stage, "result": args.review, "notes": args.notes or ""}
        snapshot = review_pack(args.project, name, args.stage, None, review)
        review["snapshot"] = str(
            Path(snapshot["archive"]).resolve().relative_to(args.project.resolve())
        )
        record["reviews"].append(review)
    save_json(args.project / "production.json", state)
    return {"emoji": name, **record}


def status(args):
    state = read_json(args.project / "production.json")
    if args.emoji:
        _, name = select(args.project, args.emoji)
        state["emojis"] = {name: state["emojis"][name]}
    return state


def handoff(args):
    if args.stage in pack_assets.LEVELS:
        if args.stage == "consistency" and (args.asset or args.emoji):
            raise ValueError("consistency review covers the whole pack")
        refs = pack_assets.review_sources(
            args.project, args.stage, args.asset, args.emoji
        )
        if args.stage == "consistency" and not (args.project / "lineup.png").is_file():
            pack_assets.lineup(
                Namespace(
                    project=args.project, output=args.project / "lineup.png", crops=None
                )
            )
        output = args.out or args.project / "review" / f"{args.stage}-{timestamp()}"
        return archive_review(
            args.project, output, refs, args.stage, pack_assets.BRIEFS[args.stage]
        )
    _, name = select(args.project, args.emoji)
    return review_pack(args.project, name, args.stage, args.out)


def configure(subcommands):
    lineup = subcommands.add_parser("lineup", help="show every asset across the pack")
    lineup.add_argument("project", type=Path)
    lineup.add_argument("output", type=Path)
    lineup.add_argument("--crops", type=Path, help="override project/lineup.json")
    for name, help_ in (
        ("sheets", "render contact sheets and a thumbnail animatic"),
        ("stage", "record a stage or review"),
        ("status", "show the production stage and reviews per emoji"),
        ("review-pack", "bundle materials for one review stage"),
    ):
        parser = subcommands.add_parser(name, help=help_)
        parser.add_argument("--project", type=Path, default=Path("."))
        parser.add_argument("--emoji")
        if name in {"stage", "review-pack"}:
            parser.add_argument(
                "stage",
                choices=STAGES + pack_assets.LEVELS
                if name == "review-pack"
                else STAGES,
            )
        if name == "review-pack":
            parser.add_argument(
                "--asset",
                help="select a specific asset for an asset or integration review",
            )
        if name in {"sheets", "review-pack"}:
            parser.add_argument("--out", type=Path)
        if name == "stage":
            parser.add_argument("--review", choices=("pass", "fail"))
            parser.add_argument("--notes")


COMMANDS = {
    "sheets": sheets,
    "stage": stage,
    "status": status,
    "review-pack": handoff,
    "lineup": pack_assets.lineup,
}
