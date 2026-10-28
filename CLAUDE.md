# YouTube packaging skills: installer instructions for Claude Code

This repo is a pack of Claude Code skills, not an app. When someone opens it
in Claude Code and says "set me up", "install", or similar, walk them through
the steps below. One step at a time, and ask before writing any file.

## 1. Check Python

Run `python --version` (or `python3 --version`). They need 3.10 or newer.
If it's missing, say what to install and stop until it's there.

## 2. Copy the skills

Copy `skills/yt-package/`, `skills/yt-hooks/` and `skills/yt-search/` to
`~/.claude/skills/`. yt-package needs yt-search for its 14-day scan, so
install them together. If a folder already exists, ask before overwriting
it: they may have customized it.

## 3. Get a YouTube Data API key

Walk them through it:
1. console.cloud.google.com → create a project.
2. APIs & Services → Library → enable **YouTube Data API v3**.
3. Credentials → Create credentials → **API key**. Suggest restricting it to
   the YouTube Data API.

When they paste the key, write `YOUTUBE_API_KEY=...` to `~/.claude/.env`
yourself. Never put it in this repo, and never repeat it in chat.

## 4. Set their channel

Ask for their channel ID (starts with `UC`) or @handle and write
`YOUTUBE_CHANNEL_ID=...` to `~/.claude/.env`.

## 5. Test it once

Run `python ~/.claude/skills/yt-package/scripts/channel_baseline.py` and
show them the views ladder. If it errors, read the message and fix it
(missing key, wrong channel, API not enabled). Then suggest a first run:
`/yt-package <the next video they plan to make>`.

## 6. Other niches

The research in `skills/yt-package/references/packaging-meta.md` is from the
AI and tech niche. If they're in another niche, offer to edit the `TOOLS`
set in `channel_performance.py` with the brand and tool names their titles
lead with.
