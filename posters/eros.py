from curl_cffi import requests
import json
import uuid
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def erosnow_org(url):
    code = url.split("/")[5]

    device_id = str(uuid.uuid4())
    api = f"https://pwaproxy.erosnow.com/api/v2/originals/{code}?img_quality=1&start_index=0&max_result=20&country=IN"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-country": "IN",
        "x-device-id": device_id,
        "x-platform": "WEB"
    }

    response = requests.get(api, headers=headers)
    data = response.json()

    title = data.get("title")
    release = data.get("release_date", "")
    year = release.split("-")[0] if release else ""

    images = data.get("images", {})

    landscape = None
    banner = None
    portrait = None
    logo = None
    cover = None

    for img_url in images.values():
        lower = img_url.lower()

        if "img625352" in lower or "625_352" in lower:
            landscape = img_url

        elif "img945380" in lower or "945_380" in lower:
            banner = img_url

        elif "imgkeyfrmhl1280x720" in lower:
            cover = img_url

        elif "imgorginalfeatured720x1280" in lower:
            portrait = img_url

        elif "imgonboarding450220" in lower:
            logo = img_url

    return {
        "title": f"{title} - ({year})" if year else title,
        "landscape": landscape,
        "portrait": portrait,
        "cover": cover,
        "banner": banner,
        "logo": logo
    }

def erosnow_movie(url):
    code = url.split("/")[5]

    device_id = str(uuid.uuid4())

    api = f"https://pwaproxy.erosnow.com/api/v2/catalog/movie/{code}?img_quality=1&optimized=true&country=IN"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "x-country":"IN",
        "x-device-id": device_id,
        "x-platform": "WEB"
    }
    response = requests.get(api, headers=headers)
    data = response.json()
    title = data.get("title", {})
    year = data.get("release_year", {})
    content = data.get("contents",{})
    img = data.get("images",{})
    for url in img.values():
        if "imgpostervl2000x3000" in url:
            portrait = url
            break
    for images in content:
        image = images.get("images",{})
        landscape = image.get("17",{})
        banner = image.get("9")

        return {
        "title": f"{title} - ({year})",
        "landscape": landscape,
        "portrait": portrait,
        "banner": banner,
        }

@router.get("/erosnow")
def erosnow(url: str = Query(..., description="Eros Now content URL")):
    if "/movie/" in url:
        result = erosnow_movie(url)
    else:
        result = erosnow_org(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
