"""Drive a production pack until it completes or needs native image-tool output."""

import base64
import json
import os
import re
import subprocess
import sys
from argparse import Namespace
from io import BytesIO
from pathlib import Path
from shutil import copy2, copytree
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image

if __package__:
    from . import common, production
else:
    import common
    import production

BEATS = (
    ("rest", "Opening", "Show the starting pose."),
    ("lift", "Anticipation", "Edit the pose partway toward the main action."),
    ("peak", "Peak", "Show the most legible moment of the action."),
    ("settle", "Settle", "Edit back toward the opening pose."),
)


def configure(subcommands):
    parser = subcommands.add_parser("make", help=__doc__)
    parser.add_argument("idea", nargs="?")
    parser.add_argument("--project", type=Path, default=Path("forge-project"))
    parser.add_argument("--refs", type=Path, nargs="+", default=[])
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--target", choices=("slack", "generic"), default="slack")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--static", action="store_true")
    mode.add_argument("--animated", action="store_true")
    parser.add_argument(
        "--yes", action="store_true", help="skip optional approval gates"
    )
    parser.add_argument(
        "--gate", choices=production.STAGES, action="append", default=[]
    )
    parser.add_argument(
        "--approve", action="store_true", help="approve the pending optional gate"
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--generator",
        type=Path,
        help="trusted Python adapter that accepts a task JSON path",
    )
    parser.add_argument("--scales", help="comma-separated distribution sizes")
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="keep import placement without torso registration",
    )


def save_state(path, state):
    temp = path.with_suffix(".tmp")
    production.save_json(temp, state)
    temp.replace(path)


def start(args, root):
    if not args.idea or not args.idea.strip() or args.count < 1:
        raise ValueError("provide an idea and a positive --count")
    if args.generator and not args.generator.is_file():
        raise ValueError("--generator must point to a Python adapter file")
    scales = [int(scale) for scale in args.scales.split(",")] if args.scales else [512]
    if any(scale < 1 for scale in scales):
        raise ValueError("--scales must be positive")
    master_size = max(*scales, 128 if args.target == "slack" else 256)
    for ref in args.refs:
        with Image.open(ref) as source:
            source.verify()
    slug = (
        re.sub(r"[^a-z0-9]+", "-", args.idea.lower()).strip("-")[:28].rstrip("-")
        or "emoji"
    )
    names = (
        [slug]
        if args.count == 1
        else [f"{slug}-{index}" for index in range(1, args.count + 1)]
    )
    root.mkdir(parents=True)
    production.scaffold(root, names)
    (root / "brief.md").write_text(
        f"# Pack brief\n\n{args.idea.strip()}\n", encoding="utf-8"
    )
    with (root / "style.md").open("a", encoding="utf-8") as bible:
        bible.write(f"\n## Starting idea\n\n{args.idea.strip()}\n")
    refs = []
    if args.refs:
        (root / "references").mkdir()
        for index, source in enumerate(args.refs, 1):
            path = root / "references" / f"{index:02d}.png"
            common.image(source).save(path)
            refs.append(path.relative_to(root).as_posix())
    for index, name in enumerate(names, 1):
        path = root / "emojis" / name
        beats = (BEATS[0],) if args.static else BEATS
        direction = f"{args.idea.strip()} · emoji {index} of {args.count}. Match the approved references. One transparent square cel."
        panels = [
            {
                "id": key,
                "file": f"panels/{row:03d}.png",
                "beat": title,
                "action": description,
                "ms": 350,
            }
            for row, (key, title, description) in enumerate(beats, 1)
        ]
        production.save_json(
            path / "storyboard.json",
            {
                "style_sheet": "../../images/model/three-quarter.png",
                "direction": direction,
                "panels": panels,
            },
        )
        (path / "storyboard.md").write_text(
            f"# {name} storyboard\n\n{direction}\n\n"
            + "\n".join(f"- {panel['beat']} — {panel['action']}" for panel in panels)
            + "\n",
            encoding="utf-8",
        )
        production.save_json(
            path / "x-sheet.json",
            {
                "frames": [
                    {
                        "panel": panel["id"],
                        "ms": panel["ms"],
                        **(
                            {"key_pose": f"keys/{row:03d}.png"} if row in {1, 3} else {}
                        ),
                    }
                    for row, panel in enumerate(panels, 1)
                ]
            },
        )
    return {
        "idea": args.idea,
        "names": names,
        "target": args.target,
        "static": args.static,
        "refs": refs,
        "phase": 0,
        "gates": args.gate,
        "yes": args.yes,
        "generator": str(args.generator.resolve()) if args.generator else None,
        "scales": args.scales,
        "master_size": master_size,
        "register": not args.no_register,
    }


def task(path, prompt, references):
    return {
        "kind": "image",
        "output": str(path),
        "prompt": prompt,
        "references": list(dict.fromkeys(str(ref) for ref in references)),
    }


