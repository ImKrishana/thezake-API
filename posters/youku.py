import re
from curl_cffi import requests
import json
import html
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def youku(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    req = requests.get(url, headers=headers)

    if req.status_code != 200:
        return {"error": "Failed to fetch page"}

    html_content = req.text

    pattern = re.compile(
        r'"showName"\s*:\s*"(?P<title>[^"]+)",\s*'
        r'"showSubtitle"\s*:\s*"[^"]*",\s*'
        r'"completed"\s*:\s*(?:true|false),\s*'
        r'"showImg"\s*:\s*"(?P<landscape>[^"]+)",\s*'
        r'"showImgV"\s*:\s*"(?P<portrait>[^"]+)"'
    )

    match = pattern.search(html_content)

    if not match:
        return {"error": "Required metadata not found"}

    def decode_url(url_str):
        return html.unescape(url_str.replace("\\u002F", "/"))

    title = match.group("title")
    landscape = decode_url(match.group("landscape"))
    portrait = decode_url(match.group("portrait"))

    return {
        "title": title,
        "landscape": landscape,
        "portrait": portrait
    }


@router.get("/youku")
def youku_poster(url: str = Query(..., description="Youku content URL")):
    result = youku(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
