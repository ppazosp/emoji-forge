# Install and run Forge

## Skills CLI

From the project you want to use it in, run `npx skills add ppazosp/emoji-forge` with Node.js 22.20 or later and select your agent. Use `-a claude-code`, `-a codex`, or `-a cursor` to select an agent directly. Add `-y` to skip prompts or `-g` for a user-level install. The project install uses `.agents/skills/emoji-forge` for Codex and Cursor and adds an entry under `.claude/skills/emoji-forge` when Claude Code is selected. [Skills CLI requirements](https://github.com/vercel-labs/skills#install-a-skill) · [Flags](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) · [Supported agents and directories](https://github.com/vercel-labs/skills/blob/main/src/agents.ts)

## Claude Code marketplace

Run `/plugin marketplace add ppazosp/emoji-forge` and then `/plugin install emoji-forge@emoji-forge`. Invoke the skill as `/emoji-forge:emoji-forge`. Claude Code 2.1.275 or later also supports `/plugin install emoji-forge --marketplace ppazosp/emoji-forge` in one step inside a session. [Claude Code plugin installation](https://code.claude.com/docs/en/plugins/install)

## Manual copy

Clone the repository or download its source from [Releases](https://github.com/ppazosp/emoji-forge/releases). Copy the entire `skills/emoji-forge` directory, including its scripts, shaders, references and sample assets. From the checkout root, for Codex or Cursor:

```sh
mkdir -p /path/to/project/.agents/skills
cp -R skills/emoji-forge /path/to/project/.agents/skills/
```

For Claude Code, use `.claude/skills` instead of `.agents/skills`. [Agent Skills specification](https://agentskills.io/specification) · [Codex skill locations](https://developers.openai.com/codex/skills/) · [Claude Code skill locations](https://code.claude.com/docs/en/skills)

## Run the CLI

Install [uv](https://docs.astral.sh/uv/). Run `uv run forge --help` from the installed skill directory or `uv run --project SKILL_DIR forge --help` from your working directory. In a clone, `SKILL_DIR` is `skills/emoji-forge`.

Raster commands use Pillow. Add `--extra gpu` to `uv run` for ModernGL. For headless WebGL, add `--extra webgl` and use installed Chrome with `--channel chrome` on supported Forge commands, or install Chromium by running `uv run --extra webgl playwright install chromium` from the skill directory. See [shader rendering](shaders.md) and the [command reference](workflow.md).

## Test from a checkout

From the repository root, run `uv run --project skills/emoji-forge --extra gpu --extra test pytest -q`. Include headless WebGL tests with Chrome installed:

```sh
uv run --project skills/emoji-forge --extra gpu --extra webgl --extra test env FORGE_TEST_CHROME=chrome pytest -q
```
