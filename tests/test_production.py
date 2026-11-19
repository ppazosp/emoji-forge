import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw
from test_forge import SKILL, call, save


def cell(
    path, color="royalblue", size=128, rectangle=(35, 38, 82, 88), background=None
):
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (size, size), background)
    ImageDraw.Draw(canvas).rectangle(rectangle, fill=color)
    canvas.save(path)


def test_plan_threads_exposure_prompts_to_previous_key_and_style(tmp_path):
    board = save(
        tmp_path / "storyboard.json",
        {
            "style_sheet": "style.png",
            "direction": "Same blue paper folds",
            "panels": [
                {"id": "wave", "action": "Raise the wing", "expression": "Eyes open"}
            ],
        },
    )
    xsheet = save(
        tmp_path / "x-sheet.json",
        {
            "frames": [
                {"panel": "wave", "key_pose": "keys/low.png", "ms": 120},
                {"pose": "Wing halfway up", "panel": "wave", "ms": 80},
                {"pose": "Wave held", "key_pose": "keys/high.png", "ms": 400},
                {"pose": "Ease the wing down", "ms": 140},
            ]
        },
    )
    out = tmp_path / "review/plan.json"
    call("plan", board, out, "--x-sheet", xsheet, "--frames-dir", "drawings")
    plan = json.loads(out.read_text())
    assert plan["durations_ms"] == [120, 80, 400, 140]
    assert plan["frames"][0]["references"]["previous_frame"] is None
    assert plan["frames"][1]["references"] == {
        "previous_frame": "drawings/001.png",
        "key_pose": "../keys/low.png",
        "style_sheet": "../style.png",
    }
    assert "Frame 02/04: Wing halfway up" in plan["frames"][1]["prompt"]
    assert "Eyes open" in plan["frames"][1]["prompt"]
    assert plan["frames"][3]["references"]["key_pose"] == "../keys/high.png"
    markdown = tmp_path / "plan.md"
    call("plan", board, markdown, "--x-sheet", xsheet)
    assert "raw/004.png" in markdown.read_text()


def test_import_keys_and_aligns_cels_and_carries_face_masks(tmp_path):
    raw = tmp_path / "raw"
    cell(raw / "01.png", rectangle=(10, 10, 39, 39), background="white")
    cell(raw / "02.png", rectangle=(50, 55, 109, 114))
    face = Image.new("L", (128, 128))
    ImageDraw.Draw(face).rectangle((20, 20, 29, 29), fill=255)
    face.save(raw / "01-face.png")
    output = tmp_path / "aligned"
    options = save(tmp_path / "plan.json", {"durations_ms": [120, 250]})
    call(
        "import",
        raw,
        output,
        "--size",
        100,
        "--anchor",
        "bottom",
        "--scale",
        "shared",
        "--timing-spec",
        options,
    )
    with (
        Image.open(output / "001.png") as first,
        Image.open(output / "002.png") as second,
    ):
        assert first.size == second.size == (100, 100)
        assert first.getbbox() == (30, 50, 70, 90)
        assert second.getbbox() == (10, 10, 90, 90)
        assert first.getpixel((0, 0))[3] == 0
    with Image.open(output / "001-face.png") as normalized:
        assert normalized.getbbox() == (43, 63, 57, 77)
    rows = json.loads((output / "timing.json").read_text())["frames"]
    assert [row["ms"] for row in rows] == [120, 250]
    assert all((output / row["body"]).is_file() for row in rows)
    assert call("register", output / "timing.json", tmp_path / "registered")["ok"]


