from curl_cffi import requests
import json
from urllib.parse import urlparse
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def vivamax_movie(content_id: str) -> dict:
    api = (
        "https://api2.vivamax.net/v1/movie"
        f"?contentId={content_id}&restricted=false"
    )

    resp = requests.get(
        api,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Origin": "https://www.vivamax.net",
            "Referer": "https://www.vivamax.net/",
            "x-appname": "Vivamax/release-R57-18",
        },
        timeout=20
    )

    data = resp.json()["results"][0]

    return {
        "title": f"{data.get('title')} - ({data.get('release')})",
        "landscape": data.get("imageLandscape"),
        "portrait": data.get("imagePortrait"),
        "cover": data.get("image"),
    }

def vivamax_tvseries(series_title: str) -> dict:
    api = (
        "https://api2.vivamax.net/v1/tvseries"
        f"?seriesTitle={series_title}&restricted=false"
    )

    resp = requests.get(
        api,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Origin": "https://www.vivamax.net",
            "Referer": "https://www.vivamax.net/",
            "x-appname": "Vivamax/release-R57-18",
        },
        timeout=20
    )

    data = resp.json()["results"][0]

    images = resp.json()["seasons"][0]

    return {
        "title": f"{images.get("seriesTitle")} - ({data.get("release")})",
        "landscape": images.get("imageLandscape"),
        "portrait": images.get("imagePortrait"),
        "cover": images.get("image"),
    }

def vivamax(url: str) -> dict:
    url = url.split("#", 1)[0]

    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid Vivamax URL")

    content_type = parts[0]
    content_value = parts[1]

    if content_type == "movie":
        return vivamax_movie(content_value)

    elif content_type == "tvseries":
        return vivamax_tvseries(content_value)

    else:
        raise ValueError("Unsupported Vivamax content type")


@router.get("/viva")
def viva_poster(url: str = Query(..., description="Vivamax content URL")):
    result = vivamax(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
