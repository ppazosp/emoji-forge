"""Thread a storyboard and X-sheet into a reference-aware list of image edits."""

import json
import os
from pathlib import Path

if __package__:
    from .common import add_timing_flags, cli, exposure_delays, output_path, read_json
else:
    from common import add_timing_flags, cli, exposure_delays, output_path, read_json


def configure(parser):
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("output", type=Path, help="plan.json or plan.md")
    parser.add_argument(
        "--x-sheet", type=Path, help="exposure rows, optionally with a timing spec"
    )
    parser.add_argument(
        "--frames-dir",
        type=Path,
        default=Path("raw"),
        help="path relative to the plan, or absolute",
    )
    add_timing_flags(parser)


def relative_to_plan(path, plan):
    return Path(os.path.relpath(path.resolve(), plan.parent.resolve())).as_posix()


def render_plan(board, exposures, args):
    frames = exposures["frames"]
    spec = read_json(args.timing_spec) if args.timing_spec else exposures.get("timing")
    delays = exposure_delays(frames, spec, args.frame_ms)
    style = relative_to_plan(args.storyboard.parent / board["style_sheet"], args.output)
    key_root = (args.x_sheet or args.storyboard).parent
    keys = {
        index: relative_to_plan(key_root / row["key_pose"], args.output)
        for index, row in enumerate(frames, 1)
        if row.get("key_pose")
    }
    if not keys:
        raise ValueError("mark at least one exposure with a key_pose reference")
    panels = {panel["id"]: panel for panel in board.get("panels", [])}
    items = []
    for index, (row, ms) in enumerate(zip(frames, delays, strict=True), 1):
        panel = panels[row["panel"]] if row.get("panel") else {}
        pose = row.get("pose") or panel.get("action")
        if not pose:
            raise ValueError(
                f"frame {index:02d}: supply a pose or a storyboard panel action"
            )
        path = (args.frames_dir / f"{index:03d}.png").as_posix()
        nearest = min(keys, key=lambda mark: abs(mark - index))
        parts = [
            f"Frame {index:02d}/{len(frames):02d}: {pose}",
            f"Expression: {panel['expression']}" if panel.get("expression") else "",
            board.get("direction", ""),
        ]
        items.append(
            {
                "file": path,
                "ms": ms,
                "key_frame": index in keys,
                "references": {
                    "previous_frame": items[-1]["file"] if items else None,
                    "key_pose": keys[nearest],
                    "style_sheet": style,
                },
                "prompt": "\n".join(filter(None, parts)),
            }
        )
    return {"durations_ms": delays, "frames": items}


def run(args):
    suffix = args.output.suffix.lower()
    if suffix not in {".json", ".md"}:
        raise ValueError("choose a .json or .md plan output")
    board = read_json(args.storyboard)
    exposures = read_json(args.x_sheet) if args.x_sheet else board
    plan = render_plan(board, exposures, args)
    if suffix == ".json":
        content = json.dumps(plan, indent=2)
    else:
        blocks = ["# Frame edit plan"]
        for entry in plan["frames"]:
            refs = "\n".join(
                f"- {label.replace('_', ' ').capitalize()}  `{path or 'none'}`"
                for label, path in entry["references"].items()
            )
            blocks.append(
                f"## {entry['file']} · {entry['ms']:g} ms\n\n{entry['prompt']}\n\n{refs}"
            )
        content = "\n\n".join(blocks)
    output_path(args.output).write_text(content + "\n", encoding="utf-8")


if __name__ == "__main__":
    cli(__doc__, configure, run)
