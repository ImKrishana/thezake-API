from curl_cffi import requests
import json
from urllib.parse import urlparse
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import datetime
router = APIRouter()

def build_image_url(image_obj, ext):
    return (
        image_obj["url"]
        .replace("{w}", str(image_obj["width"]))
        .replace("{h}", str(image_obj["height"]))
        .replace("{f}", ext)
    )


def extract_apple_tv_images(data):
    content = data.get("data", {}).get("content", {})
    images = content.get("images", {})

    title = (
        content.get("previewVideoTall", {})
               .get("content", {})
               .get("title")
    )
    year = content.get("releaseDate")
    dt = datetime.datetime.fromtimestamp(year / 1000, datetime.UTC)
    year_str = dt.strftime("%Y")
    if not title:
        title = content.get("title")


    result = {
        "title": f"{title} - ({year_str})" if year_str else title,
        "landscape": build_image_url(
            images.get("contentImage16X9"), "jpg"
        ) if images.get("contentImage16X9") else None,
        "portrait": build_image_url(
            images.get("contentImageTall"), "jpg"
        ) if images.get("contentImageTall") else None,
        "logo": build_image_url(
            images.get("contentLogo"), "png"
        ) if images.get("contentLogo") else None
    }

    return result


def extract_apple_id(url: str) -> str:
    path = urlparse(url).path
    return path.rstrip('/').split('/')[-1]

def apple(url):
    if "movie" in url:
        type = "movies"
    elif "show" in url:
        type = "shows"
    else:
        return {"error": "Invalid Apple TV URL. Must contain 'movie' or 'tv-show'."}
    endpoint = extract_apple_id(url)

    api = f"https://tv.apple.com/api/uts/v3/{type}/{endpoint}"
    params = {
        "caller": "web",
        "locale": "en-US",
        "pfm": "web",
        "platterPassThrough": "true",
        "sf": "143441",
        "utscf": "OjAAAAEAAAAAAAIAEAAAACMAKwAtAA~~",
        "utsk": "6e3013c6d6fae3c2::::::235656c069bb0efb",
        "v": "92"
    }

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Referer": "https://tv.apple.com/",
    }

    cookies = {
        "geo": "IN"
    }

    response = requests.get(
        api,
        params=params,
        headers=headers,
        cookies=cookies,
        timeout=20
    )
    print("Status Code:", response.status_code)
    if response.status_code != 200:
        return {"error": f"Failed to fetch data from Apple TV API (Status Code: {response.status_code})"}
    data = response.json()

    extracted = extract_apple_tv_images(data)
    return extracted


@router.get("/apple")
def apple_poster(
    url: str = Query(..., description="Apple content URL")
):
    result = apple(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
