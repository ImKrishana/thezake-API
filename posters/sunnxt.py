from curl_cffi import requests
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def find_image(images, img_type, resolution):
    for item in images.get("values", []):
        if item.get("type") == img_type and item.get("resolution") == resolution:
            return item.get("link")
    return None

def sunnxt(url):
    content_id = url.rstrip("/").split("/")[-1]

    api = f"https://pwaapi.sunnxt.com/content/v3/contentDetail/{content_id}/"

    params = {
        "level": "devicemax",
        "fields": (
            "contents,user/currentdata,images,generalInfo,subtitles,"
            "relatedCast,globalServiceName,globalServiceId,relatedMedia,"
            "thumbnailSeekPreview,tags,publishingHouse"
        )
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/144.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en",
        "Origin": "https://www.sunnxt.com",
        "Referer": "https://www.sunnxt.com/",
        "X-myplex-platform": "browser",
        "x-ucv": "5",
    }

    resp = requests.get(api, headers=headers, params=params, timeout=20)
    resp.raise_for_status()

    data = resp.json()["results"][0]

    images = data.get("images", {})
    general = data.get("generalInfo", {})

    landscape = find_image(images, "coverposter", "1920x1080")
    portrait = find_image(images, "thumbnail", "1000x1500")

    return {
        "title": f"{general.get('title')} ({general.get('displayTitle', '').split()[-1]})",
        "landscape": landscape,
        "portrait": portrait
    }

@router.get("/sunnxt")
def sunnxt_poster(url:str = Query(..., description="Sunnxt Content Url")):
    result = sunnxt(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result, status_code=200)
