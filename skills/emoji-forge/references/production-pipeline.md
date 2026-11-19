# Production scaffolds and review hand-offs

Use whichever stages help the user develop a consistent character or pack. A small graphic may need only a sketch and an export check. For a mascot, the sheets help an illustrator and motion designer share the same references at every hand-off.

```mermaid
flowchart LR
    A[Idea and references] --> B[Model, expression and pose sheets]
    B --> M[Asset views and integrations]
    M --> C[Storyboard, animatic and exposure sheet]
    C --> D[Key poses and threaded image edits]
    D --> E[Import, align and inspect drift]
    E --> F[Optional effects and target checks]
    F --> L[Pack lineup and scale checks]
    L --> G[One overview and multiscale bundle]
    E -->|Review and revise| C
    F -->|Review and revise| D
```

```sh
uv run forge new project --emoji wave --emoji cheer
uv run forge sheets --project project --emoji wave
uv run forge status --project project
```

The project contains a character bible (`style.md`), expression and pose notes, and `assets.json` with per-emoji slots for characters, props, effects and backgrounds. Record each asset as `todo`, `drafted` or `approved`. Add the useful model views, faces, hands and props under `images/model`, `images/expressions` and `images/poses`. Use PNGs or other supported images. Note relevant proportions, outline weight, texture, colors in hex, original references, and which features to preserve as you iterate.

Each `emojis/<name>/` contains a free-form storyboard, structured thumbnail panels in `storyboard.json`, and an exposure sheet (`x-sheet.json`). Each panel can have an ID, thumbnail path, beat, action, expression and duration in milliseconds. `forge sheets` renders the model, pose, expression and storyboard contact sheets and a timed thumbnail GIF (`animatic.gif`) from the available panels. Make an exposure row for each distinct drawing, refer to a panel by ID, and lengthen its duration for holds. Use `key_pose` on key exposures and a `pose` override for an in-between. [The frame-edit workflow](image-generation.md) shows how to plan and draw the cels from those references.

| Stage | Hand-off for the reviewer |
| --- | --- |
| `bible` | Character notes, references, model sheet and the asset list. |
| `storyboard` | Storyboard panels, model sheet and the animatic at its intended timing. |
| `keys` | Key poses, expression and pose sheets, and the storyboard. |
| `inbetweens` | Raw and aligned cels, exposure sheet, strips and drift flags. |
| `effects` | Clean cels, treated frames or exports, timing and comparison strips. |
| `final` | Final emoji, strips, checklist results and the distribution overview when available. |

Run `forge review-pack STAGE --project project --emoji wave` for a folder and ZIP containing the materials for that stage. Read the included `REVIEW.md`. A reviewer can report pass or fail with observations against the bible and storyboard. Record the result with `forge stage STAGE --review pass --notes "..." --project project --emoji wave`. This also saves a dated snapshot of the hand-off. Use `forge stage NEXT --project project --emoji wave` when ready to move on or return to an earlier stage. The stage tracker records decisions and leaves the creative workflow to you. [Reviewer brief and checklist](review-checklist.md)

Keep per-emoji assets in `emojis/<name>/panels`, `keys`, `raw`, `cels`, `strips`, `effects` and `final` as they become available. The hand-offs collect the relevant folders and notes for the chosen emoji. They omit stages you have not filled in.

## Plan the whole pack

At the bible stage, look for recognizable similarities between the proposed name, silhouette, palette and props and existing characters. Search using the proposed name and defining features, and compare the actual silhouette with the closest matches. Record what you checked and revise any combination that would cause confusion. Try the character at the target display size before generating the pack.

For a pack where elements recur, make an inventory before drawing cels. List each character, repeating design feature, prop, effect element and background element and which emoji will use it. Make model views for each one from the angles and states the action needs. Show a worn, gripped, placed or layered integration against the approved character. A container can use open and closed views. An effect can use the onset, peak and decay as its states. Record palette, line weight, scale, contact points and overlap. Detailed sheets pay off on recurring props and in scenes where parts need to fit together.

Scaffold from a seed inventory with `forge new project --emoji hammering --emoji logo --assets inventory.json`. `forge make` accepts the same `--assets` and repeated `--emoji` options. Use `--still logo` in a mixed pack. Inventory paths are relative to the project being created.