def data_url(path):
    stream = BytesIO()
    common.image(path).save(stream, format="PNG")
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(
        "ascii"
    )


def call_api(job, key):
    payload = {
        "model": os.getenv("FORGE_IMAGE_MODEL", "gpt-image-2.5-flare"),
        "prompt": job["prompt"],
        "size": "1024x1024",
        "background": "transparent",
    }
    endpoint = "generations"
    if job["references"]:
        endpoint = "edits"
        payload["images"] = [
            {"image_url": data_url(Path(ref))} for ref in job["references"]
        ]
    request = Request(
        "https://api.openai.com/v1/images/" + endpoint,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=300) as response:
            result = base64.b64decode(
                json.load(response)["data"][0]["b64_json"], validate=True
            )
    except HTTPError as error:
        raise ValueError(
            f"image API returned HTTP {error.code}; resume after checking the API key or model"
        ) from error
    except (URLError, KeyError, ValueError) as error:
        raise ValueError(
            "image API did not return an image; check the model or supply this task with a native tool"
        ) from error
    with Image.open(BytesIO(result)) as art:
        art.convert("RGBA").save(job["output"])


def ensure(root, state, job):
    output = Path(job["output"])
    if not output.is_file():
        output.parent.mkdir(parents=True, exist_ok=True)
        source = production.save_json(root / "next-task.json", job)
        if state["generator"]:
            generated = subprocess.run(
                [sys.executable, state["generator"], str(source)],
                check=False,
                capture_output=True,
                text=True,
            )
            if generated.returncode:
                raise ValueError(
                    f"image generator exited {generated.returncode}: {generated.stderr.strip()[-600:]}"
                )
        elif key := os.getenv("FORGE_IMAGE_API_KEY"):
            call_api(job, key)
        else:
            return False
    if not output.is_file():
        raise ValueError(f"the generator did not write {output}")
    with Image.open(output) as art:
        art.verify()
    log_path = root / "image-prompts.jsonl"
    output_name = output.relative_to(root).as_posix()
    known = (
        log_path.read_text(encoding="utf-8").splitlines() if log_path.is_file() else []
    )
    if not any(json.loads(line)["output"] == output_name for line in known):
        record = {
            **job,
            "output": output_name,
            "seed": None,
            "references": [
                str(Path(ref).resolve().relative_to(root))
                if Path(ref).resolve().is_relative_to(root)
                else str(ref)
                for ref in job["references"]
            ],
        }
        with log_path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(record) + "\n")
    return True


def images_for_stage(root, state, stage):
    model = root / "images/model/three-quarter.png"
    expression = root / "images/expressions/neutral.png"
    pose = root / "images/poses/rest.png"
    if stage == "bible":
        yield task(
            model,
            f"Draw a model reference for this idea: {state['idea']}. One centered character or graphic on transparent square canvas.",
            [root / ref for ref in state["refs"]],
        )
        yield task(
            expression,
            "Edit this approved model into a reference expression for the planned reaction. Keep the same design.",
            [model],
        )
        yield task(
            pose,
            "Edit this model into a legible rest pose reference. Keep the palette, proportions and silhouette features.",
            [model, expression],
        )
        return
    for name in state["names"]:
        emoji = root / "emojis" / name
        board = common.read_json(emoji / "storyboard.json")
        if stage == "storyboard":
            for panel in board["panels"]:
                if panel.get("file"):
                    yield task(
                        emoji / panel["file"],
                        f"{board['direction']} Thumbnail panel. {panel['action']}",
                        [model, expression, pose],
                    )
        elif stage == "keys":
            x_sheet = common.read_json(emoji / "x-sheet.json")
            panels = {panel["id"]: panel for panel in board["panels"]}
            for row in x_sheet["frames"]:
                if row.get("key_pose"):
                    panel = panels.get(row.get("panel"), {})
                    refs = [model, expression, pose]
                    if panel.get("file"):
                        refs.append(emoji / panel["file"])
                    yield task(
                        emoji / row["key_pose"],
                        f"{board['direction']} Key pose. {row.get('pose') or panel.get('action', '')}",
                        refs,
                    )
        elif stage == "inbetweens":
            plan = common.read_json(emoji / "plan.json")
            for row in plan["frames"]:
                output = emoji / row["file"]
                refs = [emoji / ref for ref in row["references"].values() if ref]
                if row["key_frame"] and not output.exists():
                    copy2(emoji / row["references"]["key_pose"], output)
                yield task(output, row["prompt"], refs)


