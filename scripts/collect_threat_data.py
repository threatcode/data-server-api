import asyncio
import logging
import os
from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)
logger = logging.getLogger("collect_threat_data")

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "data_server")

HACKER_NEWS_FEED = "https://feeds.feedburner.com/TheHackersNews?format=xml"
GRAHAM_CLULEY_FEED = "https://grahamcluley.com/feed/"


def clean_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


async def fetch_and_store_feed(db, feed_url, source_name):
    logger.info(f"Fetching {source_name} feed...")
    resp = requests.get(feed_url, timeout=10)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch {source_name} feed: {resp.status_code}")
        return
    feed = feedparser.parse(resp.content)
    new_count = 0
    for entry in feed.entries:
        entry_clean = {
            k: clean_html(str(v)) if isinstance(v, str) else v for k, v in entry.items()
        }
        entry_clean["source"] = source_name
        # Use 'link' as a unique identifier
        if await db.threat_feeds.find_one({"link": entry_clean.get("link")}):
            continue
        await db.threat_feeds.insert_one(entry_clean)
        new_count += 1
    logger.info(f"Stored {new_count} new items from {source_name}.")


async def main():
    logger.info("Starting threat data collection...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    await fetch_and_store_feed(db, HACKER_NEWS_FEED, "hacker-news")
    await fetch_and_store_feed(db, GRAHAM_CLULEY_FEED, "graham-cluley")
    logger.info("Threat data collection completed.")


if __name__ == "__main__":
    asyncio.run(main())
