from curl_cffi import requests
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import json

router = APIRouter()

def shemaroo(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html"
    }

    html = requests.get(url, headers=headers, timeout=30).text

    img_match = re.search(
        r'image=(https?://[^|]+)',
        html,
        re.I
    )

    landscape = img_match.group(1) if img_match else None

    portrait = None
    if landscape:
        portrait = landscape.replace("16_9", "2_3")

    title_match = re.search(
        r'<h1[^>]*class="[^"]*section-title2[^"]*"[^>]*>(.*?)</h1>',
        html,
        re.S | re.I
    )

    title = re.sub(r'\s+', ' ', title_match.group(1)).strip() if title_match else None
    if not title:
        return {"error": "Failed to extract title from Shemaroo page"}
    return {
        "title": title,
        "portrait": portrait,
        "landscape": landscape
    }

@router.get("/shemaroo")
def shemaroo_poster(
    url: str = Query(..., description="shemaroo content URL")
):
    result = shemaroo(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