def run_step(root, state, stage, invoke):
    def call(*args):
        return invoke("forge", *args, "--json")

    for name in state["names"]:
        emoji = root / "emojis" / name
        if stage in {"bible", "storyboard"}:
            call("sheets", "--project", root, "--emoji", name)
        elif stage == "keys":
            call(
                "plan",
                emoji / "storyboard.json",
                emoji / "plan.json",
                "--x-sheet",
                emoji / "x-sheet.json",
            )
        elif stage == "inbetweens":
            cels = emoji / "cels"
            use_registration = state["register"] and not state["static"]
            intermediate = emoji / "imported" if use_registration else cels
            if not intermediate.exists():
                plan = common.read_json(emoji / "plan.json")
                files = [emoji / row["file"] for row in plan["frames"]]
                for file in files:
                    with Image.open(file) as art:
                        if min(art.size) < state["master_size"]:
                            raise ValueError(
                                f"{file}: provide native art at {state['master_size']} px or larger for the requested scales"
                            )
                call(
                    "import",
                    emoji / "raw",
                    intermediate,
                    "--size",
                    state["master_size"],
                    "--scale",
                    "shared",
                    "--timing-spec",
                    emoji / "plan.json",
                )
            if use_registration and not cels.exists():
                call("register", intermediate / "timing.json", cels)
            call(
                "drift",
                cels / "timing.json",
                root / "images/model",
                emoji / "drift.json",
            )
            call(
                "strips",
                cels / "timing.json",
                emoji / "strips/cels.png",
                "--size",
                32,
                128,
                512,
            )
    if stage == "effects":
        entries = []
        for name in state["names"]:
            emoji = root / "emojis" / name
            rows, _ = common.read_timing(emoji / "cels/timing.json")
            entry = {
                "name": name,
                "static": state["static"],
                "register": False,
                "frames": [
                    {
                        **row,
                        **{
                            key: str(emoji / "cels" / row[key])
                            for key in ("file", "body", "face")
                            if key in row
                        },
                    }
                    for row in rows
                ],
            }
            for effect in (emoji / "effect.json", emoji / "effect.frag"):
                if effect.is_file():
                    entry["effect"] = str(effect)
                    break
            entries.append(entry)
        manifest = production.save_json(
            root / "source-pack.json", {"target": state["target"], "emojis": entries}
        )
        if not (root / "result").exists():
            options = ["--scales", state["scales"]] if state["scales"] else []
            call("all", manifest, root / "result", *options)
        for name in state["names"]:
            emoji = root / "emojis" / name
            treated = (
                root
                / "result"
                / "exports"
                / (name + (".png" if state["static"] else ".gif"))
            )
            (emoji / "effects").mkdir(exist_ok=True)
            copy2(treated, emoji / "effects" / treated.name)
            copy2(
                root / "result" / "strips" / f"{name}.png",
                emoji / "strips" / "export.png",
            )
    if stage == "final":
        for name in state["names"]:
            emoji = root / "emojis" / name
            copy2(root / "result" / "checks.json", emoji / "checks.json")
            if not (emoji / "final").is_dir():
                copytree(emoji / "effects", emoji / "final")
            overview = (
                root
                / "result/pack"
                / ("overview.png" if state["static"] else "overview.gif")
            )
            copy2(overview, emoji / "final" / overview.name)


def run(args, invoke):
    root = args.project.resolve()
    path = root / "make.json"
    state = common.read_json(path) if args.resume else start(args, root)
    if args.generator and args.resume:
        if not args.generator.is_file():
            raise ValueError("--generator must point to a Python adapter file")
        state["generator"] = str(args.generator.resolve())
    state["yes"] = state["yes"] or args.yes
    save_state(path, state)
    approve = args.approve
    while state["phase"] < len(production.STAGES):
        step = production.STAGES[state["phase"]]
        for job in images_for_stage(root, state, step):
            if not ensure(root, state, job):
                return {
                    "status": "needs-image",
                    "stage": step,
                    "task": job,
                    "project": str(root),
                }
        run_step(root, state, step, invoke)
        if step in state["gates"] and not (state["yes"] or approve):
            packs = [
                production.review_pack(root, name, step, None)
                for name in state["names"]
            ]
            pending = {
                "kind": "review",
                "review_packs": packs,
                "resume": "Run forge make --resume --approve after review.",
            }
            production.save_json(root / "next-task.json", pending)
            return {
                "status": "needs-review",
                "stage": step,
                "task": pending,
                "project": str(root),
            }
        for name in state["names"]:
            production.stage(
                Namespace(
                    project=root,
                    emoji=name,
                    stage=step,
                    review="pass",
                    notes="Optional review approved."
                    if approve
                    else "Automated hand-off. Expected files present. Review art and any drift flags visually.",
                )
            )
        approve = False
        state["phase"] += 1
        save_state(path, state)
    (root / "next-task.json").unlink(missing_ok=True)
    pack = root / "result/pack"
    overview = pack / ("overview.png" if state["static"] else "overview.gif")
    return {
        "status": "complete",
        "project": str(root),
        "pack": str(pack),
        "overview": str(overview),
        "zip": str(pack.with_suffix(".zip")),
    }
