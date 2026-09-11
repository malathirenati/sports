# What this pipeline can't do

This repo trades cost and reliability for depth. It costs nothing and
never depends on a subscription, a laptop being on, or an app being open —
but it is a much shallower thing than the brief Claude writes for
`malathirenati.github.io/sports/brief/`. Read this before you point anyone
at the page it produces.

## It doesn't read anything

`generate_brief.py` never opens an article. It only reads the *RSS feed
entry* Google News returns — a title, a link, a source name, a timestamp.
It has no idea what the article actually says, whether the headline
oversells it, or whether the story is accurate at all.

The Claude-written brief, by contrast, fetches and reads every article in
full before writing a sentence about it, and checks with `curl` that every
cited URL still resolves and is the actual page the claim comes from. This
script does neither. A link can be dead, paywalled, or pointing at an
aggregator's rewrite of someone else's reporting, and the script has no
way to notice.

## It doesn't write anything

There's no summarizing, no synthesis, no house style, no judgment about
what matters. Each "story" on the page is just the RSS title verbatim
(lightly cleaned up — the ` - Publisher Name` suffix Google News appends
is stripped, nothing else). If a headline is clickbait, sensationalized,
or simply wrong, that's what gets published.

There's also nothing resembling the "opportunities" section of the
Claude-written brief — the unwritten angles a person or a model can spot
by actually thinking about the day's news. A search query can't propose
an op-ed idea.

## It doesn't verify sourcing

Google News aggregates from any outlet it indexes, including wire-service
reposts, SEO farms, and low-quality sites, with no per-source trust
signal. `docs/BRIEF.md`'s sourcing rules — real outlets only, no citing a
headline you never opened, no inferred URLs — have no equivalent here.
Nothing in this script distinguishes a *Reuters* report from a content
mill that scraped it.

## The links point at Google, not the source

Google News RSS doesn't hand back the publisher's own URL — it gives a
`news.google.com/rss/articles/...` redirect link that *forwards* to the
real article. Every link on the page is one hop removed from the actual
source. That's a step the main brief explicitly refuses to take: its
sourcing rules require the URL cited to be the page the claim comes from,
checked by fetching it directly. This script can't do that check, because
it never has the real URL to check in the first place.

## Freshness is not guaranteed

A live test run of this script pulled six headlines per bucket and mixed
same-day stories with ones from July, May, March, and even February. A
static search query has no sense of "recent" — it returns whatever Google
News currently ranks as relevant to the query, which is often evergreen
explainer content or old coverage that happens to still rank well, sitting
right next to this morning's news with no visual distinction between them.

## It doesn't dedupe or track history

Each run is stateless. If the same story is trending for three days
running, it will appear fresh in the RSS feed each morning and get
published again — there's no memory of what ran yesterday, unlike the
JSON-per-day archive the main brief keeps. The page also isn't dated or
archived; each day's run overwrites the last, so there's no way to look
back at last Tuesday's edition.

## It doesn't understand desks or lenses

The `BUCKETS` list is just six keyword searches loosely aimed at an
India/global and government/markets/society split. Google News has no
idea that's the intent — a query tagged "India — Society & Culture" might
just as easily return a business story that happened to mention a word in
the query. Nothing checks that a result actually belongs in the bucket it
landed in.

## It publishes without anyone looking at it first

The main brief asks for one approval — the push — after everything else
has run and validated. This pipeline has no such gate: whatever the script
produces goes live automatically, headlines and all, with no human or
model in the loop to catch something wrong before readers see it. That's
the price of "no approvals, no manual steps."

## It's brittle in ways a paid API wouldn't be

Google News RSS is a free, undocumented, unsupported feed. Google can
change its shape, rate-limit an IP range, or drop it entirely without
notice, and this script has no fallback if that happens — a run would
just come back with empty sections (the script tolerates a failed fetch
without crashing, but an empty brief and a silently broken brief look the
same from the outside unless someone checks).

## What would actually fix these

Every limitation above is a limitation of *not paying for anything*.
Each one has a real fix, and every fix costs money or attention:

- **Reading and verifying articles** needs something that can fetch and
  understand a page — an LLM API call per story, which costs per request.
- **Writing real summaries and spotting angles** needs the same thing.
- **Sourcing quality** needs either a curated outlet allowlist you
  maintain by hand, or a paid news API with source-tier metadata.
- **Deduplication and an archive** need a small amount of stored state
  (a database, or just committing dated JSON files the way the main site
  does) and the logic to diff against it.
- **A review gate** needs a human step back in the loop — which is exactly
  what the Claude desktop routine already gives you, at the cost of it
  only running while the app is open.

In short: this pipeline is what you get for $0 and no dependency on your
own machine. The version Claude writes in chat is what you get when a
person or a model actually does the reading. They are not substitutes for
each other.
