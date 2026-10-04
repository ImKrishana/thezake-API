from curl_cffi import requests
import json
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def tataplay(url):
    match = re.search(r"/(?:movies|shows)/[^/]+/(\d+)", url)
    vod = match.group(1)
    if "movies" in url:
        type = "vod"
    else:
        type = "brand"
    api = f"https://tb.tapi.videoready.tv/content-subscriber-detail/api/content/info/{type}/{vod}?subscriberId=undefined&profileId=undefined"

    h = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    }
    response = requests.get(api, headers=h)
    result = {}
    data = response.json()
    meta = data.get("data").get("meta", {})
    title = meta.get("title", "") if meta.get("title") else meta.get("brandTitle", "")
    release_date = meta.get("releaseYear", "")
    result["title"] = f"{title} - ({release_date})"
    result["landscape"] = meta.get("boxCoverImage", "")
    result["portrait"] = meta.get("posterImage", "") if meta.get("posterImage") else meta.get("partnerPosterImage", "")
    return result

@router.get("/tataplay")
def tataplay_poster(url: str = Query(..., description="Tata Play movie/series URL")):
    try:
        result = tataplay(url)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": f"Tata Play scraping failed: {str(e)}"}, status_code=400)
