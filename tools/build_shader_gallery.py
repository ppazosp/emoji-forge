"""Render the shader catalogue and generate the small-size review sheets."""

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


def prepare(root):
    with Image.open(ROOT / "assets/brand/logo.png") as logo:
        art = logo.convert("RGBA")
    # Leave room around the mascot for effects such as the portal and orbit.
    art = art.resize((384, 384), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (512, 512))
    canvas.paste(art, (64, 64))
    canvas.save(root / "art.png")
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
    forge("render", timing, config, rendered, "--backend", "moderngl")
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
            f"{name}: expected an animated {EXPOSURES * EXPOSURE_MS} ms GIF"
        )
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
    parser.add_argument("--output", type=Path, default=ROOT / "gallery/shaders")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    shaders = sorted((SKILL / "shaders").glob("*.frag"))
    with TemporaryDirectory(prefix="forge-shader-gallery-") as temp:
        timing = prepare(Path(temp))
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending = [
                pool.submit(build_effect, shader, timing, args.output)
                for shader in shaders
            ]
            items = [future.result() for future in pending]
    review_sheet(items, args.output / "dark-32.png", "#222733", "#f2f3f7")
    review_sheet(items, args.output / "light-32.png", "#f6f6f1", "#222733")
    print(f"Rendered {len(items)} effects and two review sheets in {args.output}")


if __name__ == "__main__":
    main()
