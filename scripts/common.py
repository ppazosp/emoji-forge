"""Shared input formats for the command-line tools."""

import argparse
import json
import re
from bisect import bisect_right
from dataclasses import dataclass
from itertools import accumulate

from PIL import Image, ImageSequence


def cli(description, configure, run):
    parser = argparse.ArgumentParser(description=description)
    configure(parser)
    try:
        run(parser.parse_args())
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        parser.exit(1, f"error: {error}\n")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def image(path, mode="RGBA"):
    with Image.open(path) as source:
        return source.convert(mode)


@dataclass(frozen=True)
class Timeline:
    frames: list[Image.Image]
    delays: list[int]

    @property
    def duration(self):
        return sum(self.delays)

    @property
    def starts(self):
        return [0, *accumulate(self.delays[:-1])]


def read_timing(path):
    rows = read_json(path)["frames"]
    if not rows:
        raise ValueError("timing needs at least one exposure")
    delays = [row["ms"] for row in rows]
    if any(type(ms) is not int or ms < 20 or ms > 655350 or ms % 10 for ms in delays):
        raise ValueError("use GIF delays of 20–655350 ms in multiples of 10")
    return rows, delays


def decode(path):
    with Image.open(path) as source:
        frames, delays = [], []
        for frame in ImageSequence.Iterator(source):
            frames.append(frame.convert("RGBA"))
            delays.append(frame.info.get("duration") or 100)
    return Timeline(frames, delays)


def preview_frame(timeline, starts, timestamp):
    return timeline.frames[bisect_right(starts, timestamp % timeline.duration) - 1]


def pack_entries(manifest):
    entries = read_json(manifest)["emojis"]
    if not entries:
        raise ValueError("pack needs at least one emoji")
    seen = set()
    for entry in entries:
        path = manifest.parent / entry["file"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", entry["name"]):
            raise ValueError(f"invalid emoji name: {entry['name']}")
        if entry["name"] in seen:
            raise ValueError(f"duplicate emoji name: {entry['name']}")
        if path.suffix.lower() not in {".gif", ".png", ".jpg", ".jpeg"}:
            raise ValueError(f"unsupported raster format: {path.name}")
        seen.add(entry["name"])
        yield entry, path


def mask_geometry(mask):
    binary = mask.point(lambda value: 255 if value >= 128 else 0)
    bounds = binary.getbbox()
    if bounds is None:
        raise ValueError("body mask is empty")
    left, top, right, bottom = bounds
    cropped = binary.crop(bounds).tobytes()
    width = right - left
    xs, ys = 0, 0
    count = cropped.count(255)
    for index, pixel in enumerate(cropped):
        if pixel:
            y, x = divmod(index, width)
            xs += x
            ys += y
    return (left + xs / count, top + ys / count), (width, bottom - top)


def output_path(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
