from curl_cffi import requests
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def dangalplay(slug, slug_type):
    api = f"https://ottapi.dangalplay.com/catalogs/{slug_type}/items/{slug}.gzip?&region=IN&item_language=&auth_token=jqeGWxRKK7FK5zEk3xCM"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Referer": "https://www.dangalplay.com/"
    }

    response = requests.get(api, headers=headers)

    data = response.json()

    title = data.get("data")["title"]
    thumb = data.get("data")["thumbnails"]
    landscape = thumb.get("xl_image_16_9")["url"]
    portrait = thumb.get("xl_image_2_3")["url"]
    banner = thumb.get("xl_image_16_5")["url"]
    release_date = data.get("data").get("release_date", "")
    if not release_date:
        caption = data.get("data")["release_date_string"]
        release_date = caption.split("-")[0]


    return {
        "title": f"{title} - ({release_date})",
        "landscape": landscape,
        "portrait": portrait,
        "banner": banner,
    }

@router.get("/dangal")
def dangal_poster(url: str = Query(..., description="DangalPlay content url")):
    try:
        slug = url.split("/")[-1]
        slug_type = url.split("/")[-2]
        result = dangalplay(slug, slug_type)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
