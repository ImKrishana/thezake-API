import re
from curl_cffi import requests
import html
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_yt_video_id(url: str):
    """
    Works for:
    - watch?v=
    - youtu.be/
    - /embed/
    - URLs with extra params (&list=, &index=, etc.)
    """
    patterns = [
        r"v=([0-9A-Za-z_-]{11})",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"/embed/([0-9A-Za-z_-]{11})"
    ]

    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)

    return None


def extract_yt_title(html_text: str):
    match = re.search(
        r"<title>(.*?)</title>",
        html_text,
        re.IGNORECASE | re.DOTALL
    )
    if match:
        title = html.unescape(match.group(1))
        return title.replace("- YouTube", "").strip()
    return None


def get_maxres_thumbnail(video_id: str):
    return f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"


def youtube(url: str):
    video_id = extract_yt_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return {"error": "Failed to fetch YouTube page"}

    title = extract_yt_title(r.text)
    thumbnail = get_maxres_thumbnail(video_id)

    return {
        "title": title,
        "landscape": thumbnail,
        "video_id": video_id
    }


@router.get("/youtube")
def youtube_posters(url: str = Query(..., description="YouTube video URL")):
    result = youtube(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
