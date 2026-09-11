#!/usr/bin/env python3
"""
Generates the Daily Sports Brief as a static HTML page by pulling
headlines from Google News RSS — no API key, no paid service, no LLM,
no third-party Python packages (standard library only).

To change what gets pulled: edit BUCKETS below. Each entry is
(section title, Google News search query). Nothing else needs to change.

To change the output location: edit OUTPUT_PATH. The workflow publishes
whatever is in ./public to GitHub Pages, so keep output under public/.
"""

import datetime
import html
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

BUCKETS = [
    ("India — Government & Policy",
     "India sports policy OR governance OR federation OR doping"),
    ("India — Markets & Money",
     'India sports sponsorship OR "broadcast rights" OR IPL business'),
    ("India — Society & Culture",
     "India sports women OR grassroots OR participation"),
    ("Global — Government & Policy",
     "sports doping OR governance OR Olympic committee OR court ruling"),
    ("Global — Markets & Money",
     'sports sponsorship OR "broadcast rights" OR franchise valuation'),
    ("Global — Society & Culture",
     "women's sport OR sports inclusion OR fan culture"),
]

ITEMS_PER_BUCKET = 6
FEED_LOCALE = "hl=en-IN&gl=IN&ceid=IN:en"
OUTPUT_PATH = os.path.join("public", "brief", "index.html")
REQUEST_TIMEOUT = 15


def fetch_bucket(query: str) -> list:
    """Fetch and parse a Google News RSS feed for one search query.
    Returns an empty list (never raises) if the feed can't be fetched
    or parsed, so one bad query doesn't take down the whole run.
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&{FEED_LOCALE}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            raw = response.read()
    except Exception as error:
        print(f"  ! feed fetch failed for {query!r}: {error}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        print(f"  ! feed parse failed for {query!r}: {error}")
        return []

    items = []
    for item in root.findall("./channel/item")[:ITEMS_PER_BUCKET]:
        title = clean_title(item.findtext("title", default=""))
        link = (item.findtext("link", default="") or "").strip()
        pub_date = (item.findtext("pubDate", default="") or "").strip()
        source_el = item.find("source")
        source = source_el.text.strip() if source_el is not None and source_el.text else ""
        if title and link:
            items.append({
                "title": title,
                "link": link,
                "source": source,
                "pub_date": format_date(pub_date),
            })
    return items


def clean_title(raw_title: str) -> str:
    """Google News titles end in ' - Publisher Name'; strip that off."""
    title = html.unescape(raw_title or "").strip()
    return re.sub(r"\s+-\s+[^-]+$", "", title).strip()


def format_date(rfc822_date: str) -> str:
    """Turn an RSS pubDate into a short human-readable UTC timestamp.
    Falls back to the raw string if it can't be parsed.
    """
    if not rfc822_date:
        return ""
    try:
        parsed = parsedate_to_datetime(rfc822_date)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(datetime.timezone.utc)
        return parsed.strftime("%b %d, %H:%M UTC")
    except (TypeError, ValueError):
        return rfc822_date


def render_html(sections) -> str:
    generated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    section_html = []
    for title, items in sections:
        if not items:
            body = '<p class="empty">No headlines returned for this query today.</p>'
        else:
            rows = "\n".join(
                '<li><a href="{link}" target="_blank" rel="noopener">{title}</a>'
                '<span class="meta">{source}{sep}{date}</span></li>'.format(
                    link=html.escape(item["link"]),
                    title=html.escape(item["title"]),
                    source=html.escape(item["source"]),
                    sep=" · " if item["source"] and item["pub_date"] else "",
                    date=html.escape(item["pub_date"]),
                )
                for item in items
            )
            body = f"<ul>{rows}</ul>"
        section_html.append(f"<section><h2>{html.escape(title)}</h2>{body}</section>")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MNR Sports News — Daily Brief (auto)</title>
<meta name="robots" content="noindex">
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          max-width: 760px; margin: 0 auto; padding: 2rem 1.25rem 4rem;
          line-height: 1.5; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
  .subtitle {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
  .disclaimer {{ background: #fff8e1; border: 1px solid #e8d68a; border-radius: 8px;
                 padding: 0.75rem 1rem; font-size: 0.85rem; margin-bottom: 2rem; }}
  section {{ margin-bottom: 2rem; }}
  h2 {{ font-size: 1.05rem; border-bottom: 1px solid #ddd; padding-bottom: 0.35rem; }}
  ul {{ list-style: none; padding: 0; margin: 0.75rem 0 0; }}
  li {{ margin-bottom: 0.9rem; }}
  li a {{ font-weight: 600; text-decoration: none; }}
  li a:hover {{ text-decoration: underline; }}
  .meta {{ display: block; color: #777; font-size: 0.78rem; margin-top: 0.15rem; }}
  .empty {{ color: #999; font-style: italic; }}
  footer {{ color: #999; font-size: 0.78rem; margin-top: 3rem; }}
</style>
</head>
<body>
  <h1>MNR Sports News — Daily Brief</h1>
  <p class="subtitle">Auto-generated {generated_at}</p>
  <p class="disclaimer">
    <strong>This page is machine-generated, not written or reviewed by a
    person or an AI.</strong> It lists raw headlines pulled from Google News
    RSS, grouped by search query — nothing here has been read in full,
    fact-checked, or confirmed to still resolve. See
    <code>LIMITATIONS.md</code> in the repo for what that means in practice.
  </p>
  {''.join(section_html)}
  <footer>Generated by scripts/generate_brief.py — a free, keyless, no-AI pipeline.</footer>
</body>
</html>
"""


def main() -> None:
    print(f"Building brief from {len(BUCKETS)} buckets...")
    sections = []
    for title, query in BUCKETS:
        print(f"  fetching: {title}")
        items = fetch_bucket(query)
        print(f"    -> {len(items)} headlines")
        sections.append((title, items))

    page = render_html(sections)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
