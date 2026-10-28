# YouTube packaging skills for Claude Code

Three skills for packaging a YouTube video before you film it: the thumbnail, the title, the hook and the plan to test them. They read your own channel's numbers through the YouTube Data API.

| Skill | What it does | Run it with |
|---|---|---|
| **yt-package** | Checks the idea, pulls your channel's numbers, scans the last 14 days for videos on the same topic, then gives you 3 thumbnail concepts, about 20 scored titles, 3 packages for YouTube's Test & Compare, a cold open and a test plan | `/yt-package <your video idea>` |
| **yt-hooks** | Writes the first 15 seconds: what viewers see, hear and read, scored against four rules (alignment, speed, clarity, curiosity) | `/yt-hooks <your video idea>` |
| **yt-search** | Searches YouTube with view counts and ages. yt-package uses it for the 14-day scan | `/yt-search <query>` |

## What you need

- [Claude Code](https://claude.com/claude-code)
- Python 3.10 or newer (the scripts use only the standard library)
- A free YouTube Data API key: Google Cloud Console → create a project → enable **YouTube Data API v3** → Credentials → **API key**
- Your channel ID (starts with `UC`) or your @handle

The free quota is 10,000 units a day. One full package uses a few hundred.

## Install

Clone the repo, open it in Claude Code, and say **"set me up"**. Claude walks you through it (see [CLAUDE.md](CLAUDE.md)).

Or by hand:

1. Copy `skills/yt-package`, `skills/yt-hooks` and `skills/yt-search` into `~/.claude/skills/`.
2. Add your key and channel to `~/.claude/.env` (see [.env.example](.env.example)):
   ```
   YOUTUBE_API_KEY=your-key
   YOUTUBE_CHANNEL_ID=UC...   # or @yourhandle
   ```
3. Check it works:
   ```bash
   python ~/.claude/skills/yt-package/scripts/channel_baseline.py
   ```

## How yt-package works

1. **Idea gate.** One sentence: who it's for, what changes for them, and why now. If it can't write that, it says the idea isn't ready and suggests sharper angles.
2. **Your data.** Ranks your recent uploads against your own median and shows which title patterns win on your channel.
3. **Collision scan.** What's already out on the topic in the last 14 days, so you don't repeat it.
4. **Thumbnails first.** Three concepts that differ in kind, then titles written to finish each thumbnail's sentence.
5. **Score.** About 20 titles on a 40-point rubric, with penalties for hype words and claims the video can't back up.
6. **Packages.** Three title-and-thumbnail pairs, each a different reason to click, ready for Test & Compare.
7. **First 10 seconds and a test plan.** A cold open that pays off all three packages, and when to swap.

The niche research in `skills/yt-package/references/packaging-meta.md` comes from the AI and tech niche (October 2026). Your channel's numbers come from the scripts and win whenever the two disagree. If you're in another niche, edit the `TOOLS` list at the top of `channel_performance.py`.

## License

MIT
