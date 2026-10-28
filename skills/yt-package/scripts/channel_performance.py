#!/usr/bin/env python3
"""Which title patterns win on your channel right now (YouTube Data API).

Pulls every public upload in the window (uploads playlist -> videos.list), drops
Shorts and live/premiere placeholders, and scores each video as a multiple of the
median views of uploads from the same view-count era (before / after 2026-08-24,
when public views started counting from the first frame). Then it ranks the
videos and tags title patterns, so frames can be compared without the
view-definition change skewing them.

Fails loudly (non-zero exit, message on stderr) on a missing key, an API error,
or a window with no long-form uploads.

Usage:
    python channel_performance.py [--days 90] [--count 15] [--bottom 8]
                                  [--min-age 7] [--include-shorts]
                                  [--channel UC...|@handle] [--json]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

from yt_api import (VIEW_DEF_CUTOFF, VIEWS_NOTE, channel_info, die, fetch_videos, fmt_duration,
                    fmt_num, median, resolve_channel, upload_ids_since, utf8_stdio)

# Names that count as "tool name first". Edit this set for your own niche.
TOOLS = {"claude", "codex", "gpt", "gemini", "fable", "opus", "sonnet", "haiku", "anthropic", "openai",
         "cursor", "n8n", "obsidian", "notebooklm", "chatgpt", "grok", "deepseek", "astra", "sol", "luna",
         "jev", "rea", "higgsfield", "sora", "veo", "kimi", "qwen", "github", "copilot", "windsurf",
         "lovable", "supabase", "notion", "perplexity", "argon"}

HYPE = re.compile(r"\bNEW\b|changes everything|game[- ]changer|\bjust\b|\bINSANE\b|god mode|cheat code",
                  re.IGNORECASE)


def first_word(title):
    m = re.match(r"[A-Za-z0-9]+", title.strip())
    return m.group().lower() if m else ""


# (tag, test) pairs. Each test takes the title and returns True when the pattern is present.
PATTERNS = [
    ("tested / vs", lambda t: re.search(r"\b(tested|vs\.?|versus|beats?|benchmark(ed)?|raced?)\b", t, re.I)),
    ("first person (I / we)", lambda t: re.search(r"\b(I|I'm|I've|My|Me|We|We're)\b", t)),
    ("second person (you)", lambda t: re.search(r"\b(you|you're|your)\b", t, re.I)),
    ("parenthetical", lambda t: re.search(r"\(.+\)", t)),
    ("tool name first", lambda t: first_word(t) in TOOLS),
    ("count / $ / time", lambda t: re.search(
        r"#\d|\$\d|\b\d+x\b|\b\d+\s+(steps?|ways?|repos?|tools?|skills?|minutes?|hours?|days?|apps?)\b", t, re.I)),
    ("short verdict ([X] is [word].)", lambda t: re.fullmatch(r".{3,45}\b(is|are|was)\s+[\w'’-]+[.!]", t.strip(), re.I)),
    ("warning (stop / don't / never)", lambda t: re.search(r"\b(stop|don'?t|never|avoid|before you)\b", t, re.I)),
    ("contradiction (but / catch)", lambda t: re.search(r"\b(but|catch|truth|actually)\b", t, re.I)),
    ("anchor (since / biggest)", lambda t: re.search(r"\b(since|biggest)\b", t, re.I)),
    ("explainer / guide", lambda t: re.search(r"explained|guide|everything you need|master|tutorial", t, re.I)),
    ("hype word", lambda t: HYPE.search(t)),
    ("ends in ?", lambda t: t.strip().endswith("?")),
    ("> 60 chars", lambda t: len(t) > 60),
]


def tags_for(title):
    return [name for name, test in PATTERNS if test(title)]


def main():
    utf8_stdio()
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--days", type=int, default=90, help="window in days (default 90)")
    p.add_argument("--count", type=int, default=15, help="top videos to list (default 15)")
    p.add_argument("--bottom", type=int, default=8, help="bottom videos to list (default 8)")
    p.add_argument("--min-age", type=float, default=7, help="days before a video is judged (default 7)")
    p.add_argument("--include-shorts", action="store_true")
    p.add_argument("--channel", help="UC... id or @handle (default YOUTUBE_CHANNEL_ID)")
    p.add_argument("--json", action="store_true", help="print JSON instead of the report")
    a = p.parse_args()

    channel = channel_info(resolve_channel(a.channel))
    since = datetime.now(timezone.utc) - timedelta(days=a.days)
    print(f"Fetching {channel['title']} uploads since {since:%Y-%m-%d} via YouTube Data API...", file=sys.stderr)

    ids = upload_ids_since(channel["uploads"], since)
    if not ids:
        die(f"The uploads playlist returned 0 public videos since {since:%Y-%m-%d}. "
            "Check the channel ID and window; this is not a normal result.")
    rows = [r for r in fetch_videos(ids) if not r["live"] and (a.include_shorts or not r["is_short"])]
    if not rows:
        die(f"{len(ids)} uploads found but none are long-form. Re-run with --include-shorts if that is expected.")

    fresh = [r for r in rows if r["age_days"] < a.min_age]
    judged = [r for r in rows if r["age_days"] >= a.min_age]
    if not judged:
        die(f"No long-form upload is at least {a.min_age:g} days old in this window.")

    for r in rows:
        r["era"] = "new" if r["published"] >= VIEW_DEF_CUTOFF else "old"
        r["tags"] = tags_for(r["title"])
    era_median = {e: median([r["views"] for r in judged if r["era"] == e]) for e in ("old", "new")}
    for r in rows:
        base = era_median.get(r["era"])
        r["x"] = round(r["views"] / base, 2) if base else None
    judged.sort(key=lambda r: r["x"] or 0, reverse=True)

    pattern_rows = []
    for name, _ in PATTERNS:
        with_tag = [r["x"] for r in judged if name in r["tags"] and r["x"] is not None]
        without = [r["x"] for r in judged if name not in r["tags"] and r["x"] is not None]
        if with_tag:
            pattern_rows.append({"pattern": name, "n": len(with_tag), "median_x": round(median(with_tag), 2),
                                 "median_x_without": round(median(without), 2) if without else None})

    q = max(len(judged) // 4, 1)
    length = {
        "median_chars_all": median([len(r["title"]) for r in judged]),
        "median_chars_top_quartile": median([len(r["title"]) for r in judged[:q]]),
        "median_chars_bottom_quartile": median([len(r["title"]) for r in judged[-q:]]),
    }

    if a.json:
        def out(r):
            return {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in r.items()}
        print(json.dumps({"channel": channel, "window_days": a.days, "era_median_views": era_median,
                          "judged": [out(r) for r in judged], "too_fresh": [out(r) for r in fresh],
                          "patterns": pattern_rows, "length": length, "note": VIEWS_NOTE},
                         indent=2, ensure_ascii=False))
        return

    n_new = sum(r["era"] == "new" for r in judged)
    print(f"{channel['title']} ({fmt_num(channel['subs'])} subs): {len(judged)} long-form uploads judged, "
          f"last {a.days} days ({n_new} on/after 2026-08-24, {len(judged) - n_new} before)")
    print(f"Median views by era: before 08-24 {fmt_num(era_median['old'])}, from 08-24 {fmt_num(era_median['new'])}")
    print("x = views / median views of uploads from the same era (1.00x = a typical video)\n")

    div = "-" * 78

    def show(label, rs):
        print(f"{label}\n{div}")
        for i, r in enumerate(rs, 1):
            print(f"{i:>2}. {r['x']:>5.2f}x  {fmt_num(r['views']):>7}  {r['published']:%m-%d}  "
                  f"{len(r['title']):>3}ch  {r['title']}")
            if r["tags"]:
                print(f"{'':>30}[{', '.join(r['tags'])}]")
        print(div + "\n")

    show(f"TOP {min(a.count, len(judged))}", judged[:a.count])
    if a.bottom and len(judged) > a.count:
        show(f"BOTTOM {min(a.bottom, len(judged) - a.count)}", judged[-a.bottom:][::-1])

    print(f"TITLE PATTERNS (median x with the pattern vs without, n = videos with it)\n{div}")
    for pr in sorted(pattern_rows, key=lambda pr: pr["median_x"], reverse=True):
        without = f"{pr['median_x_without']:.2f}x" if pr["median_x_without"] is not None else "n/a"
        print(f"  {pr['pattern']:<34} {pr['median_x']:>5.2f}x  vs {without:>6}   n={pr['n']}")
    print(div)
    print(f"Length: median {length['median_chars_all']:.0f} chars overall, "
          f"{length['median_chars_top_quartile']:.0f} in the top quartile, "
          f"{length['median_chars_bottom_quartile']:.0f} in the bottom quartile\n")

    if fresh:
        print(f"TOO FRESH TO JUDGE (< {a.min_age:g} days)")
        for r in fresh:
            print(f"  {fmt_num(r['views']):>7}  {r['age_days']:.1f}d  {fmt_duration(r['seconds']):>7}  {r['title']}")
        print()

    print("NOTES")
    print(f"- {VIEWS_NOTE}")
    print("- Patterns are regex tags and n is small: treat the table as directional.")
    print("- Views keep growing after day 7, so the youngest judged videos are slightly understated.")


if __name__ == "__main__":
    main()
