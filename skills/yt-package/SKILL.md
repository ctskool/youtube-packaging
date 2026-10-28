---
name: yt-package
description: Thumbnail-first YouTube packaging for your own channel. Runs an idea gate, pulls channel data (YouTube Data API, post-Aug-24 baselines), scans the last 14 days for competitor collisions, designs 3 thumbnail concepts, writes ~20 frame-stacked titles scored on a 40-point rubric with a hype penalty, then delivers 3 Test & Compare packages that differ in reason-to-click, a first-10-seconds delivery check and an expected-rank test plan. Use whenever the user wants title ideas, thumbnail ideas or thumbnail text, asks "what should I title this", "package this video", "title and thumbnail for...", "help me name this video", wants Test & Compare variants, or wants to re-package an underperforming video. Also triggers on /yt-package and /yt-titles, and on casual mentions of titling, naming or the thumbnail for a YouTube video.
---

# YouTube Packaging (Oct 2026 meta)

Packages a video: the thumbnail concept, the title that completes it, and the plan to test them. The output is 3 packages that each give a *different reason to click*, plus alternates, an avoid list, a cold open that pays off all three, and a test plan.

The examples below come from the AI and tech niche (October 2026). Your own channel's numbers come from the scripts in Step 2, and they win whenever the two disagree.

## Principles

1. **The thumbnail leads.** People browse thumbnails and read the title second. YouTube has even tested replacing titles with AI summaries. Design the thumbnail concept first, then write the title to finish its sentence.
2. **A reason, not a label.** "[Model] Is Here" is a label that every competitor already used on launch day. Put the product in the thumbnail and the stakes in the title.
3. **Make the topic clear and keep the outcome open.** A viewer should know the topic in about 1 second. The open loop belongs in the verdict or the result.
4. **Package before you produce.** If an idea can't become a strong title and thumbnail, say so before you film it.
5. **Deliver what the package promises.** Test & Compare picks winners on **watch-time share**, so over-promising loses even when it wins the click. Within the first 10–15 seconds, the video must pay off whichever package the viewer clicked.
6. **Trust beats hype.** Words like tested, benchmarked, "No Hype", real numbers and a known authority do better. "Changes everything", "game changer", "NEW" and a bare "just" show up about 2x more in the niche's losers than in its winners.
7. **Variants differ in concept, not wording.** Three versions of one hook give an inconclusive test, so each package needs a different reason to click.
8. **Judge by expected rank, not raw CTR.** CTR falls as reach grows, and YouTube says "no metric on its own" decides. Don't swap in the first ~24h: on most channels, early data is too thin to act on.

## Inputs

- **The topic, or the video plan.** If the user has a plan or outline for the video, read it: its so-what, its demo, and what the video can actually prove. If there's no topic at all, ask one question. Otherwise proceed.
- **New upload or re-package.** For a live video, get its URL or ID and its age. Then run the re-package path in Step 9.
- **Shorts:** Test & Compare doesn't run on Shorts. For a Short, write the title and the first frame only.

## Procedure

### Step 1: Idea gate

Write the **so-what** in one sentence: who it's for, what changes for them, and why now. Then pick **one dominant emotion** for the whole video: curiosity, fear of falling behind, relief, ambition, surprise or vindication. A single package may add one secondary emotion, such as the fear of overpaying in a cost package. That makes 2 at most, counting the dominant one.

Run three checks:
- **Coming second.** If the launch already has first-look videos, the angle has to be different: a test, a concrete use, the cost, or the catch. Coming second with a better angle beats coming first: Mansel's Projects video on day 15 did 10x, while Riley's on day 4 did 0.47x.
- **Jargon and audience size.** Name the widest audience that would care. If the core noun is new to them, the package needs a known anchor, such as "Claude Code", "since Skills" or a familiar rival.
- **The gate.** If you can't write the sentence, or the only reason to click is "X exists", stop. Say so and propose 1–2 sharper angles before packaging anything.

### Step 2: Data

Run both in parallel (each costs a few quota units):

```bash
python ~/.claude/skills/yt-package/scripts/channel_performance.py --days 90
python ~/.claude/skills/yt-package/scripts/channel_baseline.py --count 10
```

