---
name: emoji-forge
description: Create or edit custom emoji, reaction stickers, static PNGs, or animated GIFs. Use when a user wants to draw, animate, add GLSL effects, or prepare an emoji pack for sharing.
license: MIT
compatibility: Uses uv and Python 3.11 or later. GPU effects can use ModernGL or Playwright Chromium.
---

# Emoji Forge

Run `uv run forge --help` from this skill folder, or pass its path with `uv run --project SKILL_DIR forge` from the working folder. Use individual commands on files and folders or `forge all` with an optional repeatable pack manifest. The [tool reference](references/workflow.md) covers both paths, including timing and Python hooks.

Explore ideas with the user. Sketch or discuss a storyboard when it helps, try poses or graphic treatments, and adapt to their feedback. Bring any cels or generate your own. Write shaders for the idea at hand using the [custom effect walkthrough](references/shaders.md). The bundled shaders are examples you can remix.

Check the result against the delivery target and compare it at the actual display size. Use `forge snapshot` before a revision and `forge compare` to show the difference. Read the [review tips](references/review-checklist.md) or the [Slack export reference](references/slack.md) when relevant. For ideas, see the optional craft notes on [timing](references/animation-timing.md), [expressions](references/expressions.md), and [common problems](references/lessons.md).
