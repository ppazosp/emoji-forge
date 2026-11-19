# Forge tool reference

Run `uv run forge COMMAND --help` from the skill directory. Commands accept `--json` for machine-readable results and exit nonzero on failure. Use the tools that fit the work.

| Command | Plain input | Result |
| --- | --- | --- |
| `new PROJECT` | New folder | Free-form style and storyboard prompts, plus an optional example manifest. Use `--no-manifest` to skip it. |
| `make "IDEA"` | Idea and optional references | Resumable brief-to-pack workflow with native image tasks. |
| `sheets` | Project artwork and thumbnail panels | Contact sheets and a timed animatic. |
| `stage`, `status`, `review-pack` | Production project | Track reviews and snapshot or bundle the stage hand-off. |
| `plan BOARD OUT` | Storyboard plus X-sheet | JSON or Markdown prompts with previous cel, key and style references. |
| `import RAW OUT` | Generated image or folder | Keyed and aligned RGBA cels, masks and timing. |
| `drift CELS STYLE OUT` | Cels and cropped model references | Palette, silhouette and perceptual comparisons. |
| `register CELS OUT` | Image, GIF or folder of cels | Cels aligned using body masks, or visible alpha when there are no masks. |
| `render CELS EFFECT OUT` | Image or cel folder, plus a fragment file or pass-chain JSON | RGBA frames rendered by [custom GLSL](shaders.md). |
| `assemble CELS OUT.gif` | GIF or cel folder | GIF from supplied exposures. |
| `fit CELS OUT.gif` | GIF or cel folder | GIF fitted to a size, byte and frame budget. |
| `check FILES` | Export image or folder | Decoded dimensions, bytes, frame count, border and seam. Geometry is available when you supply annotated timing. |
| `strips CELS OUT.png` | Image, GIF or cel folder | Timestamped frames at configurable sizes on light and dark. |
| `preview FILES STEM` | Export image or folder | Labelled GIF grid and still PNG. |
| `report FILES OUT`, `bundle FILES OUT` | Export image, folder or export manifest | One overview, multiscale named files, `NAMES.md` and ZIP. |
| `all INPUT OUT` | Cel folder, export folder with GIFs, single export, Python generator or pack JSON | A new version with checks, preview, strips and the distribution pack. |
| `snapshot INPUT OUT` | File or folder | A UTC-dated copy. |
| `compare BEFORE AFTER STEM` | Two files or two version folders | Side-by-side GIF and PNG. |

Folders use filename order, so zero-pad frame numbers. On plain inputs Forge derives lowercase output filenames. A GIF used as a cel source supplies its decoded frames and holds. Registration recognizes `frame-body.png` and `frame-face.png` beside `frame.png`. Masks use white for the torso or face ink and black elsewhere. A body mask excludes props, limbs or effects that would throw off alignment. Use `all --no-register` with a plain cel folder or run the rendering and assembly commands independently to keep source positions. Use short lowercase export names for a pack. For Slack targets, follow the [Slack reference](slack.md).

## Cels and exposure timing

The cel commands accept a timing JSON as an alternative to the folder. Paths in it are relative to the JSON file. Masks are optional. Use `motion: [dx, dy, width_change]` in source pixels when registering an intentional change. Positive y is down. Shader params in a frame can override settings for that exposure.

```json
{
  "frames": [
    {"file": "cels/01.png", "body": "cels/01-body.png", "face": "cels/01-face.png", "ms": 123.5},
    {"file": "cels/02.png", "ms": 266.5, "params": {"sparkFloor": 0.7}}
  ]
}
```

Use any positive finite per-frame delay in milliseconds. For folders, `--frame-ms` sets the default and `--timing-spec TIMING.json` accepts any of the following. A timing JSON or a pack entry can also put the same data under `timing`.

- A list of delays in frame order, such as `[123.5, 266.5]`, or an object containing `durations_ms`.
- An object with `duration_ms` and `easing` to space the frame boundaries over the run.
- An object with `keyframes` giving `frame`, `ms` and optional `ease` for the next segment. Start at boundary zero and end at the boundary after the final cel.

Frame-boundary easing supports `linear`, `ease-in`, `ease-out` and `ease-in-out`. It changes exposure spacing while preserving the supplied drawings. For custom timing, supply exact durations or use a Python hook. GIF stores delays in 10 ms units. Forge encodes with a 20 ms minimum and keeps the total near the requested length when the minimum allows. It merges identical adjacent cels and can try reduced palettes with and without dithering. If a budget still cannot fit the distinct exposures, the command reports why.