def test_drift_flags_a_palette_outlier_against_style_and_both_neighbors(tmp_path):
    raw = tmp_path / "raw"
    style = tmp_path / "style.png"
    cell(style)
    for number, color in enumerate(("royalblue", "red", "royalblue"), 1):
        cell(raw / f"{number}.png", color)
    call("import", raw, tmp_path / "cels", "--size", 128)
    result = call("drift", tmp_path / "cels", style, tmp_path / "drift.json")
    assert result["flagged"] == 1
    outlier = result["frames"][1]
    assert (
        "style:palette" in outlier["flags"] and "neighbors:palette" in outlier["flags"]
    )
    assert outlier["style"]["mask_iou"] == 1
    assert outlier["style"]["hash_distance"] == 0


def test_studio_scaffold_sheets_animatic_and_stage_review_zip(tmp_path):
    project = tmp_path / "production"
    call("new", project, "--emoji", "wave", "--emoji", "bounce")
    for group in ("model", "expressions", "poses"):
        cell(project / "images" / group / "reference.png")
    wave = project / "emojis/wave"
    cell(wave / "panels/01.png")
    cell(wave / "panels/02.png", "gold")
    cell(project / "emojis/bounce/panels/other.png", "green")
    save(
        wave / "storyboard.json",
        {
            "panels": [
                {"id": "one", "beat": "Start", "file": "panels/01.png", "ms": 130},
                {"id": "two", "beat": "Peak", "file": "panels/02.png", "ms": 270},
            ]
        },
    )
    output = call("sheets", "--project", project, "--emoji", "wave")
    assert {Path(path).name for path in output["files"]} == {
        "model.png",
        "expressions.png",
        "poses.png",
        "storyboard.png",
        "animatic.gif",
    }
    with Image.open(project / "review/wave/sheets/animatic.gif") as animatic:
        assert animatic.n_frames == 2
        assert animatic.info["duration"] == 130
    handoff = call("review-pack", "storyboard", "--project", project, "--emoji", "wave")
    with ZipFile(handoff["archive"]) as archive:
        assert "review/wave/sheets/animatic.gif" in archive.namelist()
        assert all("bounce" not in name for name in archive.namelist())
        assert "images/poses/reference.png" not in archive.namelist()
    result = call(
        "stage",
        "storyboard",
        "--project",
        project,
        "--emoji",
        "wave",
        "--review",
        "fail",
        "--notes",
        "Hold the second panel longer.",
    )
    snapshot = project / result["reviews"][0]["snapshot"]
    with ZipFile(snapshot) as archive:
        assert "Hold the second panel longer." in archive.read("REVIEW.md").decode()
    status = call("status", "--project", project)["emojis"]
    assert status["wave"]["stage"] == "storyboard"
    assert status["bounce"]["stage"] == "bible"
    assert (
        call("stage", "bible", "--project", project, "--emoji", "wave")["stage"]
        == "bible"
    )