- **`channel_performance.py`** ranks each long-form upload as a multiple of its era's median. Eras split at 2026-08-24, when public views started counting from the first frame. It also prints median multiples per title pattern, title-length medians, and a bottom list of what to avoid.
- **`channel_baseline.py`** uses only uploads from 2026-08-24 onward. It prints the views ladder of the last 10, which is what the expected rank is set against.
- **Engaged views and CTR are Studio-only.** Neither script can see them. Say so in the output.
- **If a script exits non-zero, report the error.** Never package from memory as if the data had been pulled. A missing key means `YOUTUBE_API_KEY` has to go in `~/.claude/.env`.
- **Propose an expected rank (1 = best of the last 10)**, mark it for the user to confirm, and don't block on their answer. Method:
  - Pick 1–2 named analogues from the ladder: the same kind of video (rival model test, feature launch, repo) at a similar level of topic heat.
  - Compare views/day at similar ages, because ages on the ladder differ.
  - Move the estimate 1–2 places for collision saturation and timing (Step 3).
  - Show the analogues, so the user can check the reasoning.
- **Precedence:** live script output beats the dated channel priors in `references/packaging-meta.md`. The hype penalty and the retired templates still apply even if the channel's numbers don't show a penalty, because they come from niche-wide winner/loser data and are a trust rule.

### Step 3: 14-day collision scan

Each query costs 100 quota units. Give every query a different intent, because similar queries return the same videos:

1. **What's big:** the exact product or feature name, `--order viewCount`.
2. **Is the promise taken?** The angle's own words, e.g. "[product] vs [rival]", "[product] in Claude Code", "[product] cost".
3. **Only if the launch is under 3 days old:** the exact name with `--order date`, to catch uploads from the last 48 hours.

```bash
python ~/.claude/skills/yt-search/scripts/search.py "<query>" --days 14 --count 15 --order viewCount --lang en --no-shorts --json
```

`--json` gives each video's age and thumbnail URL. `--lang en` is only a ranking hint, so drop non-English videos and multi-topic news roundups from the collision table and list them in a single line.

From the results, list:
- **Same-topic titles:** channel, views ÷ subs ratio, age. A ratio on a video under 2 days old can't be judged yet, so mark it "too fresh".
- **Saturated frames:** e.g. 3+ "X Is Here" first looks means the label lane is closed.
- **Saturated visuals:** the top 5 same-topic thumbnails by views. Open each `hqdefault.jpg` URL in the browser pane (`preview_start` with the URL, then zoom). No download is needed.
- **Adjacent hits:** off-topic videos that share the angle, such as a big "I Tested X vs Y" on another model. They're worth noting but aren't collisions.
- **The open promise:** what no collision has promised yet. That's where the packages go.

Never reuse a collision's *template plus subject*, e.g. a second "I Tested [same model] vs Opus 5.5" or another "Google Is Back". Never reuse its thumbnail idea either. Frames themselves stay open: vs, tested and warning are fine as long as the subject, condition or stake is different.

### Step 4: Three thumbnail concepts first

The three concepts must differ **in kind**: a different visual idea and feeling, not a recolor or new text. Draw them from different families:
- **Object or metaphor:** a 3D Claude-orange object or mascot, a glowing laptop seam, an inside-the-head shot.
- **Proof or output:** an output collage, a before/after, the real number.
- **Person and tension:** a face plus one prop, a brutal split-screen, a triangle of 3 headshots.
- **Symbol:** removing a mask, a "leaked blueprint", a prestige book cover, a red FOMO trend line.

For each concept, give:
- **The top half.** TV rows can show only the top half, and it must sell the video on its own (cover the bottom half to test).
- **Text: 0–4 words, or none.** It complements the title and never repeats its words. Keep it "half as complicated": 28% of breakout thumbnails have no text. Readable overlay text and readable labels both count toward the 4 words. Logos, icons and print too small to read don't.
- **Face or faceless.** 69% of breakouts show a face. Faceless winners in this niche use a 3D orange object or mascot, an output collage, or a before/after.
- **One feeling, and the reason to click it carries.**