```json
{
  "assets": {
    "hammer": {
      "name": "Copper-banded hammer",
      "type": "prop",
      "status": "todo",
      "uses": ["hammering", "logo"],
      "model": ["images/assets/hammer/model.png"],
      "integration": ["images/assets/hammer/integration.png"]
    }
  }
}
```

When the PNG paths are omitted, Forge supplies the two paths shown above. Record design notes in the generated model and integration Markdown files. The storyboard receives the assets assigned to that emoji. Each frame plan includes these references alongside the preceding cel, nearest key and character model. Use `assets: ["hammer"]` on a panel or exposure to select the references relevant to it, for example when a prop is out of frame. Review the isolated assets first, then the integration views and motion, and finish with the whole-pack review.

## Cross-pack reviews

Use `forge review-pack asset --project project --asset hammer` for the isolated model views. Use `forge review-pack integration --project project --asset hammer` for those views plus the integration sheet and relevant storyboard, keys and strips. Omit `--asset` to review all assets in the selected level. Use `forge review-pack consistency --project project` for the lineup, asset views and scale reports.

Create `lineup.json` at the project root. Each declared asset lists one or more reference crops plus one or more crops for every emoji in its `uses` list. `file` is relative to the project. `box` is optional and uses source pixels in `[left, top, right, bottom]` order. For GIFs, `frame` is one-based. Supply the same `pixels_per_unit` for crops measured on equivalent canvases to preserve their relative scale on the sheet.

```json
{
  "assets": {
    "hammer": {
      "references": [{"file": "images/assets/hammer/model.png", "box": [40, 20, 160, 200]}],
      "appearances": {
        "hammering": [{"file": "emojis/hammering/cels/003-file.png", "box": [230, 50, 350, 230]}],
        "logo": [{"file": "emojis/logo/cels/001.png", "box": [330, 90, 450, 270]}]
      }
    }
  }
}
```

Run `forge lineup project project/lineup.png` and `forge drift project project/prop-drift.json --props`. Inspect each row for mismatched geometry, finish, grip or scale. The drift report compares colour, silhouette and appearance against the closest supplied view. Review flags against the intended pose and occlusion. Add the `forge check` output as `scale-check.json` to carry measured stability into the final bundle.

## One-shot mode

`forge make "a paper bird waving hello" --refs reference.png --count 1 --target slack --animated --yes --project project --json` starts a new pack. The CLI supplies an editable draft brief, model and asset scaffolds, storyboard and X-sheet, then advances until it needs an image, an optional approval, or finishes. Before generating, adjust the text notes or the storyboard to suit the idea.

- A `needs-image` result supplies the prompt, references and exact output path in `next-task.json`. Use the native image tool, save the result there, and run `forge make --resume --project project --json`. The agent can do this autonomously. In a scripted session, each resume processes completed steps without generating them again.
- Use `--static` for a still pack, `--scales 64,128,256,512` to select variants, and `--gate STAGE` for an optional review approval. After that approval, use `--resume --approve`. Use `--yes` to skip the gates. Automatic hand-offs record completed technical steps, so visually inspect the artwork and drift notices when you act as reviewer.
- To let the CLI call a tool that the harness exposes to scripts, pass a trusted Python `--generator adapter.py`. It receives the task JSON filename as its only argument, reads `prompt` and `references`, and writes the image at `output`. Choose an adapter that can make both generation and edit calls.
- If you intentionally set `FORGE_IMAGE_API_KEY`, Forge can perform the same calls using the OpenAI Images API. This path sends the supplied references to the provider and may incur API charges. Optionally set `FORGE_IMAGE_MODEL`. For the native-only workflow, leave the key unset. [Images API reference](https://developers.openai.com/api/reference/resources/images/methods/edit)
- Optionally add `effect.json` or `effect.frag` to an emoji's directory before the effects stage. Forge records accepted frame prompts in `image-prompts.jsonl`. The completed run returns the pack folder, ZIP and one overview. Share that overview in chat. See the [pack layout](workflow.md#report-and-distribution).
