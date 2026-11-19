# Generate and edit a cel sequence

Look for image generation **and editing** in the active harness. In Codex, use its built-in image tool when available. Other agents may expose image editing through a native tool or an image-generation MCP. Inspect a local reference in the harness if required before attaching it to an edit. Keep the selected files in the working pack. If there is no image tool, use an external image API the user supplies, their hand-made art, or a [Python drawing hook](workflow.md#python-animation-hooks).

## Set the references before drawing in-betweens

1. Look at the user's reference images together. If consistency matters, lock a model sheet or turnaround and choose the expression, hand, pose and prop references worth reusing. The [production scaffold](production-pipeline.md) gives them a place to live.
2. Generate the key poses first. Edit from the locked sheet or an approved neighboring cel. Try two to four candidates for uncertain poses, then compare them at export size and keep the one that best communicates the idea.
3. Use the storyboard to name what changes in each beat. Put each distinct drawing on the X-sheet with its duration and key-pose reference. Give held drawings longer exposures to save generation calls. Use `forge plan` to turn these notes into a list of edits.

```sh
uv run forge plan project/emojis/wave/storyboard.json project/emojis/wave/plan.json \
  --x-sheet project/emojis/wave/x-sheet.json
```

## Thread each drawing through the image tool

- For each distinct cel, attach the previous accepted frame, the nearest approved key pose and the locked style sheet. Start the first frame from its key and the sheet. Use the previous cel as the edit target and the other images as references. Reuse an already generated key at its own exposure if it fits cleanly.
- Give the tool one short direction from the storyboard. For example, “Frame 07/24. Raise the arm 30° from frame 06 and leave the eyes half-closed. Steam rises above the cup. Keep the body, colors, crop and feet unchanged.”
- Ask for real transparency, or a single flat background color that differs from the subject. Use a consistent high-resolution canvas, position and scale to leave room for edits. Work large and let Forge downscale the exports.
- Re-anchor to the model sheet and nearest key after a pose change, or as soon as eyes, body shape, texture or line weight begin to shift. If a frame goes off-model, return to the last accepted cel or the key and regenerate the small change. Compare the new drawing with both neighbors before it becomes the next edit target.
- Save a prompt log with the reference filenames, selected outputs, model when known, and seeds or tool settings when the provider exposes them. Record an unavailable seed as unavailable.

| What you see | Edit to try |
| --- | --- |
| Palette or texture drifts | Attach the original sheet again, describe two or three distinguishing colors or textures, and edit a smaller area. |
| A hand, limb or prop doubles or goes missing | Re-edit from the last clean pose. Mask the joint or prop area where supported and describe what connects to what. |
| The expression changes the character's identity | Attach the expression sheet and nearest key. Mask just the mouth or eyelids, or use a tighter crop for the affected feature. |
| Text or watermark shapes appear | Re-edit the affected area with a mask or crop and ask for a blank surface. If it keeps recurring, use a clean reference image and redo the pose. |

## Import and check

```sh
uv run forge import project/emojis/wave/raw project/emojis/wave/cels --scale shared \
  --timing-spec project/emojis/wave/plan.json
uv run forge drift project/emojis/wave/cels/timing.json project/images/model project/emojis/wave/drift.json
```

`import` preserves transparent inputs, keys an edge-connected solid background, and aligns trimmed cels to a shared center or baseline. Pick `--scale shared` for raw edits that already share a working scale. `--scale fit` matches the longest visible side per cel. Use `--background keep` for an intentional background or pass a CSS color to key it explicitly. For a complex background, ask the image tool for an alpha cutout or bring a cutout you prepared separately. Import writes RGBA layers, a foreground body mask, and transformed body or face annotations if you supply them. Add or refine a torso mask and use `forge register` if a big prop or wing changes the bounding box.

`drift` compares colors, silhouette overlap and a small perceptual hash with the closest reference and neighboring frames. Give it a model pose or a folder of separately cropped views for a turnaround. Read the flags as review leads. A planned lighting change or exaggerated pose can legitimately score differently. Compare the render and reference before deciding what to redo.