Retire these:
- Raw UI crops: recent Claude launches did 0.11–0.47x with them.
- Dense diagrams: a whiteboard map got 0.10x.
- The coordinator → green-checks fan-out diagram.
- The old March-2026 style taxonomy.

If the user wants mockups, offer image generation, but don't run it unasked.

### Step 5: About 20 titles that stack frames

Write about 20 titles, roughly 6–7 per thumbnail concept. Each title should **stack 2–4 frames** and **finish its concept's sentence**.

| Frame | Shape | Example (AI niche) |
|---|---|---|
| Verdict / test | tested, vs, same tasks, "(No Hype)" | I Tested GPT 6 Astra vs Fable 5.1 (No Hype Assessment), 423K |
| Anchor to known | "since X", "biggest since", known rival | Claude Mods Is The Biggest Claude Code Upgrade Since Skills, 216K |
| Contradiction | "…, but …", "the catch" | Sonnet 5.5 Beat Opus at Coding. But Check the Bill. |
| Warning | stop / don't / before you | Don't Move Your Agents to Sol 6.1 Until You See This |
| Insider | what they didn't say, inside X | Inside Anthropic's Git Replacement |
| Transformation | X into Y, from A to B | Claude Projects Turned 4 Terminals Into 1 Chat |
| Duration | overnight, 7 days, 30 days | I Left Claude Projects Running Overnight |
| Short verdict | "[Feature] is [word]." | Claude Projects Is the Night Shift. |
| Story | how X did Y | How Anthropic Outgrew Git |

Rules for every title:
- **A reason, not a label.** If it would still make sense as a changelog headline, rewrite it. The stakes go in the title and the product sits in the thumbnail.
- **Clarity on the topic, curiosity on the outcome.** The topic noun goes in the first ~40 characters, and the verdict or result stays open. A "but" creates the unresolved *why*.
- **Short verdicts** ("[Feature] is [word].") have a 5.1x median in the niche, but only when the thumbnail proves the verdict.
- **Trust signals:** tested, benchmarked, same tasks or same harness, "No Hype", a known authority, a timeframe, real numbers. Never use a $ figure that isn't real.
- **Length:**
  - Front-load the hook into the first ~40 characters.
  - Soft cap of 60 characters; niche winners have a median of ~52.
  - Flag anything over 60, because 61–75 characters is over-represented among losers.
  - Show the character count on every title.
- **Capitalization** is a consistency choice, not a lever. Use title case, plus at most one ALL-CAPS emphasis word.
- **No filler:** Ultimate Guide, Complete Tutorial, Everything You Need to Know, Explained, Master, and a "How to" prefix unless search intent demands it.
- **Retired templates:**
  - "Open Source Repo Solves #1 Problem"
  - "X + Y = CHEAT CODE / GOD MODE"
  - "Every X Explained in N Minutes"
  - "You're Using X Wrong", unless it's the single hottest topic of the week
- **Avoid these formats:** confessions ("I was wrong", <0.5x) and titles ending in "?" (0.82x).

### Step 6: Score

Score every title **as a cold viewer**, paired with its thumbnail concept. There are 8 criteria, each scored 0–5, for a maximum of 40:

| Criterion | 5 means | 0 means |
|---|---|---|
| Glance clarity | The topic is clear in ~1 second from the title and thumbnail | Unclear what it's about |
| Reason to click | A specific stake: a verdict, cost, risk or transformation | A label ("X Is Here") |
| Anchor / specificity | Concrete numbers, a known entity, an anchor to something known | Vague |
| Open loop | Must click to resolve the outcome | Gives the outcome away, or has nothing to resolve |
| Deliverability | The first spoken line pays it off, and it stays true if the demo is weak | Over-promises |
| Complementarity | Title and thumbnail each add something and form one reason | They repeat each other |
| Breadth | Any AI-curious viewer gets it; jargon is anchored | Insider jargon only |
| Differentiation | Unlike the 14-day collisions and the channel's last 10 titles | Near-duplicate of a collision |

**Hype penalty** (subtract from the total):

| Penalty | Applies to |
|---|---|
| −3 each | "changes everything", "game changer", "NEW" as the selling point, a bare "Just" ("Just Dropped/Got/Killed"), INSANE / GOD MODE / CHEAT CODE |
| −3 | Confession frame, filler/explainer words, a retired template |
| −2 | Ends in "?" |
| −2 | Over 60 characters |
| −5 | Any claim the video can't support. This also sets Deliverability to 0. |

