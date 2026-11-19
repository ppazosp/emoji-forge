# Workflow and script interfaces

| Phase | What to produce |
| --- | --- |
| Brief | Reference permissions, action list, target format, byte and frame limits, display size and light/dark backgrounds. |
| Style lock | One reference sheet showing neutral face, silhouette, texture swatches, outline thickness, hands, feet and allowed pose changes. Record how much clear canvas the export needs. |
| Storyboard and personality | A use case and timed beat sheet for each reaction. State what an eye, hand, prop or foot does at each beat. For a still, pick the one drawing that communicates the whole reaction. |
| Key poses | Generate one full cel per key pose from the same reference. Use image edits to fix local hand and face errors. Keep the original cels. |
| Registration | Mark torso and face per pose. Register against the approved neutral pose. Check feet and joins after resampling. Keep designed jumps, leans and squash as explicit motion. |
| In-betweens and timing | Draw or edit transitional poses and hold the readable expressions. Keep a timing file with one entry per exposure. Save the lossless RGBA master cels. |
| Effects | Layer procedural effects over registered art at 512 px or more. Attach emitters to the exposed pose. Preserve a clean base export for comparison. |
| Checks | Decode the final files. Check size, bytes, frames, borders, the seam and registered geometry. |
| Motion review | Snapshot, inspect and document every frame at three sizes on both backgrounds. Fix in a new folder and recheck. |
| Pack and distribution | Fit the target profile, deliver one labelled grid and still, timestamped strips and a ZIP of individually named assets and the ordered names table. |

## Timing JSON

Paths are relative to the timing file. Each `file` points to a full RGBA cel. For registration and geometry checks, draw same-canvas grayscale `body` and `face` masks. Use white for the torso silhouette (including the area behind facial features) and facial ink respectively, and black elsewhere. Omit limbs, props and effects from the body mask. Mark the facial features where they actually appear. Avoid approximating the masks with a shared rectangle.

```json
{
  "frames": [
    {"file": "ready.png", "body": "ready-body.png", "face": "ready-face.png", "ms": 260},
    {"file": "reach.png", "body": "reach-body.png", "face": "reach-face.png", "ms": 140,
     "motion": [0, -3, 0], "anchor": [0.72, 0.64]}
  ]
}
```

`motion` is the allowed offset `[dx, dy, width_change]` in source canvas pixels. Positive y moves down. Registration applies that offset relative to the reference. For intentionally nonuniform squash, redraw against the intended registered pose and audit it separately, since the helper uses a uniform transform. `anchor` gives the shader emitter position in normalized UV from the bottom left of the **registered** cel. Set it after registration if the prop shifted. One animated GIF delay is 20 ms or more in 10 ms increments.

## Pack JSON

List entries in display and upload order. Paths are relative to the manifest. For effects, point `timing` to the registered art before effects. Decoded checks still inspect the final effects GIF. Use the optional `matte` for an intentionally opaque border and record a case-specific `seam` threshold only after reviewing a deliberate continuous motion across the seam.

```json
{
  "emojis": [
    {"name": "wave", "file": "exports/wave.gif", "use": "Say hello.",
     "timing": "wave-registered/timing.json"},
    {"name": "thanks", "file": "exports/thanks.png", "use": "Show appreciation."}
  ]
}
```

## Commands

Run from the skill directory. Use new output directories for versions and preserve the previous render.

```sh
uv run --with pillow python scripts/register_frames.py art/timing.json work/registered
uv run --with pillow python scripts/assemble_gif.py work/registered/timing.json exports/wave.gif --size 128 --max-bytes 128000 --max-frames 50
uv run --with pillow python scripts/check_pack.py pack.json --size 128 --max-bytes 128000 --max-frames 50 --drift-px 2 --require-masks
uv run --with pillow python scripts/build_preview.py pack.json report/preview --still-ms 1200
uv run --with pillow python scripts/make_strips.py exports/wave.gif report/wave.png --size 32 128 512
uv run --with pillow python scripts/bundle.py pack.json delivery/pack
```

The size, frame and byte values shown here are example profile settings. Pass the intended target's limits. `check_pack.py` measures annotated geometry at the chosen export size and compares the decoded final seam by mean premultiplied pixel difference. Hand attachment, face centring and seam pacing need human judgement. For an all-static pack it applies only canvas dimensions, byte size and border checks per asset. The scripts process raster files. An optional SVG companion can be exported separately and checked visually after rasterizing at the target size.

The preview keeps each emoji on its own loop clock within the grid. It defaults to the longest item duration, then repeats the grid as a whole. Choose `--duration-ms` to show more cycles or a shared repeat point. Strips show every decoded frame including its start timestamp, native and zoomed pixels, and the reduced display size.

## One-command packs

`forge new` writes a brief and a source manifest. Put exposure rows inline under each emoji's `frames`. Paths are relative to the manifest file.

```json
{
  "target": "slack",
  "preview_ms": 500,
  "emojis": [
    {"name": "spark", "use": "Celebrate a win.", "effect": {
      "shader": "sparkle", "params": {"anchor": [0.7, 0.8], "intensity": 0.8, "speed": 1.0}
    }, "frames": [
      {"file": "cels/rest.png", "body": "cels/rest-body.png", "face": "cels/rest-face.png", "ms": 350},
      {"file": "cels/cheer.png", "body": "cels/cheer-body.png", "face": "cels/cheer-face.png", "ms": 750},
      {"file": "cels/rest.png", "body": "cels/rest-body.png", "face": "cels/rest-face.png", "ms": 200}
    ]},
    {"name": "hello", "target": "generic", "static": true, "frames": [{"file": "cels/hello.png"}]}
  ]
}
```

Use `effect.shader` to select a bundled shader by name or a local fragment file by path. Parameters set a default emitter position, strength and effect clock speed. Exposure fields can override them. Choose `matte` for an opaque background. Set `reference` to a 1-based exposure if the neutral cel comes later. The optional per-emoji `target` overrides the pack default. `preview_ms` selects the still preview timestamp.

| Preset | Square canvas | Byte budget | GIF frame cap |
| --- | ---: | ---: | ---: |
| `slack` | 128 px | 128,000 | 50 |
| `generic` | 256 px | 1,000,000 | 120 |

`forge all PACK OUTPUT` runs registration, effects, fitting, checks and reports. Use `--jobs` for worker count, `--draft` for 64 px exports and 128 px shader renders, and `--cache` to share a cache directory across runs. The default cache is `.forge-cache` next to the manifest. The cache key covers cel and mask bytes, timing, shader source and render settings. A new version directory receives its own copies of the checked assets. `forge check OUTPUT/pack.json` reads each asset's recorded limits unless you supply an explicit budget.

Run `forge COMMAND --help` for `register`, `render`, `assemble`, `fit`, `check`, `strips`, `preview` and `bundle`. `fit` applies a preset or explicit `--size`, `--max-bytes` and `--max-frames`. It merges identical adjacent holds and tries smaller palettes with and without dithering. If it cannot fit distinct poses, it reports the budget problem and keeps the source untouched.

Before review or changes, use `forge snapshot VERSION SNAPSHOTS` for a UTC-dated copy. Use `forge compare BEFORE AFTER REPORT_STEM` to put matching names side by side on the same preview clock. Missing entries show an empty tile. Add `--json` to any command for one machine-readable result and use its exit status to detect failure.
