from curl_cffi import requests
import re
import html
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def extract_title(html_text):
    title_match = re.search(
        r'<title[^>]*>(.*?)</title>',
        html_text,
        re.IGNORECASE | re.DOTALL
    )

    text = title_match.group(1).strip() if title_match else "Unknown Title"

    match = re.search(r'Watch\s+(.*?)\s+Streaming', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return text


def extract_ldjson_image(html_text):
    ldjson_match = re.search(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>\s*({[\s\S]*?})\s*</script>',
        html_text,
        re.IGNORECASE
    )

    if not ldjson_match:
        return None

    try:
        json_data = json.loads(ldjson_match.group(1))
        image_url = json_data.get("image")
        if not image_url:
            return None

        clean_url = re.split(r'&region=.*', image_url)[0]
        return clean_url + "&region=US&format=jpeg&size=3840x2160"

    except Exception:
        return None


def extract_first_src_from_picture(html_text, class_name):
    pattern = rf'<picture[^>]*class=["\']{class_name}["\'][\s\S]*?</picture>'
    match = re.search(pattern, html_text, re.IGNORECASE)
    if not match:
        return None

    picture_html = match.group()

    srcset_match = re.search(r'srcset=["\']([^"\']+)["\']', picture_html, re.IGNORECASE)
    if srcset_match:
        return srcset_match.group(1).split(',')[0].strip().split(' ')[0]

    src_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', picture_html, re.IGNORECASE)
    if src_match:
        return src_match.group(1)

    return None


def transform_url(original_url):
    if not original_url:
        return None
    clean_url = re.split(r'&size=.*', original_url)[0]
    return clean_url + "&region=US&format=jpeg&size=3840x2160"


def scrape_hulu_images(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {"error": "Failed to fetch page"}

    html_text = html.unescape(res.text)
    title = extract_title(html_text)
    image_url = extract_ldjson_image(html_text)
    background_url = extract_first_src_from_picture(
        html_text, "DetailEntityBackground__picture"
    )
    title_url = extract_first_src_from_picture(
        html_text, "DetailEntityMasthead__title-art__image"
    )

    final_background = transform_url(background_url)
    final_title = transform_url(title_url)

    return {
        "title":title,
        "landscape": image_url,
        "cover": final_background,
        "logo": final_title
    }


@router.get("/hulu")
def hulu_poster(url: str = Query(..., description="Hulu content URL")):
    result = scrape_hulu_images(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
