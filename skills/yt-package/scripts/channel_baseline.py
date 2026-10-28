#!/usr/bin/env python3
"""Expected-rank baseline for your channel (YouTube Data API).

Uses only long-form uploads published on/after 2026-08-24. From that date
public views count from the first frame, so older numbers are on a stricter
definition and would skew the baseline. The output is the views ladder of the
last N uploads. You set a video's expected rank (1 = best of the last 10)
against it before publishing, and compares that with Studio's "Ranking by views"
card at 24-48h.

CTR and engaged views are Studio-only and are not used.

Fails loudly (non-zero exit, message on stderr) on a missing key, an API error,
or no qualifying uploads.

Usage:
    python channel_baseline.py [--count 10] [--min-age 2] [--include-shorts]
                               [--channel UC...|@handle] [--json]
"""

import argparse
import json
import sys
from datetime import datetime

from yt_api import (VIEW_DEF_CUTOFF, VIEWS_NOTE, channel_info, die, fetch_videos, fmt_num, median,
                    quantile, resolve_channel, upload_ids_since, utf8_stdio)


def main():
    utf8_stdio()
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--count", type=int, default=10, help="latest N qualifying uploads (default 10)")
    p.add_argument("--min-age", type=float, default=2, help="skip uploads younger than this many days (default 2)")
    p.add_argument("--include-shorts", action="store_true")
    p.add_argument("--channel", help="UC... id or @handle (default YOUTUBE_CHANNEL_ID)")
    p.add_argument("--json", action="store_true", help="print JSON instead of the report")
    a = p.parse_args()

    channel = channel_info(resolve_channel(a.channel))
    print(f"Fetching {channel['title']} uploads since 2026-08-24 via YouTube Data API...", file=sys.stderr)

    ids = upload_ids_since(channel["uploads"], VIEW_DEF_CUTOFF)
    if not ids:
        die("The uploads playlist returned 0 public videos since 2026-08-24. Check the channel ID.")
    rows = [r for r in fetch_videos(ids) if not r["live"] and (a.include_shorts or not r["is_short"])]
    too_young = [r for r in rows if r["age_days"] < a.min_age]
    rows = [r for r in rows if r["age_days"] >= a.min_age]
    if not rows:
        die(f"No long-form upload since 2026-08-24 is at least {a.min_age:g} days old.")
    rows.sort(key=lambda r: r["published"], reverse=True)
    rows = rows[:a.count]

    views = [r["views"] for r in rows]
    settled = [r["views"] / r["age_days"] for r in rows if r["age_days"] >= 7]
    stats = {
        "n": len(rows),
        "median_views": median(views),
        "p25_views": quantile(views, 0.25),
        "p75_views": quantile(views, 0.75),
        "median_views_per_day_7d_plus": median(settled),
        "median_title_chars": median([len(r["title"]) for r in rows]),
    }
    ladder = sorted(rows, key=lambda r: r["views"], reverse=True)

    if a.json:
        def out(r):
            return {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in r.items()}
        print(json.dumps({"channel": channel, "since": "2026-08-24", "stats": stats,
                          "ladder": [out(r) for r in ladder], "too_young": [out(r) for r in too_young],
                          "note": VIEWS_NOTE}, indent=2, ensure_ascii=False))
        return

    div = "-" * 78
    print(f"{channel['title']} ({fmt_num(channel['subs'])} subs): expected-rank baseline, "
          f"last {len(rows)} long-form uploads since 2026-08-24")
    if len(rows) < 5:
        print(f"WARNING: only {len(rows)} qualifying uploads. The baseline is thin; say so when using it.")
    print(f"\nVIEWS LADDER (rank by views today; ages differ, so read it with the age column)\n{div}")
    print(f"{'Rank':>4}  {'Views':>7}  {'Age':>6}  {'Views/day':>9}  {'Chars':>5}  Title")
    for i, r in enumerate(ladder, 1):
        print(f"{i:>4}  {fmt_num(r['views']):>7}  {r['age_days']:>5.1f}d  {fmt_num(r['views'] / r['age_days']):>9}  "
              f"{len(r['title']):>5}  {r['title'][:60]}")
    print(div)
    print(f"Median views {fmt_num(stats['median_views'])}  "
          f"(middle half {fmt_num(stats['p25_views'])} to {fmt_num(stats['p75_views'])})")
    print(f"Median views/day, uploads 7+ days old: {fmt_num(stats['median_views_per_day_7d_plus'])}")
    print(f"Median title length: {stats['median_title_chars']:.0f} chars")
    if too_young:
        print(f"\nNot in the baseline yet (< {a.min_age:g} days old): "
              + "; ".join(f"{r['title'][:50]} ({fmt_num(r['views'])}, {r['age_days']:.1f}d)" for r in too_young))

    print("\nHOW TO USE IT")
    print("- Before publishing, write down an expected rank 1-10 (1 = best of the last 10) using this ladder.")
    print("- At 24-48h, read the real rank from Studio's 'Ranking by views' card (it compares videos at the")
    print("  same age, which this public-data ladder can't). Then apply the expected-rank swap rule.")
    print(f"- {VIEWS_NOTE}")


if __name__ == "__main__":
    main()
