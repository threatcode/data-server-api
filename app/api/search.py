import datetime
from typing import Optional

from pydantic import BaseModel
from readyapi import APIRouter, HTTPException

from app.services.es import get_es_client

router = APIRouter()


class SearchIndexRequest(BaseModel):
    search_query: str
    skip: int = 0
    size: int = 10
    type: Optional[str] = "scan"


class SearchIndexV2Request(BaseModel):
    search_query: str
    skip: int = 0
    size: int = 10
    type: Optional[str] = "scan"
    index: Optional[str] = None
    query: Optional[dict] = None
    sort: Optional[list] = None
    highlight: Optional[dict] = None


class SearchIndexV3Request(BaseModel):
    index_name: str
    search_query: dict
    skip: int = 0
    size: int = 10
    type: Optional[str] = None
    sort_query: Optional[list] = None


@router.post("/index")
async def search_elastic_search(req: SearchIndexRequest):
    es = get_es_client()
    data = []
    hits = 0
    try:
        if not req.type or req.type == "scan" or req.type == "":
            result = es.search(
                index="cyber_threat_intel",
                query={
                    "query_string": {"query": req.search_query, "default_field": "*"}
                },
                sort=[{"created_at": {"order": "desc"}}],
                size=req.size,
                from_=req.skip,
            )
            data = [item["_source"] for item in result["hits"]["hits"]]
            hits = result["hits"]["total"]["value"]
        elif req.type == "index":
            result = es.search(
                index="cyber_threat_intel",
                query={"match": {"id": req.search_query}},
                sort=[{"created_at": {"order": "desc"}}],
                size=req.size,
                from_=req.skip,
            )
            data = [item["_source"] for item in result["hits"]["hits"]]
            hits = result["hits"]["total"]["value"]
        return {"total_hits": hits, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/v2")
async def search_elastic_search_v2(req: SearchIndexV2Request):
    es = get_es_client()
    data = []
    hits = 0
    remaining_size = req.size
    current_skip = req.skip
    elastic_search_indices = req.index
    try:

        def search_across_indices(indices, query, sort, size, from_, highlight=None):
            return es.search(
                index=indices,
                query=query,
                sort=sort,
                size=size,
                from_=from_,
                highlight=highlight,
            )

        def process_results(result):
            nonlocal data, hits, remaining_size, current_skip
            data += [item["_source"] for item in result["hits"]["hits"]]
            hits += result["hits"]["total"]["value"]
            remaining_size -= len(result["hits"]["hits"])
            current_skip = max(0, current_skip - result["hits"]["total"]["value"])

        query = None
        sort = [{"created_at": {"order": "desc"}}]
        highlight = None
        if req.type == "index":
            query = {"match": {"id": req.search_query}}
            elastic_search_indices = req.index
        elif req.type == "scan" or req.type == "":
            query = {"query_string": {"query": req.search_query, "default_field": "*"}}
        elif req.type == "query":
            query = req.query
            sort = req.sort
            highlight = req.highlight
            remaining_size = req.size
            current_skip = req.skip
        else:
            query = {"query_string": {"query": req.search_query, "default_field": "*"}}
        current_month = datetime.datetime.utcnow().strftime("%Y-%m")
        current_index = f"scraped-threats-data-{current_month}"
        result = search_across_indices(
            elastic_search_indices or current_index,
            query,
            sort,
            remaining_size,
            current_skip,
            highlight,
        )
        process_results(result)
        previous_month = datetime.datetime.strptime(
            current_month, "%Y-%m"
        ) - datetime.timedelta(days=1)
        while remaining_size > 0 and previous_month >= datetime.datetime(2024, 4, 1):
            current_index = f"scraped-threats-data-{previous_month.strftime('%Y-%m')}"
            result = search_across_indices(
                current_index, query, sort, remaining_size, current_skip, highlight
            )
            process_results(result)
            previous_month = previous_month.replace(day=1) - datetime.timedelta(days=1)
        return {"total_hits": hits, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/v3")
async def search_elastic_search_v3(req: SearchIndexV3Request):
    es = get_es_client()
    try:
        result = es.search(
            index=req.index_name,
            query=req.search_query,
            sort=req.sort_query,
            size=req.size,
            from_=req.skip,
        )
        data = [item["_source"] for item in result["hits"]["hits"]]
        return {"total_hits": result["hits"]["total"]["value"], "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
