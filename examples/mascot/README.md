# Ember

Ember is a small workshop fire who makes emoji for other people. The pack has six animated reactions and a still mark. Hammering, quench and idea use GLSL for the anvil sparks, steam and bulb glow. Sketch, ship and wave use only the drawn cels.

[Overview](ember/overview.gif) · [Download the ZIP](ember.zip) · [Names and usage](ember/NAMES.md) · [Slack-size files](ember/emoji/128/)

## Production

The animated reactions and logo ran through separate `forge make` projects and share the same native-generated character references. Each animated storyboard has four poses. The opening and peak are native image edits of the model with their thumbnail references. The two transitional drawings are native edits from those key cels and the model. Artwork comes from the image tool. Cropping, placement and effects run locally.

| Artifact | Animated pack | Static logo |
| --- | --- | --- |
| Reference art and asset list | [Bible](animated/style.md), [expressions](animated/expressions.md), [poses](animated/poses.md), [inventory](animated/assets.json) | [Bible](static/style.md), [inventory](static/assets.json) |
| Board to timed cels | [Hammer storyboard](animated/emojis/hammering/storyboard.md), [animatic](animated/review/hammering/sheets/animatic.gif), [X-sheet](animated/emojis/hammering/x-sheet.json), [image plan](animated/emojis/hammering/plan.json) | [Storyboard](static/emojis/logo/storyboard.md), [image plan](static/emojis/logo/plan.json) |
| Image requests | [Forge prompts](animated/image-prompts.jsonl), [actual native edit prompts](animated/native-edits.json) | [Forge prompts](static/image-prompts.jsonl) |
| Reviews | [Stage records and snapshots](animated/production.json) | [Stage records and snapshots](static/production.json) |
| Export checks | [Animated checks](animated/result/checks.json) | [Static check](static/result/checks.json) |

Both projects used the six review gates in `forge make`. The ready-to-edit image plans and native edit prompts are recorded in the table. The animated frames were imported with [goggle-landmark masks](animated/emojis/hammering/masks/), then registered before effects. Each emoji has two drift comparisons. `drift.json` compares its registration masks and `drift-art.json` compares the complete silhouettes. Props like the anvil and bucket explain style-only flags against the bare model. The stage records link to zipped snapshots that include the review notes.

The combined distribution comes from the 512 px masters. From the checkout root:

```sh
uv run --project skills/emoji-forge forge report examples/mascot/report.json build/ember --scales 64,128,256,512
```