- **Scoring before the video exists.** Most packaging happens before filming. Score a title whose promise depends on a result (a margin, a cost, "it worked") as if its gate is met, but cap Deliverability at 3 until the result exists. Write the gate in Step 7. If the gate fails on edit day, the title takes the −5 and switches to its fallback wording.
- **Studio baseline to beat.** Studio now writes channel-matched AI titles. If the user pastes Studio's suggestions, score them. If not, write a stand-in: the plainest *honest* label Studio would suggest, which is the topic noun plus their best non-hype shape, with no penalty items. Don't write a strawman. Mark it "Studio-style stand-in" and score it. **Every finalist must beat it by at least 5 and net 30 or more.**
- **Ties:** prefer the package that stays true if the demo is weak. Then prefer the one most different from the collisions, then the shorter one.
- **Optional judges** when the user has confirmed an expected rank of 1–3, or asks for them: run 3 judge subagents in parallel. They are a cold viewer, a deliverability-and-accuracy judge, and a differentiation-and-channel-fit judge. Each scores the pool blind; average their scores.

### Step 7: Three packages that differ in reason to click

- **Each package** is a title + thumbnail concept + thumbnail text + **the reason to click**, stated as the viewer's question. Three packages means three different questions.
- **Variant 1 is the safest package.** If Test & Compare finds no winner, variant 1 stays. It should stay true even if the demo underdelivers.
- **Gates:** state what must be true on edit day for each package (a number filled in, a result reached). Give the fallback wording if a gate fails.
- **Alternates:** 4–7, each with a "use when" condition, for round 2 or a re-package.
- **Avoid list for this video:**
  - fatigued words
  - the visuals the collisions already used
  - claims the demo doesn't support
  - format traps
- **Description, line 1:** the search term and entity nouns, because Ask YouTube (Gemini search) retrieves on them. Search is still only 5–10% of traffic for most channels.

### Step 8: First-10-seconds delivery check

- **Write the cold open** (≤15 seconds, word for word) so that it **pays off all three packages**. Misleading packaging can lose 60–70% of viewers in the first 10 seconds.
- **Check each package:** does the video pay off this promise in 10–15 seconds? If not, fix the cold open or drop the package.
- **Add a partial-result line** if the demo might fall short ("If the run is partial: …").
- **For a full hook,** offer /yt-hooks.

### Step 9: Test plan

**New upload:**
1. **Load the 3 packages into Test & Compare as title + thumbnail pairs,** with variant 1 the safest. Each pair is one reason to click, and mixing halves from different packages breaks that reason. Use desktop Studio and a normal upload, not a Premiere.
2. **Write the expected rank (1–10)** against the post-Aug-24 baseline before publishing.
3. **First ~24h: touch nothing.** Editing a title or thumbnail mid-test stops the test. Don't read raw CTR.
4. **At 24–48h,** apply the expected-rank swap rule below.
5. **About 2 weeks later,** re-package flops using the alternates. Make this a habit roughly every 2 weeks.

**Round 2 (a new upload that tanked in its first days):** run another pairs test. Use the current best variant plus 2 alternates whose gates are met, and each alternate must bring a **new thumbnail concept**, not only a new title.

**Re-package (live video, weeks old):**
- **Change the thumbnail concept first:** run a thumbnail-only test of 3 concepts, keeping the best title. Test titles after that.
- **Test pairs only** when a flatlined evergreen video needs an entirely new concept.
- **Practice on older videos.** YouTube recommends testing older videos first, so use the back catalog to practise.

**Expected-rank swap rule.** E is the expected rank you wrote before publishing. A is Studio's **"Ranking by views"** card at 24–48h; it compares videos at the same age, which public data can't do.

| Situation | Action |
|---|---|
| A ≤ E + 2 (met it, or close) | Leave it alone. Good data beats no data, and the test keeps running. |
| E is 1–3 and A is 6–10 (a high-expectation video landed in the bottom half) | Act fast. End the test and start round 2 (above). |
| Anything else below E | Leave it. If it's still below E at about 2 weeks, re-package it in the sweep. |
| Rank is fine but retention or satisfaction is poor | The video is the problem, not the package. Don't swap. |

