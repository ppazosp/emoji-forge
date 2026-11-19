"""Render the shader catalogue, overview grid and small-size review sheets."""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "emoji-forge"
CLI = SKILL / "scripts" / "forge.py"
EXPOSURE_MS = 100
EXPOSURES = 16
# Place effects on the available space around this particular cel.
PARAMS = {
    "fire": {"anchor": [0.25, 0.29], "intensity": 1.25},
    "god-rays": {"intensity": 1.7},
    "lightning": {"intensity": 1.5},
    "shockwave": {"intensity": 1.6},
    "sparkle": {"anchor": [0.68, 0.57], "intensity": 1.8},
}


def forge(*args):
    result = subprocess.run(
        [sys.executable, CLI, *map(str, args), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout or result.stderr)


def prepare(root, destination, cel=None):
    canvas = Image.new("RGBA", (512, 512))
    with Image.open(cel or ROOT / "assets/brand/logo.png") as source:
        art = source.convert("RGBA")
    art.thumbnail((384, 384), Image.Resampling.LANCZOS)
    canvas.paste(art, ((512 - art.width) // 2, (512 - art.height) // 2))
    canvas.save(root / "art.png")
    canvas.save(destination / "fixture.png", optimize=True)
    timing = root / "timing.json"
    timing.write_text(
        json.dumps({"frames": [{"file": "art.png", "ms": EXPOSURE_MS}] * EXPOSURES}),
        encoding="utf-8",
    )
    return timing


def build_effect(shader, timing, destination):
    work = timing.parent
    name = shader.stem
    config = work / f"{name}.json"
    config.write_text(
        json.dumps(
            {
                "shader": name,
                "bloom": name in {"bloom-glow", "fire"},
                "params": PARAMS.get(name, {}),
            }
        ),
        encoding="utf-8",
    )
    rendered = work / name
    forge("render", timing, config, rendered, "--backend", "moderngl", "--size", 512)
    gif = destination / f"{name}.gif"
    forge("fit", rendered / "timing.json", gif, "--preset", "slack")
    with Image.open(gif) as image:
        exposures = []
        for frame in ImageSequence.Iterator(image):
            rgba = frame.convert("RGBA")
            bounds = rgba.getbbox()
            if bounds and (min(bounds[:2]) == 0 or max(bounds[2:]) == image.width):
                raise ValueError(
                    f"{name}: frame {frame.tell() + 1} touches the canvas border"
                )
            reduced = rgba.resize((32, 32), Image.Resampling.LANCZOS)
            exposures.append((reduced, frame.info["duration"]))
    remaining_marks = iter((0, 400, 700, 1100, 1400))
    mark = next(remaining_marks)
    samples = []
    elapsed = 0
    for frame, duration in exposures:
        elapsed += duration
        while mark < elapsed:
            samples.append(frame)
            mark = next(remaining_marks, float("inf"))
    if elapsed != EXPOSURE_MS * EXPOSURES or len(exposures) < 2:
        raise ValueError(
            f"{name}: expected an animated {EXPOSURE_MS * EXPOSURES} ms GIF"
        )
    if len({frame.tobytes() for frame, _ in exposures}) < 2:
        raise ValueError(f"{name}: no visible change at 32 px after GIF fitting")
    return name, samples


def review_sheet(items, path, background, text):
    columns, width, height = 4, 203, 68
    sheet = Image.new(
        "RGBA",
        (columns * width, 30 + ((len(items) + columns - 1) // columns) * height),
        background,
    )
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (14, 10),
        "Shader catalogue at 32 px · sample times 0.0 / 0.4 / 0.7 / 1.1 / 1.4 s",
        fill=text,
    )
    for index, (name, samples) in enumerate(items):
        x, y = (index % columns) * width + 14, (index // columns) * height + 29
        draw.text((x, y), name, fill=text)
        for frame_number, frame in enumerate(samples):
            sheet.alpha_composite(frame, (x + 36 * frame_number, y + 18))
    sheet.convert("RGB").save(path, optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/shader-gallery")
    parser.add_argument("--cel", type=Path, help="use an alternate test cel")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    shaders = sorted((SKILL / "shaders").glob("*.frag"))
    with TemporaryDirectory(prefix="forge-shader-gallery-") as temp:
        timing = prepare(Path(temp), args.output, args.cel)
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending = [
                pool.submit(build_effect, shader, timing, args.output)
                for shader in shaders
            ]
            items = [future.result() for future in pending]
        pack = Path(temp) / "gallery.json"
        pack.write_text(
            json.dumps(
                {
                    "emojis": [
                        {
                            "name": name,
                            "file": str((args.output / f"{name}.gif").resolve()),
                        }
                        for name, _ in items
                    ]
                }
            ),
            encoding="utf-8",
        )
        forge(
            "preview",
            pack,
            args.output / "overview",
            "--columns",
            8,
            "--tile",
            64,
            "--font-size",
            11,
            "--still-ms",
            700,
        )
    review_sheet(items, args.output / "dark-32.png", "#222733", "#f2f3f7")
    review_sheet(items, args.output / "light-32.png", "#f6f6f1", "#222733")
    print(
        f"Rendered {len(items)} effects, an overview and two review sheets in {args.output}"
    )


if __name__ == "__main__":
    main()
