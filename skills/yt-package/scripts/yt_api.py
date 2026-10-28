"""Shared YouTube Data API v3 helpers for the yt-package scripts.

Every call fails loudly: a missing key, an HTTP or quota error, or an empty
result exits non-zero with a message on stderr. The old yt-dlp scripts hit the
bot check, printed nothing and exited 0, so the skill reasoned over no data.

Key lookup: process env first, then ~/.claude/.env (same as outlier-radar and
metrics-pull). Needs YOUTUBE_API_KEY; YOUTUBE_CHANNEL_ID is the default channel.
"""

import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.googleapis.com/youtube/v3"

# Public views have counted from the first frame since this date. Earlier public
# counts used the stricter definition (now "engaged views", ~60% of public views),
# so a baseline that spans this date is inflated by the newer uploads.
VIEW_DEF_CUTOFF = datetime(2026, 8, 24, tzinfo=timezone.utc)

# The API has no Shorts flag. Shorts can run up to 3 minutes, so anything at or
# under 180s is treated as a Short.
SHORTS_MAX_SECONDS = 180

VIEWS_NOTE = (
    "Public views count from the first frame since 2026-08-24, so only uploads "
    "from that date on are compared. Engaged views (the old definition, about 60% "
    "of public views) and CTR are only in YouTube Studio."
)


def utf8_stdio():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def env(name):
    if os.environ.get(name):
        return os.environ[name]
    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def api(endpoint, **params):
    key = env("YOUTUBE_API_KEY")
    if not key:
        die("YOUTUBE_API_KEY is not set (process env or ~/.claude/.env).")
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode({**params, 'key': key})}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as res:
                return json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            reason, message = "", ""
            try:
                err = json.loads(e.read().decode("utf-8"))["error"]
                message = err.get("message", "")
                reason = err["errors"][0]["reason"]
            except Exception:
                pass
            if reason in ("quotaExceeded", "dailyLimitExceeded"):
                die(f"YouTube API quota exhausted ({reason}). It resets at midnight Pacific.")
            if (e.code == 429 or e.code >= 500) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            die(f"YouTube API {endpoint} failed: HTTP {e.code} {reason} {message}".strip())
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            die(f"YouTube API {endpoint} unreachable: {e}")


def chunks(seq, n=50):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def parse_duration(iso):
    """ISO 8601 duration (PT1H2M3S, P1DT2H) to seconds."""
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def resolve_channel(arg=None):
    """Channel ID from a UC... id, an @handle, or YOUTUBE_CHANNEL_ID."""
    arg = arg or env("YOUTUBE_CHANNEL_ID")
    if not arg:
        die("No channel given and YOUTUBE_CHANNEL_ID is not set (process env or ~/.claude/.env).")
    if re.fullmatch(r"UC[\w-]{22}", arg):
        return arg
    handle = arg if arg.startswith("@") else f"@{arg}"
    items = api("channels", part="id", forHandle=handle).get("items") or []
    if not items:
        die(f"No channel found for handle {handle}.")
    return items[0]["id"]


def channel_info(channel_id):
    items = api("channels", part="snippet,statistics,contentDetails", id=channel_id).get("items") or []
    if not items:
        die(f"Channel {channel_id} not found.")
    c = items[0]
    stats = c.get("statistics", {})
    return {
        "id": channel_id,
        "title": c["snippet"]["title"],
        "subs": None if stats.get("hiddenSubscriberCount") else int(stats.get("subscriberCount", 0)),
        "uploads": c["contentDetails"]["relatedPlaylists"]["uploads"],
    }


def upload_ids_since(uploads_playlist, since):
    """IDs of public uploads published at or after `since`, newest first."""
    ids, token = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": uploads_playlist, "maxResults": 50}
        if token:
            params["pageToken"] = token
        page = api("playlistItems", **params)
        items = page.get("items") or []
        older_seen = False
        for it in items:
            published = it["contentDetails"].get("videoPublishedAt")
            if not published:
                continue
            if parse_ts(published) >= since:
                ids.append(it["contentDetails"]["videoId"])
            else:
                older_seen = True
        token = page.get("nextPageToken")
        if older_seen or not token or not items:
            return ids


def fetch_videos(ids):
    """videos.list rows for the given IDs, in a flat analysis-ready shape."""
    now = datetime.now(timezone.utc)
    rows = []
    for batch in chunks(list(ids)):
        resp = api("videos", part="snippet,statistics,contentDetails", id=",".join(batch), maxResults=50)
        for v in resp.get("items") or []:
            sn, st = v["snippet"], v.get("statistics", {})
            published = parse_ts(sn["publishedAt"])
            seconds = parse_duration(v["contentDetails"].get("duration"))
            rows.append({
                "id": v["id"],
                "title": sn["title"],
                "channel": sn.get("channelTitle"),
                "channel_id": sn.get("channelId"),
                "published": published,
                "age_days": max((now - published).total_seconds() / 86400, 0.04),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)) if "likeCount" in st else None,
                "comments": int(st.get("commentCount", 0)) if "commentCount" in st else None,
                "seconds": seconds,
                "is_short": 0 < seconds <= SHORTS_MAX_SECONDS,
                "live": sn.get("liveBroadcastContent", "none") != "none",
                "thumbnail": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
            })
    return rows


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    mid = len(xs) // 2
    return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2


def quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def fmt_num(n):
    if n is None:
        return "N/A"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:.0f}"


def fmt_duration(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
