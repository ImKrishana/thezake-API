from curl_cffi import requests
import json
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_hungama_tvshow(api_response: dict):
    try:
        show = api_response["data"]["head"]

        title = show.get("title")
        release_date = show.get("releasedate", "")
        year = release_date.split("/")[0] if release_date else None

        portrait = show.get("image", "").replace("_m", "_xl")
        landscape = show.get("tv_banner_listing_img")

        return {
            "title": f"{title} - ({year})" if year else title,
            "landscape": landscape,
            "portrait": portrait,
        }

    except (KeyError, TypeError):
        return None


def extract_hungama_movie(api_response: dict):
    try:
        movie = api_response["data"]["head"]["data"]

        title = movie.get("title")
        release_date = movie.get("releasedate", "")
        year = release_date.split("/")[0] if release_date else None

        portrait = movie.get("image", "").replace("_m", "_xl")
        landscape = movie.get("tv_banner_img")

        return {
            "title": f"{title} - ({year})" if year else title,
            "landscape": landscape,
            "portrait": portrait,
        }

    except (KeyError, TypeError):
        return None


def fetch_hungama(url: str):

    id_match = re.search(r"/(\d+)/?$", url)
    if not id_match:
        return None

    content_id = id_match.group(1)

    if "/movie/" in url:
        content_type = "movie"
    elif "/tv-show/" in url:
        content_type = "tvshow"
    else:
        return None

    api = f"https://cpage.api.hungama.com/v2/page/content/{content_id}/{content_type}/detail"

    params = {
        "lang": "",
        "alang": "en",
        "mlang": "en",
        "vlang": "en",
        "device": "web",
        "platform": "a",
        "storeId": "1",
        "uid": "1813500234",
        "country_code": "IN",
        "page_no": "1",
        "pagesize": "5",
        "pagination": "true",
        "ismusic": "false"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.hungama.com",
        "Referer": "https://www.hungama.com/"
    }

    response = requests.get(api, headers=headers, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    if content_type == "movie":
        return extract_hungama_movie(data)
    else:
        return extract_hungama_tvshow(data)

@router.get("/hungama")
def hungama(url: str = Query(..., description="Hungama content URL")):
    result = fetch_hungama(url)

    if not result:
        return JSONResponse(content={"error": "Failed to fetch metadata"}, status_code=400)

    return JSONResponse(content=result, status_code=200)
