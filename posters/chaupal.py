from curl_cffi import requests
import re
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def clean_chaupal_image_url(url: str) -> str:
    return re.sub(r'(/chaupal)/\d+/\d+/', r'\1/', url)


def chaupal(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html"
    }

    html = requests.get(url, headers=headers).text

    scripts = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.S | re.I
    )

    for raw_json in scripts:
        try:
            data = json.loads(raw_json.strip())

            return {
                "title": f"{data['name']} - ({data.get('releaseYear')})",
                "portrait": clean_chaupal_image_url(data["thumbnailUrl"]),
                "landscape": clean_chaupal_image_url(data["image"]),
                "type": data.get("@type")
            }

        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    return {}

@router.get("/chaupal")
def chaupal_poster(
    url: str = Query(..., description="Chaupal content URL")
):
    result = chaupal(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
