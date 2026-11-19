# Sprout · Python-hook fallback

Sprout shows a way to make emoji when you work with procedural art. The optional [Python hook](../build.py) draws frames and supplies separate body and face masks. The [source manifest](source-pack.json) calls it by name and adds a sparkle shader to hooray.

- [Character bible](style.md) · [Expressions](expressions.md) · [Poses](poses.md) · [Asset list](assets.json)
- [Coffee storyboard](emojis/coffee/storyboard.md) · [Animatic](review/coffee/sheets/animatic.gif) · [Exposure sheet](emojis/coffee/x-sheet.json)
- [Stage reviews and snapshot paths](production.json) · [Export checks](result/checks.json)
- [Pack overview](result/pack/overview.gif) · [Pack ZIP](result/pack.zip)

The overview mixes three animated GIFs and a still PNG. The ZIP includes 64, 128, 256 and 512 px versions. Sprout's stage notes review the existing drawings in the studio format.

From the repo root, rebuild the pack from the checked-in manifest.

```sh
uv run --project skills/emoji-forge --extra gpu forge all examples/demo/source-pack.json build/sprout --allow-scripts
```

To regenerate the production sheets and source manifest as well, run:

```sh
uv run --project skills/emoji-forge --extra gpu python examples/build.py build/sprout-studio
```
