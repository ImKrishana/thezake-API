import re
import json
from curl_cffi import requests
import html
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def wetv(url: str):
    cid = url.split("/")[5]
    headers = {"User-Agent": "Mozilla/5.0"}

    api = f"https://wetv.vip/api/play?cid={cid}"

    jr = requests.get(api, headers=headers, timeout=15)
    data = jr.json()

    title = data["playData"]["coverInfo"]["title"]
    year = data["playData"]["coverInfo"]["year"]
    landscape = data["playData"]["coverInfo"]["posterHz"]
    portrait = data["playData"]["coverInfo"]["posterVt"]

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape,
        "portrait": portrait
    }



@router.get("/wetv")
def wetv_poster(url: str = Query(..., description="Wetv.vip content URL")):
    result = wetv(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