## Optional pack JSON

A pack can describe repeatable inputs for `forge all`. Use inline frame rows, filenames or a folder path under `frames`, a Python `script`, or both. This example uses short poses just to show the fields.

```json
{
  "target": "slack",
  "preview_ms": 500,
  "emojis": [
    {
      "name": "spark",
      "use": "Celebrate a win.",
      "frames": "cels/spark",
      "timing": {"duration_ms": 1800, "easing": "ease-in-out"},
      "effect": {"shader": "effects/spark.frag", "params": {"ink": "#f1c548"}},
      "register": false
    },
    {"name": "hello", "target": "generic", "static": true, "frames": ["cels/hello.png"]}
  ]
}
```

Per-entry `target` overrides the pack default. `register: false` preserves the supplied placements. You can set the 1-based `reference` exposure for registration, choose a `matte` and GIF `loop` count, and set an optional `seam` tolerance for a deliberate visual cut. The checker reports decoded seam distance as an average premultiplied pixel difference. Set a limit with `check --seam` or a pack entry’s `seam` when a smooth loop matters. To check face containment and registration, annotate body and face masks and use `--require-masks`. The visual review still helps with fine details and pacing.

| Preset | Square canvas | Byte budget | GIF frame cap |
| --- | ---: | ---: | ---: |
| `slack` | 128 px | 128,000 | 50 |
| `generic` | 256 px | 1,000,000 | 120 |

`forge all` renders emoji in parallel. Choose the worker count with `--jobs`. Draft runs export at 64 px and render effects at 128 px. Each hit in the content cache covers one emoji and its inputs. Use `--cache` to point to a shared cache folder. Pass a new version folder on each run. `forge check` reads the recorded limits on an exported pack unless you supply a budget. Use `all --exports` for a folder of finished stills. This export manifest can also feed `preview` and `bundle`, or either can read the exports folder directly.

## Python animation hooks

Use a hook to draw cels, edit a sequence, or set poses and durations in code. A pack entry can set `"script": "draw.py:animate"` or supply an object.

```json
{
  "path": "draw.py",
  "function": "animate",
  "mode": "emoji",
  "params": {"line_width": 2},
  "deps": ["palette.json"]
}
```

Use `forge all PACK OUT --allow-scripts` for a manifest with trusted local Python. You can also run `forge all draw.py OUT` directly or `forge all cels/ OUT --script draw.py:animate`. Python hooks run with your local process permissions. Treat them as code.

- In `emoji` mode, `animate(frames, context)` receives a list of cels and returns a list. With no cels supplied, it receives an empty list and can create a sequence.
- In `frame` mode, `animate(frame, context)` receives and returns one cel. For drawing from scratch, use `count` in the script object to create timed blank frame records. This mode adds zero-based `index`, `time` in seconds and `progress` in the loop to the context.
- Each frame is a Python dictionary with a Pillow `image`, optional `body` and `face` mask images, and timing or custom parameter metadata. Return `ms` to specify the cel's hold. Without returned holds, Forge uses the supplied timing spec or the default.
- Context includes `name`, suggested canvas `size`, `draft`, `project_dir`, `source_dir` and the hook's `params`. List any additional files your hook reads in `deps` so a change invalidates the cache. Use a new cache if behavior depends on external state.

See the [custom animation example](../assets/lantern/README.md) for a hook and two bespoke passes working together.

## Report and distribution

`forge report INPUT OUTPUT` and `forge bundle INPUT OUTPUT` create the same pack directory and sibling ZIP. For each emoji, keep PNG for a still and GIF for animation at every scale. Pass `--scales 64,128,256,512` to choose sizes and `--2x` for an optional larger overview. Use `--pixel-art` for nearest-neighbor scaling. The overview is PNG for an all-static pack and GIF if any emoji is animated. Use the single `overview` path returned with `--json` when sharing the pack in chat.

```text
pack/
├── overview.gif or overview.png
├── overview@2x.gif or overview@2x.png   (optional)
├── NAMES.md
└── emoji/
    ├── 64/
    ├── 128/
    ├── 256/
    └── 512/
```

Only the upload scale identified by the preset or manifest has the platform byte and frame cap. `forge all` retains an original-resolution master for each available larger version. For existing exports, set `master` in each export entry to a high-resolution PNG, GIF or lossless-cel timing JSON. An explicit scale above the smallest available master fails with its supported size. Without an explicit list, the report selects the available default scales and the upload scale. It does not upscale small exports.
