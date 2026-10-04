from curl_cffi import requests
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def fetch_mubi_data(film):
    url = f"https://api.mubi.com/v4/films/{film}"

    headers = {
        "Accept": "*/*",
        "accept-language": "en",
        "ANONYMOUS_USER_ID": "96150c41-71c0-4cf9-a726-70841610a8e6",
        "CLIENT": "web",
        "Client-Country": "IN",
        "Origin": "https://mubi.com",
        "Referer": "https://mubi.com/",
        "User-Agent": "Mozilla/5.0"
    }

    req = requests.get(url, headers=headers)
    data = req.json()
    return data


def extract_mubi_details(data):
    title = data.get("title", "N/A")
    year = data.get("year", "N/A")

    landscape = None
    portrait = None
    cover = None
    logo = None

    artworks = data.get("artworks", [])

    for art in artworks:
        fmt = art.get("format")
        url = art.get("image_url")

        if fmt == "cover_artwork_horizontal":
            landscape = url
        elif fmt == "cover_artwork_vertical":
            portrait = url
        elif fmt == "tile_artwork":
            cover = url
        elif fmt == "content_logo_monochromatic" or fmt == "content_logo_polychromatic":
            logo = url

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape,
        "portrait": portrait,
        "cover": cover,
        "logo": logo
    }

@router.get("/mubi")
def mubi(url: str = Query(..., description="MUBI FILM URL")):
    try:
        film = url.split("/")[-1]
        data = fetch_mubi_data(film)
        details = extract_mubi_details(data)
        return JSONResponse(content=details, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
