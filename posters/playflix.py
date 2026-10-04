import html as html_parser
import re
from urllib.parse import urlparse

from curl_cffi import requests
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"


def clean_text(value):
    """Decode HTML entities and remove markup/extra whitespace."""
    value = html_parser.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_attr(tag, name):
    match = re.search(
        rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1",
        tag,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    value = html_parser.unescape(match.group(2))
    return re.sub(r"\s+", "", value) if name.lower() == "src" else value.strip()


def extract_first(pattern, html_text, flags=re.IGNORECASE | re.DOTALL):
    match = re.search(pattern, html_text, flags)
    return clean_text(match.group(1)) if match else None


def extract_content_id(url):
    """Extract the base64-like content id from /content/<id>."""
    match = re.search(r"/content/([^/?#]+)/?", url, re.IGNORECASE)
    return match.group(1) if match else None


def extract_poster_images(html_text):
    """Extract the page's primary portrait and landscape poster URLs."""
    portrait = None
    landscape = None

    for tag in re.findall(r"<img\b[^>]*>", html_text, re.IGNORECASE | re.DOTALL):
        src = extract_attr(tag, "src")
        if not src or not re.match(r"https?://", src, re.IGNORECASE):
            continue

        classes = (extract_attr(tag, "class") or "").lower()
        if "horizontal-poster" in classes or "horizontal-thumbnail" in classes:
            landscape = landscape or src
        elif not portrait and re.search(r"(?:_333|portrait|vertical)[^/]*\.jpg(?:[?#]|$)", src, re.IGNORECASE):
            portrait = src

    if not portrait:
        match = re.search(
            r"https?://[^\s\"']+_333\.jpg(?:[?#][^\s\"']*)?",
            html_text,
            re.IGNORECASE,
        )
        portrait = match.group(0) if match else None

    if not landscape:
        match = re.search(
            r"https?://[^\s\"']+_(?:1280|1080)\.jpg(?:[?#][^\s\"']*)?",
            html_text,
            re.IGNORECASE,
        )
        landscape = match.group(0) if match else None

    if landscape and not portrait:
        portrait = re.sub(r"_(?:1280|1080)(\.jpg(?:[?#].*)?)$", r"_333\1", landscape, flags=re.IGNORECASE)
    if portrait and not landscape:
        landscape = re.sub(r"_333(\.jpg(?:[?#].*)?)$", r"_1280\1", portrait, flags=re.IGNORECASE)

    return portrait, landscape


def extract_labeled_value(label, html_text):
    pattern = rf"<b[^>]*>\s*{re.escape(label)}\s*:\s*</b>\s*(.*?)\s*</p>"
    return extract_first(pattern, html_text)


def playflix(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"error": "Invalid Playflix URL"}

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=20,
        )
    except Exception as exc:
        return {"error": f"Failed to fetch Playflix page: {exc}"}

    if response.status_code != 200:
        return {"error": f"Playflix returned HTTP {response.status_code}"}

    html_text = response.text
    title = extract_first(r"<h4\b[^>]*>\s*(.*?)\s*</h4>", html_text)
    description = extract_first(
        r"<span\b[^>]*id\s*=\s*['\"]long-content['\"][^>]*>(.*?)</span>",
        html_text,
    )
    portrait, landscape = extract_poster_images(html_text)

    result = {
        "title": title,
        "description": description,
        "landscape": landscape,
        "portrait": portrait,
        "content_id": extract_content_id(url),
    }

    for label, key in (("Cast", "cast"), ("Director", "director"), ("Genre", "genre")):
        value = extract_labeled_value(label, html_text)
        if value:
            result[key] = value

    if not title and not landscape and not portrait:
        return {"error": "Playflix metadata not found"}

    return result


@router.get("/playflix")
def playflix_poster(
    url: str = Query(..., description="Playflix content URL")
):
    result = playflix(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result, status_code=200)
