import re
import html

from curl_cffi import requests
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()


def extract_video_id(url: str):
    match = re.search(r"dailymotion\.com/video/([A-Za-z0-9]+)", url)

    if match:
        return match.group(1)

    return None


def extract_title(html_text: str):
    match = re.search(
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
        html_text,
        re.IGNORECASE
    )

    if match:
        return html.unescape(match.group(1)).strip()

    return None


def dailymotion(url: str):
    video_id = extract_video_id(url)

    if not video_id:
        return {"error": "Invalid Dailymotion URL"}

    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )

        title = extract_title(r.text) if r.status_code == 200 else None

    except Exception:
        title = None

    return {
        "title": title,
        "landscape": f"https://www.dailymotion.com/thumbnail/video/{video_id}",
        "video_id": video_id
    }


@router.get("/dailymotion")
def dailymotion_poster(
    url: str = Query(..., description="Dailymotion video URL")
):
    result = dailymotion(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
