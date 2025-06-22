from bson import ObjectId
from readyapi import APIRouter, HTTPException

from app.services.mongo import get_database

router = APIRouter()

db = get_database()


@router.get("/last-scrap-time")
async def get_last_time_scrap():
    doc = await db.scraped_status.find_one(
        {"_id": ObjectId("6718325775f9bc86ed23a71e")}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Not Found")
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/{id}")
async def get_stats(id: str):
    try:
        doc = await db.stats.find_one({"_id": ObjectId(id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Not Found")
        doc["_id"] = str(doc["_id"])
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