def test_make_waits_resumes_approves_and_finishes_with_fixture_cels(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("FORGE_IMAGE_API_KEY", raising=False)
    project = tmp_path / "project"
    result = call(
        "make",
        "Blue bird wave",
        "--animated",
        "--project",
        project,
        "--gate",
        "bible",
        "--scales",
        "64,128",
    )
    count = 0
    while result["status"] != "complete" and count < 24:
        if result["status"] == "needs-review":
            assert result["stage"] == "bible"
            assert len(result["task"]["review_packs"]) == 1
            result = call("make", "--resume", "--approve", "--project", project)
        else:
            job = result["task"]
            assert all(Path(ref).is_file() for ref in job["references"])
            tone = "gold" if "/raw/" in job["output"] else "royalblue"
            cell(
                Path(job["output"]), color=tone, size=512, rectangle=(90, 100, 350, 370)
            )
            result = call("make", "--resume", "--project", project)
        count += 1
    assert result["status"] == "complete"
    assert Path(result["overview"]).name == "overview.gif"
    assert Path(result["zip"]).is_file()
    assert not (project / "next-task.json").exists()
    assert (project / "image-prompts.jsonl").is_file()
    assert call("make", "--resume", "--project", project)["zip"] == result["zip"]
    reviews = call("status", "--project", project)["emojis"]["blue-bird-wave"][
        "reviews"
    ]
    assert [review["stage"] for review in reviews] == [
        "bible",
        "storyboard",
        "keys",
        "inbetweens",
        "effects",
        "final",
    ]


def test_report_uses_masters_and_selects_overview_type(tmp_path):
    low = tmp_path / "still.png"
    master = tmp_path / "master.png"
    cell(low, color="black", size=128)
    cell(master, color="lime", size=512, rectangle=(35, 38, 320, 360))
    manifest = save(
        tmp_path / "pack.json",
        {
            "emojis": [
                {"name": "still", "file": low.name, "master": master.name},
            ]
        },
    )
    output = tmp_path / "only-stills"
    result = call(
        "report", manifest, output, "--scales", "64,128,256,512", "--2x", "--pixel-art"
    )
    assert Path(result["overview"]).name == "overview.png"
    assert (output / "overview@2x.png").exists() and not (
        output / "overview.gif"
    ).exists()
    for size in (64, 128, 256, 512):
        with Image.open(output / "emoji" / str(size) / "still.png") as frame:
            assert frame.size == (size, size)
            if size >= 256:
                assert frame.getpixel((size // 3, size // 3))[:3] == (0, 255, 0)
    with ZipFile(output.with_suffix(".zip")) as archive:
        assert "emoji/512/still.png" in archive.namelist()
    frames = tmp_path / "frames"
    cell(frames / "01.png", size=256)
    cell(frames / "02.png", color="gold", size=256)
    gif = tmp_path / "wave.gif"
    call("assemble", frames, gif)
    mixed = save(
        tmp_path / "mixed.json",
        {
            "target": "slack",
            "emojis": [
                {"name": "still", "file": low.name, "master": master.name},
                {"name": "wave", "file": gif.name},
            ],
        },
    )
    report = call("bundle", mixed, tmp_path / "mixed", "--scales", "64,128,256")
    assert Path(report["overview"]).name == "overview.gif"
    for size in (64, 128, 256):
        folder = tmp_path / "mixed" / "emoji" / str(size)
        assert (folder / "still.png").is_file()
        with Image.open(folder / "wave.gif") as animated:
            assert animated.n_frames == 2
            assert animated.size == (size, size)
    assert (
        "without upscaling"
        in call("bundle", mixed, tmp_path / "invalid", "--scales", "512", status=1)[
            "error"
        ]
    )


def test_shipped_native_frames_import_and_drift(tmp_path):
    sample = SKILL / "assets/threaded"
    call(
        "import",
        sample / "emojis/wave/raw",
        tmp_path / "cels",
        "--scale",
        "shared",
        "--timing-spec",
        sample / "emojis/wave/plan.json",
    )
    checked = call(
        "drift", tmp_path / "cels", sample / "images/model", tmp_path / "drift.json"
    )
    assert len(checked["frames"]) == 4
    assert checked["flagged"] == 0


def test_make_runs_static_without_intervention_using_adapter(tmp_path, monkeypatch):
    monkeypatch.delenv("FORGE_IMAGE_API_KEY", raising=False)
    project = tmp_path / "static"
    adapter = tmp_path / "adapter.py"
    adapter.write_text(
        """import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
job = json.loads(Path(sys.argv[1]).read_text())
frame = Image.new("RGBA", (128, 128))
ImageDraw.Draw(frame).ellipse((35, 34, 90, 92), fill="orange")
frame.save(job["output"])
""",
        encoding="utf-8",
    )
    result = call(
        "make",
        "Amber circle",
        "--project",
        project,
        "--static",
        "--generator",
        adapter,
        "--yes",
        "--gate",
        "bible",
        "--scales",
        "64,128",
    )
    assert result["status"] == "complete"
    assert Path(result["overview"]).suffix == ".png"
    assert (Path(result["pack"]) / "emoji/64/amber-circle.png").is_file()
    assert not (Path(result["pack"]) / "overview.gif").exists()
