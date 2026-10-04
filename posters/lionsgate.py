from curl_cffi import requests
import re
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
router = APIRouter()

def lionsgate(url):
    res = requests.get(url, timeout=20)
    if res.status_code != 200:
        return {"error": "Failed to fetch page"}
    html_text = res.text

    og_img_match = re.search(r'<meta property="og:image" content="([^"]+)"', html_text)
    portrait = og_img_match.group(1) if og_img_match else None
    title_match = re.search(r'<h1\s+class=["\']detail-title["\']\s*>(.*?)</h1>', html_text)
    year_match = re.search(r'<li\s+class=["\']detail-data-item["\']\s*>(.*?)</li>', html_text)

    title = title_match.group(1) if title_match else None
    year = year_match.group(1) if year_match else None

    clean_portrait = re.sub(r'/\d+w/', '/', portrait)

    landscape = re.sub(
        r'-spa-.*?\.jpg',
        '-lgi-landscape-poster-1920X1080-PSTL.jpg',
        clean_portrait
    )
    banner = re.sub(
        r'-spa-.*?\.jpg',
        '-spa-1536x613-DMHE.jpg',
        clean_portrait
    )

    return {
        "title": f"{title} - ({year})" if year else title,
        "portrait": clean_portrait,
        "landscape": landscape,
        "banner": banner
    }

@router.get("/lionsgate")
def lionsgate_poster(url: str = Query(..., description="Lionsgate movie URL")):
    result = lionsgate(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
