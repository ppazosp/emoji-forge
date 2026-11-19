"""Build the Sprout studio example using the optional Python animation hook."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FORGE = ROOT / "skills/emoji-forge/scripts/forge.py"
SCALE = 4
INK = "#172c3a"
FILL = "#7de1bf"
SHADE = "#4ab69b"
CREAM = "#f9ffed"


def bounds(coordinates):
    return tuple(round(value * SCALE) for value in coordinates)


def draw_cel(expression, action, amount):
    art = Image.new("RGBA", (128 * SCALE, 128 * SCALE))
    draw = ImageDraw.Draw(art)
    body = Image.new("L", art.size)
    face = Image.new("L", art.size)
    face_draw = ImageDraw.Draw(face)

    def line(points, fill=INK, width=3, pen=draw):
        pen.line(bounds(points), fill=fill, width=width * SCALE, joint="curve")

    def oval(box, fill, outline=None, width=2, pen=draw):
        pen.ellipse(bounds(box), fill=fill, outline=outline, width=width * SCALE)

    def round_box(box, radius, fill, outline=None, width=2, pen=draw):
        pen.rounded_rectangle(bounds(box), radius * SCALE, fill, outline, width * SCALE)

    def limb(points):
        line(points, CREAM, 5)
        line(points)

    # Each exposure is a full drawing. Body geometry is fixed by the style sheet.
    round_box((42, 90, 57, 103), 6, SHADE, INK)
    round_box((71, 90, 86, 103), 6, SHADE, INK)
    limb((62, 38, 62, 24, 74, 17))
    oval((68, 14, 84, 23), SHADE, INK)
    oval((52, 16, 63, 25), FILL, INK)
    round_box((29, 31, 99, 96), 25, CREAM, width=3)
    round_box((32, 34, 96, 93), 23, FILL, INK, 3)
    round_box((32, 34, 96, 93), 23, 255, pen=ImageDraw.Draw(body))
    oval((44, 46, 51, 49), "#b5f5d9")
    oval((54, 43, 58, 46), "#b5f5d9")
    oval((44, 65, 51, 69), "#f69b93")
    oval((77, 65, 84, 69), "#f69b93")

    if expression in {"happy", "blink"}:
        for x in (53, 75):
            points = (x - 4, 61, x, 57 if expression == "happy" else 61, x + 4, 61)
            line(points)
            line(points, 255, pen=face_draw)
    else:
        for x in (53, 75):
            box = (x - 2, 56, x + 2, 62)
            oval(box, INK)
            oval(box, 255, pen=face_draw)

    if expression == "happy":
        round_box((55, 66, 73, 79), 6, INK)
        round_box((55, 66, 73, 79), 6, 255, pen=face_draw)
        oval((59, 72, 69, 77), "#fa999e")
    elif expression == "sip":
        oval((61, 66, 67, 72), INK)
        oval((61, 66, 67, 72), 255, pen=face_draw)
    else:
        points = (58, 69, 62, 72, 66, 72, 70, 69)
        line(points, width=2)
        line(points, 255, width=2, pen=face_draw)

    if action == "wave":
        x = 106 + 5 * amount
        y = 80 - 32 * min(1, abs(amount)) - 9 * amount
        limb((92, 70, 101, 76 - 16 * abs(amount), x, y))
        oval((x - 5, y - 7, x + 5, y + 5), CREAM, INK)
        limb((34, 71, 26, 80))
        oval((22, 76, 30, 84), CREAM, INK)
    elif action == "coffee":
        y = 93 - amount * 13
        limb((36, 74, 43, 84 - 8 * amount, 54, y - 2))
        limb((92, 74, 84, 84 - 8 * amount, 75, y - 2))
        oval((72, y - 5, 81, y + 5), SHADE, INK)
        round_box((53, y - 8, 76, y + 10), 4, "#faac7e", INK)
        line((56, y - 5, 73, y - 5), "#ffe2b3", 2)
        oval((49, y - 6, 57, y + 2), CREAM, INK)
        oval((74, y - 6, 82, y + 2), CREAM, INK)
    else:
        y = 80 - amount * 38
        for x, direction in ((25, 1), (103, -1)):
            limb((x + direction * 9, 71, x + direction * 4, 75 - amount * 19, x, y))
            oval((x - 5, y - 5, x + 5, y + 5), CREAM, INK)
    return art, body, face


ANIMATIONS = {
    "wave": (
        "Say hello or goodbye.",
        [
            (0, "rest", 330),
            (0.25, "rest", 200),
            (0.55, "rest", 180),
            (0.87, "happy", 350),
            (-0.79, "happy", 260),
            (0.96, "happy", 290),
            (-0.66, "happy", 270),
            (0.78, "happy", 380),
            (0.44, "happy", 320),
            (0.18, "rest", 260),
            (0, "blink", 180),
            (0, "rest", 180),
        ],
    ),
    "coffee": (
        "Taking a coffee break.",
        [
            (0, "rest", 410),
            (0.18, "rest", 240),
            (0.44, "rest", 210),
            (0.72, "sip", 220),
            (0.91, "sip", 260),
            (1, "sip", 530),
            (0.93, "blink", 250),
            (0.69, "happy", 300),
            (0.43, "happy", 260),
            (0.18, "rest", 270),
            (0, "blink", 170),
            (0, "rest", 180),
        ],
    ),
    "hooray": (
        "Celebrate a small win.",
        [
            (0, "rest", 340),
            (0.16, "rest", 280),
            (0.32, "rest", 200),
            (0.58, "happy", 180),
            (0.89, "happy", 200),
            (1, "happy", 250),
            (0.95, "happy", 290),
            (1, "happy", 310),
            (0.91, "happy", 350),
            (0.64, "happy", 220),
            (0.36, "happy", 260),
            (0.12, "rest", 230),
            (0, "blink", 180),
            (0, "rest", 180),
        ],
    ),
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def exposures(name):
    return ANIMATIONS[name][1] if name in ANIMATIONS else [(0, "rest", 400)]


def animate(_frames, context):
    """Forge calls this hook to author cels and explicit geometry masks."""
    name = context["params"]["name"]
    result = []
    for amount, expression, ms in exposures(name):
        image, body, face = draw_cel(expression, name, amount)
        result.append({"image": image, "body": body, "face": face, "ms": ms})
    return result


def invoke(*args):
    subprocess.run([sys.executable, FORGE, *args, "--json"], check=True)


def save_cel(name, index, destination):
    amount, expression, _ = exposures(name)[index]
    draw_cel(expression, name, amount)[0].save(destination, optimize=True)


def build(output, args):
    names = [*ANIMATIONS, "hello"]
    invoke(
        "new",
        output,
        "--preset",
        "slack",
        *(arg for name in names for arg in ("--emoji", name)),
    )
    (output / "pack.json").unlink()
    notes = {
        "style.md": "# Sprout character bible\n\nRounded seafoam body with fixed feet and a two-leaf top. Navy outline (#172c3a), mint body (#7de1bf), dark leaf (#4ab69b), cream gloves (#f9ffed). The front view suits this set of small gestures.\n",
        "expressions.md": "# Expressions\n\nResting dot eyes, happy closed eyes, and a small round mouth for the sip.\n",
        "poses.md": "# Poses, hands and props\n\nRound cream mittens at the end of each arm. The peach mug stays between both hands.\n",
    }
    for path, content in notes.items():
        (output / path).write_text(content, encoding="utf-8")
    for group, filename, name, index in (
        ("model", "front", "hello", 0),
        ("expressions", "happy", "hooray", 5),
        ("expressions", "sip", "coffee", 5),
        ("poses", "wave", "wave", 3),
        ("poses", "cup", "coffee", 0),
    ):
        save_cel(name, index, output / "images" / group / f"{filename}.png")

    entries, inventory = [], {}
    for name in names:
        base = output / "emojis" / name
        poses = exposures(name)
        indices = [0] if name == "hello" else [0, 3, 5, len(poses) - 1]
        beats = ["Opening", "Anticipation", "Action", "Settle"]
        gestures = {
            "wave": ["Arm rests", "Mitten rises", "Mitten sways", "Arm lowers"],
            "coffee": ["Mug at belt", "Mug lifts", "Sips", "Mug lowers"],
            "hooray": ["Hands low", "Hands rise", "Cheers", "Hands lower"],
            "hello": ["Faces viewer"],
        }[name]
        panels = []
        for panel, index in enumerate(indices):
            filename = f"panels/{panel + 1:02}.png"
            save_cel(name, index, base / filename)
            rows = poses[
                index : indices[panel + 1] if panel + 1 < len(indices) else len(poses)
            ]
            panels.append(
                {
                    "id": str(panel + 1),
                    "file": filename,
                    "beat": beats[panel],
                    "action": gestures[panel],
                    "expression": poses[index][1],
                    "ms": sum(row[2] for row in rows),
                }
            )
        write_json(
            base / "storyboard.json",
            {
                "style_sheet": "../../images/model/front.png",
                "panels": panels,
                "direction": "Sprout is an optional Python-hook example.",
            },
        )
        use = ANIMATIONS[name][0] if name in ANIMATIONS else "A quiet greeting."
        (base / "storyboard.md").write_text(
            f"# {name}\n\n{use}\n\n"
            + "".join(
                f"- {p['beat']} · {p['action']} · {p['expression']} · {p['ms']} ms\n"
                for p in panels
            ),
            encoding="utf-8",
        )
        timing = []
        for index, (amount, expression, ms) in enumerate(poses):
            panel = next(
                p for p in reversed(range(len(indices))) if indices[p] <= index
            )
            row = {
                "panel": panels[panel]["id"],
                "pose": f"{expression}, gesture amount {amount}",
                "ms": ms,
            }
            if index in indices:
                row["key_pose"] = f"keys/{index + 1:03}.png"
                save_cel(name, index, base / row["key_pose"])
            save_cel(name, index, base / "raw" / f"{index + 1:03}.png")
            timing.append(row)
        write_json(base / "x-sheet.json", {"frames": timing})
        invoke("sheets", "--project", output, "--emoji", name)
        invoke(
            "plan",
            base / "storyboard.json",
            base / "plan.json",
            "--x-sheet",
            base / "x-sheet.json",
        )
        entry = {
            "name": name,
            "use": use,
            "static": name == "hello",
            "script": {
                "path": os.path.relpath(Path(__file__).resolve(), output),
                "params": {"name": name},
            },
        }
        if name == "hooray":
            entry["effect"] = {"shader": "sparkle", "params": {"anchor": [0.5, 0.76]}}
        entries.append(entry)
        inventory[name] = [
            {"name": "Sprout", "type": "character", "status": "approved"},
            {"name": "Transparent", "type": "background", "status": "approved"},
        ]
        if name == "coffee":
            inventory[name].append(
                {"name": "Mug", "type": "prop", "status": "approved"}
            )
        if name == "hooray":
            inventory[name].append(
                {"name": "Sparkle", "type": "effect", "status": "approved"}
            )

    write_json(output / "assets.json", {"emojis": inventory})
    manifest = output / "source-pack.json"
    write_json(manifest, {"target": "slack", "preview_ms": 1550, "emojis": entries})
    channel = ["--channel", args.channel] if args.channel else []
    invoke(
        "all",
        manifest,
        output / "result",
        "--backend",
        args.backend,
        "--allow-scripts",
        *channel,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--backend", default="auto", choices=["auto", "moderngl", "webgl"]
    )
    parser.add_argument("--channel")
    args = parser.parse_args()
    build(args.output, args)
