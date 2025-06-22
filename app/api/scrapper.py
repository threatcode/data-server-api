from readyapi import APIRouter, Query, HTTPException
from typing import Optional
import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise RuntimeError("APIFY_TOKEN environment variable is required.")

client = ApifyClient(APIFY_TOKEN)

@router.get("/screenshot")
async def get_screenshot(url: str = Query(...)):
    try:
        run = client.actor("apify/screenshot-url").call(
            run_input={
                "delay": 5,
                "proxy": {"useApifyProxy": True},
                "scrollToBottom": False,
                "urls": [{"url": url}],
                "waitUntil": "networkidle0",
                "waitUntilNetworkIdleAfterScroll": False,
                "format": "png",
                "viewportWidth": 1280,
                "delayAfterScrolling": 2500,
                "waitUntilNetworkIdleAfterScrollTimeout": 30000,
                "selectorsToHide": ""
            }
        )
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items()["items"]
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twitter")
async def get_twitter(query: str = Query(...), max_item: Optional[int] = Query(10)):
    try:
        run = client.actor("apidojo/tweet-scraper").call(
            run_input={
                "customMapFunction": "(object) => { return {...object} }",
                "includeSearchTerms": False,
                "maxItems": min(int(max_item), 10),
                "minimumFavorites": 5,
                "minimumReplies": 5,
                "minimumRetweets": 5,
                "onlyImage": False,
                "onlyQuote": False,
                "onlyTwitterBlue": False,
                "onlyVerifiedUsers": False,
                "onlyVideo": False,
                "sort": "Latest",
                "tweetLanguage": "en",
                "searchTerms": query.split(","),
            }
        )
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items()["items"]
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 