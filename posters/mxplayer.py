import re
from curl_cffi import requests
import json
from datetime import datetime
import uuid
from fastapi import APIRouter, Query
import html
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_title_from_h1(html_text):
    match = re.search(
        r'<h1[^>]*class=["\']sp-seo-title["\'][^>]*>(.*?)</h1>',
        html_text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return None

    title = html.unescape(match.group(1))
    title = re.sub(r'<.*?>', '', title)
    return title.strip()

def transform_bigpic_url(original_url):
    match = re.match(r"(.*?/16x9/)[^/]+/(.*?)(\.jpg)", original_url)
    if match:
        base_url = match.group(1)
        filename = match.group(2)
        return f"{base_url}3840x2160/{filename}.jpg"
    return None


def transform_portrait_url(original_url):
    match = re.match(r"(.*?/2x3/)[^/]+/(.*?)(\.jpg)", original_url)
    if match:
        base_url = match.group(1)
        filename = match.group(2)
        return f"{base_url}640x960/{filename}.jpg"
    return None


def transform_landscape_url(original_url):
    return re.sub(r"/16x9/[^/]+/", "/16x9/640x360/", original_url)


def mxplayer(url):
    id = url.split("-")[-1]
    if "show" in url:
        content_type = "tvshow"
        api = "https://api.mxplayer.in/v1/web/detail/collection"
    else:
        content_type = "movie"
        api ="https://api.mxplayer.in/v1/web/detail/video"

    params = {
        "type": content_type,
        "id": id,
        "userid": str(uuid.uuid4()),
        "platform": "com.mxplay.desktop"
    }

    res = requests.get(
        api,
        params=params,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    data = res.json()
    landscape = None
    portrait = None
    cover = None
    logo = None
    title = data.get("title")
    created_at = data.get("releaseDate")
    year = datetime.fromisoformat(
              created_at.replace("Z", "")
          ).year

    image = data.get("imageInfo")
    for img in image:
      if img.get("type") == "bigpic":
          landscape = "https://qqcdnpictest.mxplay.com/"+img.get("url")
      if img.get("type") == "portrait" or img.get("type") == "portrait_large":
          portrait = "https://qqcdnpictest.mxplay.com/"+img.get("url")
    logo = data.get("titleContentImageInfo")
    for log in logo:
      if log.get("type") == "banner_and_static_bg_desktop":
          cover = "https://qqcdnpictest.mxplay.com/"+log.get("url")
      if log.get("type") == "title_desktop":
          logo = "https://qqcdnpictest.mxplay.com/"+log.get("url")

    return {
        "title": f"{title} - ({year})",
        "landscape": transform_bigpic_url(landscape),
        "portrait": transform_portrait_url(portrait),
        "cover": cover,
        "logo": transform_landscape_url(logo)
    }


@router.get("/mxplayer")
def mxplayer_poster(url: str = Query(..., description="MX Player content URL")):
    result = mxplayer(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