## The Oct-2026 toolkit

| Tool | What it does | How to use it |
|---|---|---|
| **Test & Compare** | Up to 3 titles, thumbnails or pairs. The winner is chosen on watch-time share, and a small control group sees only the default. Editing mid-test stops it. Desktop Studio only. Excludes Shorts, Made for Kids, mature and live. | The main test. Variants must differ in concept. |
| **Dynamic thumbnails** (Made on YouTube, 2026-09-23) | Up to 3 thumbnails, each shown to a different audience segment. This is personalization, not a single-winner test. | Never during a Test & Compare run. Afterwards, if the audience splits (heavy users vs broader AI viewers), give each segment its concept. |
| **Hook A/B of video cuts** (coming soon) | Tests opening cuts. | When it ships, test 2 cold opens that both pay off the lead package. |
| **Studio auto-swap** (coming later) | Swaps thumbnails that underperform. | When it ships, make sure it can't swap during a Test & Compare run. |
| **Studio AI titles and thumbnails** | Generated in the channel's style. | The baseline every finalist must beat (Step 6). |
| **Ask Studio** (replaced the Inspiration tab, Aug 2026) | Audience and idea questions inside Studio. | Ask it what the audience is searching for and watching. The Inspiration tab is gone; never point the user there. |
| **Ask YouTube** and custom Home feeds | Gemini search, plus feeds users can steer. | Entity nouns in the title and description line 1 help retrieval. |

## Output format

```
## Idea gate
So-what: [one sentence]. Emotion: [one]. Angle vs the collisions: [one line]. [PASS, or STOP + sharper angles]

## Data
Baseline (last N since 08-24): median [X] views, ladder [top..bottom]. Patterns winning now: [2–3 with x].
Expected rank: [E]/10, proposed: [reason]. You confirm.
Note: engaged views and CTR are Studio-only.

## Collisions (last 14 days)
| Title | Channel | Ratio | Age | Frame / visual |
Saturated: [...]. Open promise: [...].

## Thumbnail concepts
A. [name]: top half [...]; text [0–4 words]; face/faceless; feeling; reason it carries
B. ...
C. ...

## Title pool (scored)
| # | Title (chars) | Concept | Frames | Score − penalty = net |
Studio-style baseline: [title], net [N]. Cut: [titles that didn't beat it].

## Package
### Lead (Test & Compare variant 1)
Title, thumbnail, why it leads
### Test & Compare set
| Slot | Title (chars) | Thumbnail + text | Reason to click |
Gates: [...]
### Alternates
| Title | Thumbnail text | Use when |
### Avoid
[...]
Description line 1: [...]

## First 10 seconds
[cold open, word for word, which pays off A/B/C] + partial-result line

## Test plan
[new-upload or re-package steps, E, and the swap rule applied to this video]

## Notes
[steps skipped or failed, assumptions such as gate-scoring, and the publish-timing window if the topic is time-sensitive]
```

**Where it goes:**
- **If the user has a plan file for the video,** write the `## Package` and `## Test plan` sections into it, replacing any existing ones, and say so.
- **Otherwise,** reply in chat and offer to save it as `YYYY-MM-DD-<slug>-package.md` wherever they keep video plans.

## Hard rules

- **Thumbnail concepts come before titles.** Never ship a title without its picture.
- **The 3 packages differ in reason to click,** not in wording.
- **No label titles, filler, hype words, confessions or "?" endings,** unless a scored exception is explained.
- **No claim the video can't support,** and no $ figures that aren't real.
- **Thumbnail text never repeats the title.**
- **Don't swap or edit in the first ~24h.** Don't read raw CTR for swap decisions.
- **Baselines use uploads from 2026-08-24 onward only.**
- **A data step that failed is reported as failed,** never filled in from memory.

## References

- `references/packaging-meta.md`: frame multiples, niche winners vs losers (AI niche, 2026-10-14 snapshot), thumbnail styles, platform changes and sources.
- **Your channel:** `scripts/channel_performance.py` and `scripts/channel_baseline.py` (Step 2).
