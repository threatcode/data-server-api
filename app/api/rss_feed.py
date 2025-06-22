from typing import List, Optional

import feedparser
import requests
from bs4 import BeautifulSoup
from readyapi import APIRouter, HTTPException, Query

router = APIRouter()

HACKER_NEWS_FEED = "https://feeds.feedburner.com/TheHackersNews?format=xml"
GRAHAM_CLULEY_FEED = "https://grahamcluley.com/feed/"


def clean_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def parse_feed(url: str) -> List[dict]:
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch feed: {url}")
    feed = feedparser.parse(resp.content)
    cleaned_entries = []
    for entry in feed.entries:
        cleaned_entry = {
            k: clean_html(str(v)) if isinstance(v, str) else v for k, v in entry.items()
        }
        cleaned_entries.append(cleaned_entry)
    return cleaned_entries


@router.get("/")
async def get_rss_feed(source: Optional[str] = Query("hacker-news")):
    sources = [s.strip() for s in source.split(",") if s.strip()]
    feed = []
    for src in sources:
        if src == "hacker-news":
            feed.extend(parse_feed(HACKER_NEWS_FEED))
        if src == "graham-cluley":
            feed.extend(parse_feed(GRAHAM_CLULEY_FEED))
    return feed
