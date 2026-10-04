from curl_cffi import requests
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def fix_image(url, variant="desktopDetail"):
    if not url:
        return None

    if "imagedelivery" in url and not url.endswith(variant):
        return f"{url}/{variant}"

    return url


def fetch_aaonxt(url):
    slug = url.split("/")[-1]
    if "series" in url:
        base = "https://aaonxt.com/_next/data/8L0k5Obx_zXhq4cp-uJC7/series"
        id = "webSeriesId"
    else:
        base = "https://aaonxt.com/_next/data/8L0k5Obx_zXhq4cp-uJC7/movies"
        id = "movieId"

    url = f"{base}/{slug}.json"

    params = {
        id: slug
    }

    headers = {
        "Accept": "*/*",
        "Referer": "https://aaonxt.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "x-nextjs-data": "1"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
    )

    data = response.json()
    try:
        page = data.get("pageProps", {})

        movie = page.get("MovieData") or page.get("seriesData")

        if not movie:
            print("❌ No data found")
            return None

        result = {
            "title": f"{movie.get('title')} - ({movie.get('year') or str(movie.get("releaseDate", ""))[:4]})",
            "landscape": fix_image(movie.get("tvBannerImage")),
            "portrait": fix_image(movie.get("cardImage")),
            "banner": fix_image(movie.get("detailImage")),
        }

        return result

    except Exception as e:
        print("error:", e)
        return None

@router.get("/aaonxt")
def aaonxt_poster(url: str = Query(..., description="AAONXT content URL")):
    result = fetch_aaonxt(url)

    if not result:
        return JSONResponse(content={"error": "Failed to fetch data from AAONXT"}, status_code=400)

    return JSONResponse(content=result, status_code=200)
