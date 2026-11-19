import json
import os
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "forge.py"


def call(*args, status=0):
    run = subprocess.run([sys.executable, CLI, *map(str, args), "--json"], check=False, capture_output=True, text=True)
    assert run.returncode == status, (run.stdout, run.stderr)
    return json.loads(run.stdout)


def save(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def make_cel(root, index, offset=0, wide=0, eye=(16, 17), color="gold", border=False):
    cel = Image.new("RGBA", (32, 32))
    body, face = Image.new("L", cel.size), Image.new("L", cel.size)
    geometry = (8 + offset, 8, 22 + offset + wide, 25)
    ImageDraw.Draw(cel).ellipse(geometry, fill=color)
    ImageDraw.Draw(body).ellipse(geometry, fill=255)
    ImageDraw.Draw(face).point(eye, fill=255)
    cel.putpixel(eye, (0, 0, 0, 255))
    if border:
        cel.putpixel((0, 0), (10, 0, 0, 255))
    result = {}
    for field, layer in (("file", cel), ("body", body), ("face", face)):
        filename = f"{index}-{field}.png"
        layer.save(root / filename)
        result[field] = filename
    return {"ms": 100, **result}


@pytest.fixture
def cels(tmp_path):
    rows = [make_cel(tmp_path, 1), make_cel(tmp_path, 2, color="royalblue")]
    return save(tmp_path / "timing.json", {"frames": [rows[0], rows[0], rows[1], rows[0]]})


def test_register_removes_accidental_translation_and_keeps_declared_motion(tmp_path):
    first = make_cel(tmp_path, 1)
    second = make_cel(tmp_path, 2, offset=4, eye=(20, 17))
    timing = save(tmp_path / "timing.json", {"frames": [first, second, {**second, "motion": [2, 0, 0]}]})
    directory = tmp_path / "registered"
    assert call("register", timing, directory)["ok"]
    rows = json.loads((directory / "timing.json").read_text())["frames"]
    boxes = [Image.open(directory / row["body"]).getbbox() for row in rows]
    assert boxes[:2] == [(8, 8, 23, 26)] * 2
    assert boxes[2] == (10, 8, 25, 26)


@pytest.mark.parametrize("matte", [None, "#20252f"])
def test_fit_combines_holds_without_losing_transparency_or_exact_matte(tmp_path, cels, matte):
    gif = tmp_path / "sample.gif"
    matte_args = ("--matte", matte) if matte else ()
    result = call("fit", cels, gif, "--size", 32, "--max-frames", 3, "--max-bytes", 4000, *matte_args)
    assert result["files"][0]["frames"] == 3
    with Image.open(gif) as image:
        assert image.info["loop"] == 0
        for index, duration in enumerate((200, 100, 100)):
            image.seek(index)
            assert image.info["duration"] == duration
            assert image.convert("RGBA").getpixel((0, 0)) == ((32, 37, 47, 255) if matte else (0, 0, 0, 0))
    entry = {"name": "hello", "file": gif.name, "timing": cels.name}
    if matte:
        entry["matte"] = matte
    pack = save(tmp_path / "pack.json", {"emojis": [entry]})
    result = call("check", pack, "--size", 32, "--require-masks")
    assert result["emojis"][0]["duration_ms"] == 400
    assert result["emojis"][0]["geometry_checked"]
    assert call("fit", cels, tmp_path / "too-big.gif", "--size", 32, "--max-bytes", 10, status=1)["error"]
    assert not (tmp_path / "too-big.gif").exists()


def test_preview_strips_and_bundle_preserve_order_names_and_pixels(tmp_path, cels):
    gif = tmp_path / "sample.gif"
    call("assemble", "--size", 32, cels, gif)
    png = tmp_path / "still.png"
    Image.new("RGBA", (32, 32)).save(png)
    pack = save(tmp_path / "pack.json", {"emojis": [
        {"name": "first", "file": png.name, "use": "A greeting"},
        {"name": "second", "file": gif.name, "use": "A wave"},
    ]})
    stem = tmp_path / "gallery"
    preview = call("preview", pack, stem, "--columns", 2)
    assert [item["frames"] for item in preview["files"]] == [3, 1]
    output = tmp_path / "strip.png"
    assert call("strips", gif, output, "--size", 8, 32, 128)["files"][0]["size"][0] == 408
    folder = tmp_path / "pack"
    archive = tmp_path / "deliver.zip"
    call("bundle", pack, folder, f"--zip={archive}")
    with ZipFile(archive) as zipped:
        assert zipped.namelist() == ["NAMES.md", "first.png", "second.gif"]
        assert zipped.read("second.gif") == gif.read_bytes()
        assert "| 1 | `first` | A greeting |" in zipped.read("NAMES.md").decode()


@pytest.mark.parametrize(("failure", "hint"), [
    ("face", "face mask"), ("drift", "drift"), ("seam", "seam"),
    ("border", "canvas border"), ("frames", "GIF frames"), ("bytes", "exceeds"),
    ("size", "expected"), ("masks", "missing timing"),
])
def test_checker_reports_bad_assets_in_json(tmp_path, failure, hint):
    first = make_cel(tmp_path, 1)
    second = make_cel(
        tmp_path, 2, offset=5 if failure == "drift" else 0, color="royalblue",
        eye=(1, 1) if failure == "face" else (16, 17), border=failure == "border",
    )
    third = second if failure == "seam" else first
    timing = save(tmp_path / "timing.json", {"frames": [first, second, third]})
    gif = tmp_path / "sample.gif"
    call("assemble", timing, gif)
    entry = {"name": "sample", "file": gif.name, "timing": timing.name}
    if failure == "masks":
        entry.pop("timing")
    pack = save(tmp_path / "pack.json", {"emojis": [entry]})
    args = {
        "frames": ["--max-frames", 2], "bytes": ["--max-bytes", 4],
        "seam": ["--seam", .0001], "drift": ["--drift-px", 1],
    }.get(failure, [])
    result = call("check", pack, "--size", 64 if failure == "size" else 32, "--require-masks", *args, status=1)
    assert not result["ok"]
    assert hint in result["emojis"][0]["error"]


def test_scaffold_build_cache_edits_snapshot_and_comparison(tmp_path):
    project = tmp_path / "brief"
    call("new", project, "--preset", "slack")
    assert {"style.md", "storyboard.md", "pack.json", "cels"} == {p.name for p in project.iterdir()}
    source = Image.new("RGBA", (512, 512))
    ImageDraw.Draw(source).ellipse((120, 120, 290, 300), fill="gold")
    source.save(project / "body.png")
    source.save(project / "another.png")
    manifest = save(project / "pack.json", {"target": "slack", "emojis": [
        {"name": "hey", "static": True, "frames": [{"file": "body.png"}]},
        {"name": "hello", "static": True, "target": "generic", "frames": [{"file": "another.png"}]},
    ]})
    before = tmp_path / "before"
    draft = call("all", manifest, before, "--draft", "--jobs", 2)
    assert [item["size"] for item in draft["checks"]] == [[64, 64], [64, 64]]
    assert draft["cache_hits"] == []
    cached = call("all", manifest, tmp_path / "second", "--draft")
    assert cached["cache_hits"] == ["hey", "hello"]
    saved = Path(call("snapshot", before, tmp_path / "review")["path"])
    assert (saved / "pack.zip").read_bytes() == (before / "pack.zip").read_bytes()
    assert call("snapshot", before, before / "inside", status=1)["error"]
    assert call("all", manifest, before, status=1)["error"]

    after = tmp_path / "after"
    full = call("all", manifest, after)
    assert full["cache_hits"] == []
    assert [item["size"] for item in full["checks"]] == [[128, 128], [256, 256]]
    assert call("check", after / "pack.json")["ok"]
    source.putpixel((245, 245), (1, 2, 3, 255))
    source.save(project / "body.png")
    assert call("all", manifest, tmp_path / "changed")["cache_hits"] == ["hello"]
    comparison = call("compare", saved, after, tmp_path / "comparison")
    assert not comparison["added"] and Path(comparison["files"][1]["path"]).is_file()
    assert call("fit", "--not-an-option", status=1)["error"]


def test_every_shader_renders_on_modern_gl(tmp_path, cels):
    base = json.loads(cels.read_text())["frames"][0]
    save(cels, {"frames": [{**base, "ms": 420}, {**base, "ms": 580}]})
    for shader in sorted((ROOT / "shaders").glob("*.frag")):
        result = call("render", cels, shader, tmp_path / shader.stem, "--backend", "moderngl", "--size", 24)
        assert len(result["files"]) == 3
        first, peak = [Image.open(result["files"][i]["path"]).convert("RGBA") for i in (0, 1)]
        assert first.getbbox() and first.getpixel((0, 0))[3] == 0
        assert first.tobytes() != peak.tobytes(), shader.name


def test_headless_webgl_fallback_renders(tmp_path, cels):
    channel = os.getenv("FORGE_TEST_CHROME")
    if not channel:
        pytest.skip("set FORGE_TEST_CHROME=chrome to run browser backend with installed Chrome")
    result = call("render", cels, ROOT / "shaders/sparkle.frag", tmp_path / "webgl",
                  "--backend", "webgl", "--channel", channel, "--draft")
    assert result["files"][0]["size"] == [128, 128]
    first = Image.open(result["files"][0]["path"]).convert("RGBA")
    assert first.getpixel((0, 0))[3] == 0
    assert first.getpixel((60, 64))[3] > 250
