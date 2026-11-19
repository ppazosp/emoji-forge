---
name: emoji-forge
description: Create or edit custom emoji, reaction stickers, static PNGs, or animated GIFs. Use when a user wants to draw, animate, add GLSL effects, or prepare an emoji pack for sharing.
license: MIT
compatibility: Uses uv and Python 3.11 or later. GPU effects can use ModernGL or Playwright Chromium.
---

# Emoji Forge

Run `uv run forge --help` from this skill folder, or pass its path with `uv run --project SKILL_DIR forge` from the working folder. Use individual commands on files and folders or `forge all` with an optional repeatable pack manifest. The [tool reference](references/workflow.md) covers both paths, including timing and Python hooks.

Explore ideas with the user. Sketch or discuss a storyboard when it helps, try poses or graphic treatments, and adapt to their feedback. If the harness has native image generation and editing, such as Codex's built-in image tool or an image MCP, use it for characters, poses, expressions, props and in-betweens. For character packs, sketch a distinctive model and check its name and silhouette for resemblance to existing characters. Model the parts that recur, then thread each cel through the previous frame, nearest key, and relevant character, asset and integration sheets. [Frame-edit workflow](references/image-generation.md)

Use `forge new`, `sheets`, `stage` and `review-pack` for [production scaffolds and reviewer hand-offs](references/production-pipeline.md). If there is no native image tool, use a user-provided image API, hand-made art or a Python drawing hook.

## One-shot requests

Treat `make <idea>` after the skill name, or an equivalent request for a finished pack, as a one-shot request. Run `forge make "<idea>" --project <pack-dir> --json` yourself. Use a project directory in the user's workspace. Pass request details as CLI options. Use `--refs` for attached images, `--count` for pack size, `--target` for the platform preset, `--static` or `--animated` for the requested format, and `--emoji` for each explicitly named emoji. Pass `--yes` when they ask to skip approvals. Optional review gates are off by default.

When the result is `needs-image`, create the requested file with the available image tool and run `forge make --resume --project <pack-dir> --json`. Repeat until the result includes an overview and ZIP. On follow-ups about an unfinished pack, resume the same project using its saved `make.json`. Ask for approval only on `needs-review`, then resume with `--approve` when the user approves. Share the overview and ZIP when the run completes. See the [one-shot workflow](references/production-pipeline.md#one-shot-mode) for the full hand-off.

Write shaders for the idea at hand using the [custom effect walkthrough](references/shaders.md). The bundled shaders are examples you can remix.

Review individual assets, how they interact in motion, and the whole pack side by side with `forge lineup`. Use `forge check` with a model mask and a drift tolerance to catch unintended changes of scale or position. Use `forge snapshot` before a revision and `forge compare` to show the difference. Read the [review tips](references/review-checklist.md) or the [Slack export reference](references/slack.md) when relevant. For ideas, see the optional craft notes on [timing](references/animation-timing.md), [expressions](references/expressions.md), and [common problems](references/lessons.md).
