from curl_cffi import requests
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def aha(url):
    path = url.split("www.aha.video")[-1]
    api = (
        "https://api-aha-cdn.api.ahacms.firstlight.ai/content/"
        f"urn/resource/catalog/{path}"
        "?reg=in&acl=te&dt=web&ipr=true&itvod=true"
    )

    response = requests.get(
        api,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        },
        timeout=20
    )

    data = response.json()["data"]

    locd = data.get("lon", [{}])[1]
    title = locd.get("n", "Unknown Title")
    year = data.get("r", "Unknown Year")

    content_id = data.get("id")

    landscape = (
        f"https://image-resizer-cloud-api-ahacms.akamaized.net/"
        f"image/{content_id}/0-16x9.jpg?width=4000"
    )

    portrait = landscape.replace("16x9", "2x3")

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape,
        "portrait": portrait
    }

@router.get("/aha")
def aha_poster(
    url: str = Query(..., description="aha content URL")
):
    result = aha(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
